"""Tests for normalized Evidence and Report filesystem persistence."""

import json
from datetime import datetime, timezone

import pytest

from centaurus.evidence import Evidence, EvidenceSource
from centaurus.finding import Finding
from centaurus.investigation import Investigation
from centaurus.report import Report
from centaurus.rules.condition import Condition
from centaurus.rules.rule import Rule
from centaurus.persistence import EvidenceStore, FindingStore, ReportStore
from centaurus.persistence.filesystem import FilesystemEvidenceStore, FilesystemFindingStore, FilesystemReportStore


def make_evidence() -> Evidence:
    return Evidence(
        source=EvidenceSource.WHOIS,
        data={"domain_name": "example.org", "registrar": "Example Registrar"},
        collected_at=datetime(2026, 8, 15, 12, 0, tzinfo=timezone.utc),
    )


def make_finding(evidence: Evidence) -> Finding:
    rule = Rule(
        id="RL-TEST-001",
        version="1.0",
        name="test_rule",
        description="Test rule.",
        category="registration",
        conditions=(Condition(field="registrar", operator="missing"),),
        conclusion="Registrar information is missing.",
    )
    return Finding(
        conclusion=rule.conclusion,
        rule=rule,
        evidences=(evidence,),
    )


def make_report(
    investigation: Investigation,
    findings: tuple[Finding, ...] = (),
    *,
    analyst_question: str | None = None,
) -> Report:
    return Report(
        investigation_id=investigation.id,
        generated_at=datetime(2026, 8, 20, 12, 30, tzinfo=timezone.utc),
        target=investigation.target,
        target_type=investigation.target_type,
        intent=investigation.intent,
        findings=findings,
        analyst_question=analyst_question,
    )


def test_evidence_store_defines_contract() -> None:
    assert hasattr(EvidenceStore, "persist_evidence")
    assert hasattr(FilesystemEvidenceStore, "persist_evidence")


def test_evidence_store_persists_normalized_evidence(tmp_path) -> None:
    path = FilesystemEvidenceStore(tmp_path).persist_evidence("INV-001", make_evidence())
    assert path.name == "INV-001_0001-whois.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["source"] == "whois"
    assert payload["data"]["domain_name"] == "example.org"


def test_evidence_store_is_append_only(tmp_path) -> None:
    store = FilesystemEvidenceStore(tmp_path)
    first = store.persist_evidence("INV-001", make_evidence())
    second = store.persist_evidence("INV-001", make_evidence())
    assert first.name == "INV-001_0001-whois.json"
    assert second.name == "INV-001_0002-whois.json"


def test_report_store_defines_contract() -> None:
    assert hasattr(ReportStore, "persist_report")
    assert hasattr(FilesystemReportStore, "persist_report")


def test_report_store_persists_report_and_findings(tmp_path) -> None:
    evidence = make_evidence()
    finding = make_finding(evidence)
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    investigation.add_finding(finding)
    report = make_report(
        investigation,
        (finding,),
        analyst_question="Investiga la exposición pública de example.org",
    )

    path = FilesystemReportStore(tmp_path).persist_report(investigation.id, report)
    reports_dir = tmp_path / "investigations" / investigation.id / "reports"
    markdown_path = reports_dir / "report.md"

    assert path == reports_dir / "report.json"
    assert markdown_path.is_file()

    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["investigation_id"] == investigation.id
    assert payload["generated_at"] == "2026-08-20T12:30:00+00:00"
    assert payload["target"] == "example.org"
    assert payload["target_type"] == "DOMAIN"
    assert payload["intent"] == "public_exposure_assessment"
    assert payload["analyst_question"] == "Investiga la exposición pública de example.org"
    assert payload["findings"][0]["finding_ref"] == "F-001"
    assert payload["findings"][0]["rule"]["id"] == "RL-TEST-001"
    assert payload["findings"][0]["evidences"][0]["data"]["domain_name"] == "example.org"

    markdown = markdown_path.read_text(encoding="utf-8")
    assert markdown.startswith("# CENTAURUS OSINT Investigation Report\n")
    assert "**Report generated:** `2026-08-20T12:30:00Z`" in markdown
    assert "**Target:** `DOMAIN:example.org`" in markdown
    assert "**Intent:** `public_exposure_assessment`" in markdown
    assert "> Investiga la exposición pública de example.org" in markdown
    assert "**Authoritative artifact:** `report.json`" in markdown
    assert "### F-001 — `RL-TEST-001` · `test_rule`" in markdown
    assert "Registrar information is missing." in markdown
    assert "##### Evidence 1 — `whois`" in markdown
    assert '    "domain_name": "example.org"' in markdown


def test_report_store_rejects_second_report(tmp_path) -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    report = make_report(investigation)
    store = FilesystemReportStore(tmp_path)
    store.persist_report(investigation.id, report)
    with pytest.raises(FileExistsError):
        store.persist_report(investigation.id, report)


