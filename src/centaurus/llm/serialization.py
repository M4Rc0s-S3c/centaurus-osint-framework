"""Representation of domain Reports for LLM input."""

import json

from centaurus.report.report import Report


def serialize_report(report: Report) -> str:
    """Serialize a Report into deterministic, structured JSON text."""

    if not isinstance(report, Report):
        raise TypeError("report must be a Report instance")

    payload = {
        "investigation_id": report.investigation_id,
        "findings": [
            {
                "conclusion": finding.conclusion,
                "rule_id": finding.rule.id,
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
            for finding in report.findings
        ],
    }

    return json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
