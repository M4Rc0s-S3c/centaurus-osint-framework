"""Deterministic Markdown projection for persisted Reports."""

from __future__ import annotations

import json
from typing import Any

from centaurus.persistence.serialization import json_default
from centaurus.report.report import Report


def _inline_json(value: Any) -> str:
    """Render a compact deterministic JSON value for Markdown metadata."""

    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        default=json_default,
    )


def _indented_json(value: Any) -> list[str]:
    """Render deterministic JSON as an indented Markdown code block."""

    encoded = json.dumps(
        value,
        ensure_ascii=False,
        indent=2,
        sort_keys=True,
        default=json_default,
    )
    return [f"    {line}" for line in encoded.splitlines()]


def _blockquote(value: str) -> list[str]:
    """Render untrusted analyst text as a Markdown blockquote."""

    return [f"> {line}" if line else ">" for line in value.splitlines()]


def _utc_iso(value) -> str:
    """Render a UTC datetime using an explicit ``Z`` suffix."""

    return value.isoformat().replace("+00:00", "Z")


def render_report_markdown(report: Report) -> str:
    """Project a domain Report into deterministic analyst-facing Markdown.

    The Markdown contains no LLM output and creates no new domain knowledge.
    ``report.json`` remains the authoritative persisted representation; this
    file is a human-readable projection of the same Report snapshot.
    """

    if not isinstance(report, Report):
        raise TypeError("report must be a Report instance")

    lines = [
        "# CENTAURUS OSINT Investigation Report",
        "",
        "## Investigation context",
        "",
        f"- **Investigation ID:** `{report.investigation_id}`",
        f"- **Report generated:** `{_utc_iso(report.generated_at)}`",
        f"- **Target:** `{report.target_type}:{report.target}`",
        f"- **Intent:** `{report.intent}`",
        f"- **Findings:** {len(report.findings)}",
        "",
        "## Analyst question",
        "",
    ]

    if report.analyst_question is None:
        lines.extend(
            [
                "No analyst question was recorded for this Report.",
                "",
            ]
        )
    else:
        lines.extend(_blockquote(report.analyst_question))
        lines.append("")

    lines.extend(
        [
            "## Report provenance",
            "",
            "- **Authoritative artifact:** `report.json`",
            "- **Markdown role:** deterministic projection of the persisted Report",
            "",
            "## Findings",
            "",
        ]
    )

    if not report.findings:
        lines.extend(
            [
                "No Findings were produced.",
                "",
            ]
        )
        return "\n".join(lines)

    for index, finding in enumerate(report.findings, start=1):
        rule = finding.rule
        finding_ref = f"F-{index:03d}"
        lines.extend(
            [
                f"### {finding_ref} — `{rule.id}` · `{rule.name}`",
                "",
                "#### Conclusion",
                "",
                finding.conclusion,
                "",
                f"- **Rule version:** `{rule.version}`",
                f"- **Category:** `{rule.category}`",
                f"- **Description:** {rule.description}",
                f"- **Supporting Evidence:** {len(finding.evidences)}",
                "",
                "#### Rule conditions",
                "",
            ]
        )

        if rule.conditions:
            for condition_index, condition in enumerate(rule.conditions, start=1):
                lines.append(
                    f"{condition_index}. `{condition.field}` "
                    f"`{condition.operator}` {_inline_json(condition.value)}"
                )
        else:
            lines.append("No conditions were recorded for this Rule.")

        lines.extend(["", "#### Supporting Evidence", ""])

        for evidence_index, evidence in enumerate(finding.evidences, start=1):
            source = getattr(evidence.source, "value", evidence.source)
            lines.extend(
                [
                    f"##### Evidence {evidence_index} — `{source}`",
                    "",
                    f"- **Collected at:** `{evidence.collected_at.isoformat()}`",
                    "- **Data:**",
                    "",
                ]
            )
            lines.extend(_indented_json(evidence.data))
            lines.append("")

    return "\n".join(lines)
