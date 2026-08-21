"""End-to-end validation of the complete CENTAURUS MVP flow."""

from collections import Counter
from datetime import datetime, timezone
import json
import sys
from types import SimpleNamespace

from centaurus.cli import CLI
from centaurus.core.core import Core
from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.investigation import InvestigationStatus
from centaurus.llm.llm_manager import LLMManager
from centaurus.llm.request_interpreter import RequestInterpreter
from centaurus.persistence.filesystem import (
    FilesystemEvidenceStore,
    FilesystemExecutionFailureStore,
    FilesystemFindingStore,
    FilesystemRawObservationStore,
    FilesystemReportStore,
)
from centaurus.exceptions import PluginExecutionError
from centaurus.plugin_manager.plugin_manager import PluginManager
from centaurus.request import PUBLIC_EXPOSURE_ASSESSMENT
from centaurus.rules.dns_rules import DNS_RULES
from centaurus.rules.exposure_rules import EXPOSURE_RULES
from centaurus.rules.registration_rules import REGISTRATION_RULES


class FixedIntentProvider:
    """Deterministic test double for the external LLM #1 boundary."""

    def classify_intent(self, user_input: str) -> str:
        return PUBLIC_EXPOSURE_ASSESSMENT


class CapturingReportProvider:
    """Test double for LLM #2 that preserves the Report boundary."""

    def __init__(self) -> None:
        self.reports = []

    def generate(self, report) -> str:
        self.reports.append(report)
        return "Registration findings presented for the analyst."


