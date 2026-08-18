"""Validated ephemeral contract for LLM #2 analyst assistance."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any

from centaurus.llm.exceptions import LLMResponseError
from centaurus.report.report import Report


PRESENTATION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": [
        "executive_summary",
        "finding_summaries",
        "risk_considerations",
        "recommendations",
    ],
    "properties": {
        "executive_summary": {
            "type": "object",
            "additionalProperties": False,
            "required": ["text", "supporting_finding_refs"],
            "properties": {
                "text": {"type": "string", "minLength": 1},
                "supporting_finding_refs": {
                    "type": "array",
                    "items": {"type": "string", "pattern": r"^F-[0-9]{3}$"},
                    "uniqueItems": True,
                },
            },
        },
        "finding_summaries": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["finding_ref", "text"],
                "properties": {
                    "finding_ref": {
                        "type": "string",
                        "pattern": r"^F-[0-9]{3}$",
                    },
                    "text": {"type": "string", "minLength": 1},
                },
            },
        },
        "risk_considerations": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "supporting_finding_refs"],
                "properties": {
                    "text": {"type": "string", "minLength": 1},
                    "supporting_finding_refs": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string",
                            "pattern": r"^F-[0-9]{3}$",
                        },
                        "uniqueItems": True,
                    },
                },
            },
        },
        "recommendations": {
            "type": "array",
            "maxItems": 5,
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["text", "supporting_finding_refs"],
                "properties": {
                    "text": {"type": "string", "minLength": 1},
                    "supporting_finding_refs": {
                        "type": "array",
                        "minItems": 1,
                        "items": {
                            "type": "string",
                            "pattern": r"^F-[0-9]{3}$",
                        },
                        "uniqueItems": True,
                    },
                },
            },
        },
    },
}


@dataclass(frozen=True, slots=True)
class GroundedStatement:
    """Ephemeral presentation statement anchored to Report Findings."""

    text: str
    supporting_finding_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class FindingSummary:
    """One concise linguistic summary of one Report Finding."""

    finding_ref: str
    text: str


@dataclass(frozen=True, slots=True)
class AnalystPresentation:
    """Validated non-domain representation returned by LLM #2."""

    executive_summary: GroundedStatement
    finding_summaries: tuple[FindingSummary, ...]
    risk_considerations: tuple[GroundedStatement, ...]
    recommendations: tuple[GroundedStatement, ...]
    omitted_risk_considerations: int = 0
    omitted_recommendations: int = 0


_OBSERVATIONAL_ABSENCE_MARKERS = (
    "not observed",
    "was not observed",
    "were not observed",
)

_ABSOLUTE_ABSENCE_PATTERNS = (
    re.compile(r"\babsence of\b", re.IGNORECASE),
    re.compile(r"\bmissing\b", re.IGNORECASE),
    re.compile(r"\bnot present\b", re.IGNORECASE),
    re.compile(r"\blacks?\b", re.IGNORECASE),
    re.compile(r"\bwithout\b", re.IGNORECASE),
    re.compile(
        r"\bno\s+(?:direct\s+)?(?:spf|dmarc|dnssec)\b"
        r"(?![^.!?]{0,80}\b(?:was|were)\s+(?:directly\s+)?observed\b)",
        re.IGNORECASE,
    ),
)

_UNSUPPORTED_TARGET_STATE_PATTERNS = (
    re.compile(r"\bnot properly configured\b", re.IGNORECASE),
    re.compile(r"\bimproperly configured\b", re.IGNORECASE),
    re.compile(r"\bmisconfigured\b", re.IGNORECASE),
    re.compile(r"\btarget\s+(?:is|appears|seems|may be|might be)\s+vulnerable\b", re.IGNORECASE),
    re.compile(r"\btarget\s+(?:is|appears|seems|may be|might be)\s+compromised\b", re.IGNORECASE),
    re.compile(r"\btarget\s+(?:is|appears|seems|may be|might be)\s+malicious\b", re.IGNORECASE),
    re.compile(r"\btarget\s+(?:is|appears|seems|may be|might be)\s+exploited\b", re.IGNORECASE),
    re.compile(r"\btarget\s+(?:is|appears|seems|may be|might be)\s+under\s+(?:active\s+)?attack\b", re.IGNORECASE),
)

