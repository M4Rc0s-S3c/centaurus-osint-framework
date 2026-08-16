"""End-to-end validation of the complete CENTAURUS MVP flow."""

from datetime import datetime, timezone
import json
import sys
from types import SimpleNamespace

from centaurus.cli import CLI
from centaurus.core.core import Core
from centaurus.investigation import InvestigationStatus
from centaurus.llm.llm_manager import LLMManager
from centaurus.llm.request_interpreter import RequestInterpreter
from centaurus.persistence.filesystem import (
    FilesystemEvidenceStore,
    FilesystemFindingStore,
    FilesystemRawObservationStore,
    FilesystemReportStore,
)
from centaurus.request import PUBLIC_EXPOSURE_ASSESSMENT
from centaurus.rules.whois_rules import WHOIS_RULES


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
        return "WHOIS findings presented for the analyst."


def test_complete_mvp_flow_from_cli_to_persisted_report_and_llm_presentation(
    tmp_path,
    monkeypatch,
) -> None:
    """Exercise the complete deterministic pipeline with only external I/O stubbed."""

    whois_result = {
        "domain_name": "EXAMPLE.COM",
        "registrar": None,
        "name_servers": None,
        "creation_date": datetime(2020, 1, 1, tzinfo=timezone.utc),
        "expiration_date": datetime(2030, 1, 1, tzinfo=timezone.utc),
        "dnssec": "unsigned",
        "registrant_name": None,
    }

    # Keep the real PluginManager -> WhoisPlugin path while replacing only
    # the external python-whois/network boundary with deterministic data.
    monkeypatch.setitem(
        sys.modules,
        "whois",
        SimpleNamespace(whois=lambda domain: whois_result),
    )
    from centaurus.plugins.whois import plugin as whois_plugin

    monkeypatch.setattr(
        whois_plugin.whois,
        "whois",
        lambda domain: whois_result,
    )

    report_provider = CapturingReportProvider()
    core = Core(
        raw_observation_store=FilesystemRawObservationStore(tmp_path),
        evidence_store=FilesystemEvidenceStore(tmp_path),
        finding_store=FilesystemFindingStore(tmp_path),
        report_store=FilesystemReportStore(tmp_path),
        llm_manager=LLMManager(provider=report_provider),
        rules=WHOIS_RULES,
    )
    interpreter = RequestInterpreter(provider=FixedIntentProvider())
    cli = CLI(core=core, request_interpreter=interpreter)

    investigation = cli.submit("Analiza la exposición pública de example.com")

    assert investigation.status is InvestigationStatus.COMPLETED
    assert investigation.target == "example.com"
    assert investigation.target_type == "DOMAIN"
    assert investigation.intent == PUBLIC_EXPOSURE_ASSESSMENT

    assert len(investigation.results) == 1
    assert len(investigation.evidences) == 1
    assert {finding.rule.id for finding in investigation.findings} == {
        "RL-001",
        "RL-002",
        "RL-004",
        "RL-005",
    }

    assert investigation.report is not None
    assert investigation.report.findings == investigation.findings
    assert report_provider.reports == [investigation.report]
    assert core.last_llm_output == "WHOIS findings presented for the analyst."

    root = tmp_path / "investigations" / investigation.id
    raw_files = list((root / "evidences" / "raw").glob("*.json"))
    evidence_files = list((root / "evidences" / "normalized").glob("*.json"))
    finding_files = list((root / "findings").glob("*.json"))
    report_files = list((root / "reports").glob("*.json"))

    assert len(raw_files) == 1
    assert len(evidence_files) == 1
    assert len(finding_files) == 4
    assert len(report_files) == 1

    persisted_report = json.loads(report_files[0].read_text(encoding="utf-8"))
    assert persisted_report["investigation_id"] == investigation.id
    assert {item["rule"]["id"] for item in persisted_report["findings"]} == {
        "RL-001",
        "RL-002",
        "RL-004",
        "RL-005",
    }
