"""Infrastructure-only JSON serialization helpers for domain snapshots."""

from datetime import date, datetime
from enum import Enum
from typing import Any


def json_default(value: Any) -> str:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Enum):
        return value.value
    raise TypeError(f"Object of type {type(value).__name__} is not JSON serializable")


def evidence_payload(evidence: Any) -> dict[str, Any]:
    return {
        "source": getattr(evidence.source, "value", evidence.source),
        "collected_at": evidence.collected_at,
        "data": evidence.data,
    }

def rule_payload(rule: Any) -> dict[str, Any]:
    return {
        "id": rule.id,
        "version": rule.version,
        "name": rule.name,
        "description": rule.description,
        "category": rule.category,
        "conditions": [
            {"field": c.field, "operator": c.operator, "value": c.value}
            for c in rule.conditions
        ],
        "conclusion": rule.conclusion,
    }

def finding_payload(finding: Any) -> dict[str, Any]:
    return {
        "conclusion": finding.conclusion,
        "rule": rule_payload(finding.rule),
        "evidences": [evidence_payload(e) for e in finding.evidences],
    }