def test_report_store_rejects_orphan_markdown_artifact(tmp_path) -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    report = make_report(investigation)
    reports_dir = tmp_path / "investigations" / investigation.id / "reports"
    reports_dir.mkdir(parents=True)
    (reports_dir / "report.md").write_text("orphan", encoding="utf-8")

    with pytest.raises(FileExistsError):
        FilesystemReportStore(tmp_path).persist_report(investigation.id, report)


def test_report_store_rolls_back_json_if_markdown_write_fails(tmp_path, monkeypatch) -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    report = make_report(investigation)
    store = FilesystemReportStore(tmp_path)
    original = FilesystemReportStore._persist_exclusive
    calls = 0

    def fail_second_write(destination, encoded):
        nonlocal calls
        calls += 1
        if calls == 2:
            raise OSError("simulated markdown persistence failure")
        return original(destination, encoded)

    monkeypatch.setattr(
        FilesystemReportStore,
        "_persist_exclusive",
        staticmethod(fail_second_write),
    )

    with pytest.raises(OSError, match="markdown persistence failure"):
        store.persist_report(investigation.id, report)

    reports_dir = tmp_path / "investigations" / investigation.id / "reports"
    assert not (reports_dir / "report.json").exists()
    assert not (reports_dir / "report.md").exists()


def test_report_store_rejects_other_investigation(tmp_path) -> None:
    investigation = Investigation(target="example.org", intent="public_exposure_assessment")
    other = Investigation(target="example.net", intent="public_exposure_assessment")
    report = make_report(other)
    with pytest.raises(ValueError):
        FilesystemReportStore(tmp_path).persist_report(investigation.id, report)


def test_finding_store_defines_contract() -> None:
    assert hasattr(FindingStore, "persist_finding")
    assert hasattr(FilesystemFindingStore, "persist_finding")


def test_finding_store_persists_finding_with_rule_and_evidence_traceability(tmp_path) -> None:
    evidence = make_evidence()
    finding = make_finding(evidence)

    path = FilesystemFindingStore(tmp_path).persist_finding("INV-001", finding)

    assert path == tmp_path / "investigations" / "INV-001" / "findings" / "INV-001_0001-RL-TEST-001.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["conclusion"] == "Registrar information is missing."
    assert payload["rule"]["id"] == "RL-TEST-001"
    assert payload["rule"]["version"] == "1.0"
    assert payload["evidences"][0]["data"]["domain_name"] == "example.org"


def test_finding_store_is_append_only(tmp_path) -> None:
    store = FilesystemFindingStore(tmp_path)
    evidence = make_evidence()
    finding = make_finding(evidence)

    first = store.persist_finding("INV-001", finding)
    second = store.persist_finding("INV-001", finding)

    assert first.name == "INV-001_0001-RL-TEST-001.json"
    assert second.name == "INV-001_0002-RL-TEST-001.json"
    assert first.read_text(encoding="utf-8") == second.read_text(encoding="utf-8")


def test_finding_store_rejects_other_investigation_id_only_by_store_boundary(tmp_path) -> None:
    evidence = make_evidence()
    finding = make_finding(evidence)

    path = FilesystemFindingStore(tmp_path).persist_finding("INV-OTHER", finding)

    assert path.parent == tmp_path / "investigations" / "INV-OTHER" / "findings"


def test_finding_store_rejects_invalid_inputs(tmp_path) -> None:
    store = FilesystemFindingStore(tmp_path)
    with pytest.raises(ValueError):
        store.persist_finding("../escape", make_finding(make_evidence()))
    with pytest.raises(TypeError):
        store.persist_finding("INV-001", object())


def test_finding_store_persists_multiple_supporting_evidences(tmp_path) -> None:
    first = Evidence(
        source=EvidenceSource.SUBLIST3R,
        data={"subdomains": ["www.example.org"]},
        collected_at=datetime(2026, 8, 18, 10, 0, tzinfo=timezone.utc),
    )
    second = Evidence(
        source=EvidenceSource.CRTSH,
        data={"subdomains": ["www.example.org"]},
        collected_at=datetime(2026, 8, 18, 10, 1, tzinfo=timezone.utc),
    )
    rule = Rule(
        id="RL-TEST-CORRELATION",
        version="1.0",
        name="correlation_test",
        description="Test multi-Evidence persistence.",
        category="public_exposure",
        conditions=(
            Condition(
                field="subdomains",
                operator="shared_collection_item_min_sources",
                value=2,
            ),
        ),
        conclusion="Subdomain corroborated.",
    )
    finding = Finding(
        conclusion=rule.conclusion,
        rule=rule,
        evidences=(first, second),
    )

    path = FilesystemFindingStore(tmp_path).persist_finding(
        "INV-CORRELATION",
        finding,
    )
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert [item["source"] for item in payload["evidences"]] == [
        "sublist3r",
        "crtsh",
    ]
    assert [item["data"]["subdomains"] for item in payload["evidences"]] == [
        ["www.example.org"],
        ["www.example.org"],
    ]