def test_complete_catalog_multitool_flow_from_cli_to_persisted_report_and_llm_presentation(
    tmp_path,
    monkeypatch,
) -> None:
    """Validate the six-tool catalog plus direct DMARC acquisition end to end."""

    whois_result = {
        "domain_name": "EXAMPLE.COM",
        "registrar": None,
        "name_servers": None,
        "creation_date": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "expiration_date": datetime(2030, 1, 1, tzinfo=timezone.utc),
        "dnssec": "unsigned",
        "registrant_name": None,
    }

    rdap_result = {
        "objectClassName": "domain",
        "handle": "EXAMPLE-1",
        "ldhName": "example.com",
        "status": ["active"],
        "events": [
            {"eventAction": "registration", "eventDate": "1995-08-14T04:00:00Z"},
            {"eventAction": "expiration", "eventDate": "2030-08-14T04:00:00Z"},
        ],
        "nameservers": [
            {"ldhName": "ns1.example.com"},
            {"ldhName": "ns2.example.com"},
        ],
        "entities": [
            {
                "roles": ["registrar"],
                "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrar"]]],
            },
            {
                "roles": ["registrant"],
                "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrant"]]],
            },
        ],
    }

    dnsrecon_result = [
        {"type": "ScanInfo", "arguments": "dnsrecon -d example.com -t std", "date": "2026-08-16"},
        {
            "domain": "example.com",
            "type": "A",
            "name": "example.com",
            "address": "192.0.2.10",
        },
    ]

    dmarc_dnsrecon_result = [
        {
            "type": "ScanInfo",
            "arguments": "dnsrecon -d _dmarc.example.com -t std",
            "date": "2026-08-18",
        },
    ]

    crtsh_result = [
        {
            "issuer_ca_id": 123,
            "issuer_name": "Example CA",
            "common_name": "www.example.com",
            "name_value": "www.example.com\napi.example.com",
            "id": 456,
            "entry_timestamp": "2026-08-16T10:00:00",
            "not_before": "2026-08-16T09:00:00",
            "not_after": "2026-11-14T09:00:00",
            "serial_number": "01AB",
        }
    ]

    theharvester_result = {
        "cmd": "theHarvester -d example.com ...",
        "hosts": ["mail.example.com", "www.example.com"],
        "emails": ["admin@example.com", "security@example.com"],
        "ips": ["192.0.2.20"],
        "interesting_urls": ["https://mail.example.com/login"],
        "asns": ["AS64500"],
        "shodan": [],
    }

    # Keep the real PluginManager -> WhoisPlugin path while replacing only
    # the external python-whois/network boundary with deterministic data.
    monkeypatch.setitem(
        sys.modules,
        "whois",
        SimpleNamespace(whois=lambda domain, **kwargs: whois_result),
    )
    from centaurus.plugins.whois import plugin as whois_plugin

    monkeypatch.setattr(
        whois_plugin.whois,
        "whois",
        lambda domain, **kwargs: whois_result,
    )

    from centaurus.plugins.crtsh import plugin as crtsh_plugin
    from centaurus.plugins.rdap import plugin as rdap_plugin

    class FakeRdapResponse:
        def __init__(self, data):
            self._data = data

        def raise_for_status(self):
            return None

        def json(self):
            return self._data

    def fake_http_get(url: str, **kwargs):
        if url == "https://data.iana.org/rdap/dns.json":
            return FakeRdapResponse({
                "services": [
                    [["com"], ["https://rdap.example/registry/"]],
                ]
            })
        if url == "https://rdap.example/registry/domain/example.com":
            return FakeRdapResponse(rdap_result)
        if url == "https://crt.sh/":
            assert kwargs["params"] == {
                "q": "%.example.com",
                "output": "json",
            }
            return FakeRdapResponse(crtsh_result)
        raise AssertionError(f"Unexpected HTTP request: {url}")

    monkeypatch.setattr(rdap_plugin.httpx, "get", fake_http_get)
    assert crtsh_plugin.httpx.get is fake_http_get

    from centaurus.plugins.dnsrecon import plugin as dnsrecon_plugin

    from centaurus.plugins.sublist3r import plugin as sublist3r_plugin
    from centaurus.plugins.theharvester import plugin as theharvester_plugin

    def fake_tool_run(command, **kwargs):
        if command[0] == "dnsrecon":
            query_name = command[command.index("-d") + 1]
            output_path = command[command.index("-j") + 1]
            records = (
                dmarc_dnsrecon_result
                if query_name == "_dmarc.example.com"
                else dnsrecon_result
            )
            with open(output_path, "w", encoding="utf-8") as output:
                json.dump(records, output)
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        if command[0] == "sublist3r":
            output_path = command[command.index("-o") + 1]
            with open(output_path, "w", encoding="utf-8") as output:
                output.write("www.example.com\n")
                output.write("api.example.com\n")
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        if command[0] == "theHarvester":
            report_base = command[command.index("-f") + 1]
            with open(f"{report_base}.json", "w", encoding="utf-8") as output:
                json.dump(theharvester_result, output)
            return SimpleNamespace(returncode=0, stdout="", stderr="")

        raise AssertionError(f"Unexpected external command: {command[0]}")

    monkeypatch.setattr(dnsrecon_plugin.subprocess, "run", fake_tool_run)
    assert sublist3r_plugin.subprocess.run is fake_tool_run
    assert theharvester_plugin.subprocess.run is fake_tool_run

    report_provider = CapturingReportProvider()
    core = Core(
        raw_observation_store=FilesystemRawObservationStore(tmp_path),
        evidence_store=FilesystemEvidenceStore(tmp_path),
        finding_store=FilesystemFindingStore(tmp_path),
        report_store=FilesystemReportStore(tmp_path),
        llm_manager=LLMManager(provider=report_provider),
        rules=REGISTRATION_RULES + DNS_RULES + EXPOSURE_RULES,
    )
    interpreter = RequestInterpreter(provider=FixedIntentProvider())
    cli = CLI(core=core, request_interpreter=interpreter)

    investigation = cli.submit("Analiza la exposición pública de example.com")

    assert investigation.status is InvestigationStatus.COMPLETED
    assert investigation.target == "example.com"
    assert investigation.target_type == "DOMAIN"
    assert investigation.intent == PUBLIC_EXPOSURE_ASSESSMENT

    expected_sources = [
        EvidenceSource.WHOIS,
        EvidenceSource.RDAP,
        EvidenceSource.DNSRECON,
        EvidenceSource.DNSRECON,
        EvidenceSource.SUBLIST3R,
        EvidenceSource.CRTSH,
        EvidenceSource.THEHARVESTER,
    ]

    # The six-tool DOMAIN catalog now contains seven sequential tasks because
    # DNSRecon is reused for one explicit direct-DMARC observation. Every task
    # must cross both RawObservation and normalized Evidence boundaries.
    assert len(investigation.evidences) == 7
    assert [evidence.source for evidence in investigation.evidences] == expected_sources

    whois_evidence = investigation.evidences[0].data
    rdap_evidence = investigation.evidences[1].data
    standard_dns_evidence = investigation.evidences[2].data
    dmarc_dns_evidence = investigation.evidences[3].data
    sublist3r_evidence = investigation.evidences[4].data
    crtsh_evidence = investigation.evidences[5].data
    theharvester_evidence = investigation.evidences[6].data

    assert whois_evidence["registrar"] is None
    assert whois_evidence["creation_date"] == "2020-01-01T00:00:00+00:00"
    assert rdap_evidence["domain_name"] == "example.com"
    assert rdap_evidence["registrar"] == "Example Registrar"
    assert standard_dns_evidence["a_records"] == ["192.0.2.10"]
    assert standard_dns_evidence["spf_records"] == []
    assert dmarc_dns_evidence["domain_name"] == "example.com"
    assert dmarc_dns_evidence["query_name"] == "_dmarc.example.com"
    assert dmarc_dns_evidence["dmarc_records"] == []
    assert "spf_records" not in dmarc_dns_evidence
    assert sublist3r_evidence["subdomains"] == [
        "api.example.com",
        "www.example.com",
    ]
    assert crtsh_evidence["certificate_names"] == [
        "api.example.com",
        "www.example.com",
    ]
    assert theharvester_evidence["hosts"] == [
        "mail.example.com",
        "www.example.com",
    ]
    assert theharvester_evidence["emails"] == [
        "admin@example.com",
        "security@example.com",
    ]
    assert theharvester_evidence["subdomains"] == [
        "mail.example.com",
        "www.example.com",
    ]

    # Registral Evidence keeps producing the existing Findings. Standard and
    # direct-DMARC DNS Evidence produce isolated factual mail-policy Findings,
    # while collection Rules remain tool-agnostic across compatible sources.
    finding_counts = Counter(finding.rule.id for finding in investigation.findings)
    assert finding_counts == Counter(
        {
            "RL-001": 1,
            "RL-002": 1,
            "RL-004": 1,
            "RL-005": 1,
            "RL-007": 1,
            "RL-008": 3,
            "RL-009": 1,
            "RL-010": 1,
            "RL-014": 2,
        }
    )

    corroboration_findings = [
        finding
        for finding in investigation.findings
        if finding.rule.id == "RL-014"
    ]
    assert [finding.conclusion for finding in corroboration_findings] == [
        "Subdomain api.example.com was observed in at least two distinct "
        "normalized Evidence sources.",
        "Subdomain www.example.com was observed in at least two distinct "
        "normalized Evidence sources.",
    ]
    assert [
        [evidence.source for evidence in finding.evidences]
        for finding in corroboration_findings
    ] == [
        [EvidenceSource.SUBLIST3R, EvidenceSource.CRTSH],
        [
            EvidenceSource.SUBLIST3R,
            EvidenceSource.CRTSH,
            EvidenceSource.THEHARVESTER,
        ],
    ]

    assert investigation.report is not None
    assert investigation.report.findings == investigation.findings
    assert investigation.report.target == "example.com"
    assert investigation.report.target_type == "DOMAIN"
    assert investigation.report.intent == PUBLIC_EXPOSURE_ASSESSMENT
    assert (
        investigation.report.analyst_question
        == "Analiza la exposición pública de example.com"
    )
    assert investigation.report.generated_at.tzinfo is not None
    assert report_provider.reports == [investigation.report]
    assert core.last_llm_output == "Registration findings presented for the analyst."

    root = tmp_path / "investigations" / investigation.id
    raw_files = sorted((root / "evidences" / "raw").glob("*.json"))
    evidence_files = sorted((root / "evidences" / "normalized").glob("*.json"))
    finding_files = sorted((root / "findings").glob("*.json"))
    report_files = sorted((root / "reports").glob("*.json"))
    markdown_files = sorted((root / "reports").glob("*.md"))

    assert len(raw_files) == 7
    assert len(evidence_files) == 7
    assert len(finding_files) == 12
    assert len(report_files) == 1
    assert len(markdown_files) == 1

    persisted_report = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert persisted_report["target"] == "example.com"
    assert persisted_report["target_type"] == "DOMAIN"
    assert persisted_report["intent"] == PUBLIC_EXPOSURE_ASSESSMENT
    assert (
        persisted_report["analyst_question"]
        == "Analiza la exposición pública de example.com"
    )
    assert persisted_report["generated_at"].endswith("+00:00")
    assert persisted_report["findings"][10]["finding_ref"] == "F-011"
    assert persisted_report["findings"][11]["finding_ref"] == "F-012"

    markdown_report = markdown_files[0].read_text(encoding="utf-8")
    assert markdown_report.startswith("# CENTAURUS OSINT Investigation Report\n")
    assert "**Target:** `DOMAIN:example.com`" in markdown_report
    assert "**Intent:** `public_exposure_assessment`" in markdown_report
    assert "> Analiza la exposición pública de example.com" in markdown_report
    assert "**Authoritative artifact:** `report.json`" in markdown_report
    assert "### F-011 — `RL-014`" in markdown_report
    assert "### F-012 — `RL-014`" in markdown_report
    assert "`sublist3r`" in markdown_report
    assert "`crtsh`" in markdown_report
    assert "`theharvester`" in markdown_report
    assert "Registration findings presented for the analyst." not in markdown_report

    # Filesystem persistence must preserve the seven-task execution order,
    # including the second DNSRecon observation, at RAW and normalized levels.
    persisted_raw_sources = [
        json.loads(path.read_text(encoding="utf-8"))["source"]
        for path in raw_files
    ]
    persisted_evidence_sources = [
        json.loads(path.read_text(encoding="utf-8"))["source"]
        for path in evidence_files
    ]
    expected_source_values = [source.value for source in expected_sources]
    assert persisted_raw_sources == expected_source_values
    assert persisted_evidence_sources == expected_source_values

    persisted_dmarc_raw = json.loads(raw_files[3].read_text(encoding="utf-8"))
    persisted_dmarc_evidence = json.loads(
        evidence_files[3].read_text(encoding="utf-8")
    )
    assert persisted_dmarc_raw["data"]["scan_kind"] == "dmarc"
    assert persisted_dmarc_raw["data"]["query_name"] == "_dmarc.example.com"
    assert persisted_dmarc_evidence["data"]["dmarc_records"] == []

    persisted_correlation_findings = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in finding_files
        if path.name.endswith("-RL-014.json")
    ]
    assert len(persisted_correlation_findings) == 2
    assert [
        [evidence["source"] for evidence in item["evidences"]]
        for item in persisted_correlation_findings
    ] == [
        ["sublist3r", "crtsh"],
        ["sublist3r", "crtsh", "theharvester"],
    ]

    persisted_report = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert persisted_report["investigation_id"] == investigation.id
    persisted_finding_counts = Counter(
        item["rule"]["id"]
        for item in persisted_report["findings"]
    )
    assert persisted_finding_counts == finding_counts