_UNSUPPORTED_RISK_INTENSITY_PATTERNS = (
    re.compile(
        r"\b(?:significantly|substantially|materially|considerably)\s+"
        r"(?:increase|increases|raise|raises|elevate|elevates)\s+(?:the\s+)?risk\b",
        re.IGNORECASE,
    ),
)

_FORBIDDEN_RATING_PATTERNS = (
    re.compile(r"\b(?:high|medium|low|critical)\s+(?:risk|severity)\b", re.IGNORECASE),
    re.compile(r"\brisk\s+level\b", re.IGNORECASE),
    re.compile(r"\brisk\s+score\b", re.IGNORECASE),
    re.compile(r"\bseverity\s+(?:level|score)\b", re.IGNORECASE),
    re.compile(r"\bconfidence\s+(?:level|score)\b", re.IGNORECASE),
    re.compile(r"\bcvss\b", re.IGNORECASE),
    re.compile(r"\briesgo\s+(?:alto|medio|bajo|cr[ií]tico)\b", re.IGNORECASE),
    re.compile(r"\bnivel\s+de\s+riesgo\b", re.IGNORECASE),
    re.compile(r"\bseveridad\b", re.IGNORECASE),
    re.compile(r"\bpuntuaci[oó]n\s+de\s+riesgo\b", re.IGNORECASE),
)


def finding_refs(report: Report) -> tuple[str, ...]:
    """Return deterministic presentation-only references for Report Findings."""

    if not isinstance(report, Report):
        raise TypeError("report must be a Report instance")

    return tuple(f"F-{index:03d}" for index in range(1, len(report.findings) + 1))


def parse_analyst_presentation(report: Report, text: str) -> AnalystPresentation:
    """Parse and validate one structured LLM #2 response against a Report."""

    if not isinstance(report, Report):
        raise TypeError("report must be a Report instance")
    if not isinstance(text, str) or not text.strip():
        raise LLMResponseError("LLM presentation response is empty")

    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise LLMResponseError("LLM presentation response is not valid JSON") from exc

    if not isinstance(payload, dict):
        raise LLMResponseError("LLM presentation response must be a JSON object")

    expected_keys = {
        "executive_summary",
        "finding_summaries",
        "risk_considerations",
        "recommendations",
    }
    if set(payload) != expected_keys:
        raise LLMResponseError("LLM presentation response has unexpected fields")

    allowed_refs = finding_refs(report)
    allowed_ref_set = set(allowed_refs)

    executive = _parse_grounded_statement(
        payload["executive_summary"],
        allowed_ref_set,
        field_name="executive_summary",
        refs_required=bool(allowed_refs),
    )

    if set(executive.supporting_finding_refs) != allowed_ref_set:
        raise LLMResponseError(
            "Executive summary must reference every Finding in the Report"
        )

    summaries_raw = payload["finding_summaries"]
    if not isinstance(summaries_raw, list):
        raise LLMResponseError("finding_summaries must be a list")

    summaries: list[FindingSummary] = []
    seen_summary_refs: set[str] = set()
    for item in summaries_raw:
        if not isinstance(item, dict) or set(item) != {"finding_ref", "text"}:
            raise LLMResponseError("finding_summaries contains an invalid item")
        ref = item["finding_ref"]
        summary_text = _non_empty_text(item["text"], "finding summary")
        if ref not in allowed_ref_set:
            raise LLMResponseError(f"Unknown Finding reference: {ref!r}")
        if ref in seen_summary_refs:
            raise LLMResponseError(f"Duplicate Finding summary reference: {ref!r}")
        _reject_risk_ratings(summary_text)
        seen_summary_refs.add(ref)
        summaries.append(FindingSummary(finding_ref=ref, text=summary_text))

    if seen_summary_refs != allowed_ref_set:
        raise LLMResponseError(
            "LLM presentation must contain exactly one summary for every Report Finding"
        )

    risk_considerations = _parse_grounded_list(
        payload["risk_considerations"],
        allowed_ref_set,
        field_name="risk_considerations",
        maximum=5,
    )
    recommendations = _parse_grounded_list(
        payload["recommendations"],
        allowed_ref_set,
        field_name="recommendations",
        maximum=5,
    )

    if not allowed_refs and (risk_considerations or recommendations):
        raise LLMResponseError(
            "A Report without Findings cannot produce risk considerations or recommendations"
        )

    _validate_required_grounding_semantics(
        report,
        executive=executive,
        summaries=summaries,
    )
    risk_considerations, omitted_risks = _filter_optional_grounded_statements(
        report,
        risk_considerations,
    )
    recommendations, omitted_recommendations = _filter_optional_grounded_statements(
        report,
        recommendations,
    )

    order = {ref: index for index, ref in enumerate(allowed_refs)}
    summaries.sort(key=lambda item: order[item.finding_ref])

    return AnalystPresentation(
        executive_summary=executive,
        finding_summaries=tuple(summaries),
        risk_considerations=tuple(risk_considerations),
        recommendations=tuple(recommendations),
        omitted_risk_considerations=omitted_risks,
        omitted_recommendations=omitted_recommendations,
    )


