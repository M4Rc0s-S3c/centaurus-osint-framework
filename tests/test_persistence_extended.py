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
        category="whois_rdap",
        conditions=(Condition(field="registrar", operator="missing"),),
        conclusion="Registrar information is missing.",
    )
    return Finding(
        conclusion=rule.conclusion,
        rule=rule,
        evidences=(evidence,),
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
    investigation = Investigation(objective="example.org")
    investigation.add_finding(finding)
    report = Report(investigation_id=investigation.id, findings=(finding,))

    path = FilesystemReportStore(tmp_path).persist_report(investigation.id, report)
    assert path == tmp_path / "investigations" / investigation.id / "reports" / "report.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["investigation_id"] == investigation.id
    assert payload["findings"][0]["rule"]["id"] == "RL-TEST-001"
    assert payload["findings"][0]["evidences"][0]["data"]["domain_name"] == "example.org"


def test_report_store_rejects_second_report(tmp_path) -> None:
    investigation = Investigation(objective="example.org")
    report = Report(investigation_id=investigation.id, findings=())
    store = FilesystemReportStore(tmp_path)
    store.persist_report(investigation.id, report)
    with pytest.raises(FileExistsError):
        store.persist_report(investigation.id, report)


def test_report_store_rejects_other_investigation(tmp_path) -> None:
    investigation = Investigation(objective="example.org")
    other = Investigation(objective="example.net")
    report = Report(investigation_id=other.id, findings=())
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
