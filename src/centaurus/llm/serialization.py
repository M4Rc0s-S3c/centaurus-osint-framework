"""Representation of domain Reports for LLM input."""

import json

from centaurus.report.report import Report


def serialize_report(report: Report) -> str:
    """Serialize a Report into deterministic, structured JSON text."""

    if not isinstance(report, Report):
        raise TypeError("report must be a Report instance")

    # Deliberate allowlist: Report provenance such as analyst_question,
    # generated_at, Target and Intent is not part of the LLM #2 prompt.
    # LLM #2 remains grounded only in the established Finding/Evidence view.
    payload = {
        "investigation_id": report.investigation_id,
        "findings": [
            {
                "finding_ref": f"F-{index:03d}",
                "conclusion": finding.conclusion,
                "rule_id": finding.rule.id,
                "rule_version": finding.rule.version,
                "rule_name": finding.rule.name,
                "rule_category": finding.rule.category,
                "rule_description": finding.rule.description,
                "evidence": [
                    {
                        "source": evidence.source.value,
                        "data": evidence.data,
                        "collected_at": evidence.collected_at.isoformat(),
                    }
                    for evidence in finding.evidences
                ],
            }
            for index, finding in enumerate(report.findings, start=1)
        ],
    }

    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