def render_analyst_presentation(
    report: Report,
    presentation: AnalystPresentation,
) -> str:
    """Render validated analyst assistance without changing the Report."""

    if not isinstance(report, Report):
        raise TypeError("report must be a Report instance")
    if not isinstance(presentation, AnalystPresentation):
        raise TypeError("presentation must be an AnalystPresentation instance")

    rule_ids_by_ref = {
        ref: finding.rule.id
        for ref, finding in zip(finding_refs(report), report.findings, strict=True)
    }

    lines = [
        "Analyst-assistance view — ephemeral and non-authoritative",
        "",
        "Executive summary",
        presentation.executive_summary.text,
    ]

    if presentation.finding_summaries:
        lines.extend(["", "Finding summaries"])
        for item in presentation.finding_summaries:
            rule_id = rule_ids_by_ref[item.finding_ref]
            lines.append(f"- [{item.finding_ref} | {rule_id}] {item.text}")
    else:
        lines.extend(["", "Finding summaries", "- No Findings are present in the Report."])

    lines.extend(["", "Potential risk implications — non-authoritative"])
    if presentation.risk_considerations:
        for item in presentation.risk_considerations:
            refs = ", ".join(item.supporting_finding_refs)
            lines.append(f"- [{refs}] {item.text}")
    else:
        lines.append("- No additional risk implication was produced from the Report Findings.")

    lines.extend(["", "Recommendations for analyst review — advisory"])
    if presentation.recommendations:
        for item in presentation.recommendations:
            refs = ", ".join(item.supporting_finding_refs)
            lines.append(f"- [{refs}] {item.text}")
    else:
        lines.append("- No additional recommendation was produced from the Report Findings.")

    lines.extend(
        [
            "",
            "Scope limitations",
            "- This presentation is grounded only in the Findings and supporting Evidence "
            "contained in the supplied Report.",
            "- It does not create Findings, assign severity or a risk score, or establish "
            "target-specific facts from external knowledge.",
            "- Recommendations are advisory analyst guidance, not Report facts or domain "
            "knowledge, and should be verified against the authoritative report.json/report.md.",
        ]
    )

    omitted_total = (
        presentation.omitted_risk_considerations
        + presentation.omitted_recommendations
    )
    if omitted_total:
        lines.append(
            "- Grounding validation omitted "
            f"{omitted_total} unsafe or insufficiently grounded advisory item(s); "
            "omitted text is not shown or persisted."
        )

    lines.append(
        "- Operational ExecutionFailures are outside the Report and must be reviewed "
        "separately when the investigation status is partial."
    )

    return "\n".join(lines)


def _validate_required_grounding_semantics(
    report: Report,
    *,
    executive: GroundedStatement,
    summaries: list[FindingSummary],
) -> None:
    """Fail closed when mandatory factual presentation text is not grounded."""

    refs = finding_refs(report)
    findings_by_ref = dict(zip(refs, report.findings, strict=True))

    _validate_statement_language(
        executive.text,
        executive.supporting_finding_refs,
        findings_by_ref,
    )
    for summary in summaries:
        _validate_statement_language(
            summary.text,
            (summary.finding_ref,),
            findings_by_ref,
        )