def test_multitool_flow_continues_after_one_tool_failure_without_creating_failure_knowledge(
    tmp_path,
    monkeypatch,
) -> None:
    """G6: one isolated tool failure yields a partial execution and valid Report."""

    source_by_plugin = {
        "whois": EvidenceSource.WHOIS,
        "rdap": EvidenceSource.RDAP,
        "dnsrecon": EvidenceSource.DNSRECON,
        "sublist3r": EvidenceSource.SUBLIST3R,
        "crtsh": EvidenceSource.CRTSH,
        "theharvester": EvidenceSource.THEHARVESTER,
    }

    def fake_execute(self, task):
        if task.plugin_id == "crtsh":
            try:
                raise TimeoutError("crt.sh timed out")
            except TimeoutError as exc:
                raise PluginExecutionError("crtsh", str(exc)) from exc

        return RawObservation(
            source=source_by_plugin[task.plugin_id],
            data={},
            collected_at=datetime(2026, 8, 18, 9, 0, tzinfo=timezone.utc),
        )

    monkeypatch.setattr(PluginManager, "execute", fake_execute)

    report_provider = CapturingReportProvider()
    core = Core(
        raw_observation_store=FilesystemRawObservationStore(tmp_path),
        evidence_store=FilesystemEvidenceStore(tmp_path),
        finding_store=FilesystemFindingStore(tmp_path),
        report_store=FilesystemReportStore(tmp_path),
        execution_failure_store=FilesystemExecutionFailureStore(tmp_path),
        llm_manager=LLMManager(provider=report_provider),
        rules=(),
    )

    from centaurus.investigation import Investigation

    investigation = Investigation(target="example.com", intent="public_exposure_assessment")
    result = core.run_investigation(investigation)

    assert result["status"] == "partial"
    assert len(result["results"]) == 6
    assert len(result["failures"]) == 1
    assert result["failures"][0].plugin_id == "crtsh"
    assert result["failures"][0].category.value == "timeout"

    assert investigation.status is InvestigationStatus.COMPLETED
    assert len(investigation.evidences) == 6
    assert investigation.findings == ()
    assert investigation.report is not None
    assert report_provider.reports == [investigation.report]

    root = tmp_path / "investigations" / investigation.id
    assert len(list((root / "evidences" / "raw").glob("*.json"))) == 6
    assert len(list((root / "evidences" / "normalized").glob("*.json"))) == 6
    assert len(list((root / "execution" / "failures").glob("*.json"))) == 1
    assert len(list((root / "findings").glob("*.json"))) == 0
    assert len(list((root / "reports").glob("*.json"))) == 1
    assert len(list((root / "reports").glob("*.md"))) == 1
    markdown_report = next((root / "reports").glob("*.md")).read_text(
        encoding="utf-8"
    )
    assert "**Findings:** 0" in markdown_report
    assert "No Findings were produced." in markdown_report

    persisted_failure = json.loads(
        next((root / "execution" / "failures").glob("*.json")).read_text(
            encoding="utf-8"
        )
    )
    assert persisted_failure["plugin_id"] == "crtsh"
    assert persisted_failure["category"] == "timeout"
    assert persisted_failure["task_index"] == 6