def _filter_optional_grounded_statements(
    report: Report,
    items: list[GroundedStatement],
) -> tuple[list[GroundedStatement], int]:
    """Keep only grounded advisory items; never repair or re-prompt unsafe text."""

    refs = finding_refs(report)
    findings_by_ref = dict(zip(refs, report.findings, strict=True))
    accepted: list[GroundedStatement] = []
    omitted = 0

    for item in items:
        try:
            _validate_statement_language(
                item.text,
                item.supporting_finding_refs,
                findings_by_ref,
            )
        except LLMResponseError:
            omitted += 1
            continue
        accepted.append(item)

    return accepted, omitted


def _validate_statement_language(
    text: str,
    supporting_refs: tuple[str, ...],
    findings_by_ref: dict[str, Any],
) -> None:
    _reject_risk_ratings(text)
    _reject_unsupported_statement(text, supporting_refs, findings_by_ref)

def _reject_unsupported_statement(
    text: str,
    supporting_refs: tuple[str, ...],
    findings_by_ref: dict[str, Any],
) -> None:
    """Fail closed on known wording that upgrades observational evidence to facts."""

    supported_findings = [findings_by_ref[ref] for ref in supporting_refs]
    trusted_claim_text = " ".join(
        " ".join(
            (
                finding.conclusion,
                finding.rule.conclusion,
                finding.rule.description,
            )
        )
        for finding in supported_findings
    ).lower()

    observational_absence = any(
        marker in trusted_claim_text
        for marker in _OBSERVATIONAL_ABSENCE_MARKERS
    )
    if observational_absence:
        for pattern in _ABSOLUTE_ABSENCE_PATTERNS:
            if pattern.search(text):
                raise LLMResponseError(
                    "LLM presentation converted an observational absence into an absolute absence"
                )

    for pattern in _UNSUPPORTED_TARGET_STATE_PATTERNS:
        match = pattern.search(text)
        if match and match.group(0).lower() not in trusted_claim_text:
            raise LLMResponseError(
                "LLM presentation introduced an unsupported target-state assertion"
            )

    for pattern in _UNSUPPORTED_RISK_INTENSITY_PATTERNS:
        if pattern.search(text):
            raise LLMResponseError(
                "LLM presentation introduced unsupported risk intensity"
            )

def _parse_grounded_list(
    value: Any,
    allowed_refs: set[str],
    *,
    field_name: str,
    maximum: int,
) -> list[GroundedStatement]:
    if not isinstance(value, list):
        raise LLMResponseError(f"{field_name} must be a list")
    if len(value) > maximum:
        raise LLMResponseError(f"{field_name} exceeds the maximum of {maximum} items")

    return [
        _parse_grounded_statement(
            item,
            allowed_refs,
            field_name=field_name,
            refs_required=True,
        )
        for item in value
    ]


def _parse_grounded_statement(
    value: Any,
    allowed_refs: set[str],
    *,
    field_name: str,
    refs_required: bool,
) -> GroundedStatement:
    if not isinstance(value, dict) or set(value) != {"text", "supporting_finding_refs"}:
        raise LLMResponseError(f"{field_name} contains an invalid grounded statement")

    statement_text = _non_empty_text(value["text"], field_name)
    refs = value["supporting_finding_refs"]
    if not isinstance(refs, list) or not all(isinstance(ref, str) for ref in refs):
        raise LLMResponseError(f"{field_name} supporting_finding_refs must be a string list")
    if len(refs) != len(set(refs)):
        raise LLMResponseError(f"{field_name} contains duplicate Finding references")
    if refs_required and not refs:
        raise LLMResponseError(f"{field_name} requires at least one Finding reference")

    unknown = [ref for ref in refs if ref not in allowed_refs]
    if unknown:
        raise LLMResponseError(f"Unknown Finding reference: {unknown[0]!r}")

    return GroundedStatement(
        text=statement_text,
        supporting_finding_refs=tuple(refs),
    )


def _non_empty_text(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise LLMResponseError(f"{field_name} requires non-empty text")
    return value.strip()


def _reject_risk_ratings(text: str) -> None:
    for pattern in _FORBIDDEN_RATING_PATTERNS:
        if pattern.search(text):
            raise LLMResponseError(
                "LLM presentation attempted to introduce a prohibited risk/severity rating"
            )
