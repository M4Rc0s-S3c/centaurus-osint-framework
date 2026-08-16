"""theHarvester passive OSINT plugin implementation."""

from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import tempfile

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


_THEHARVESTER_EXECUTABLE = "theHarvester"
_THEHARVESTER_TIMEOUT_SECONDS = 300
_THEHARVESTER_LIMIT = 100
_THEHARVESTER_SOURCES = (
    "duckduckgo",
    "rapiddns",
    "urlscan",
    "waybackarchive",
)


class Plugin(BasePlugin):
    """Passive theHarvester collection plugin for domain targets."""

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """Execute a bounded passive collection and return its JSON report."""

        domain = str(parameters.get("domain", "")).strip().rstrip(".").lower()

        if not domain:
            data = {}
        else:
            data = self._run_theharvester(domain)

        return RawObservation(
            source=EvidenceSource.THEHARVESTER,
            data=data,
            collected_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _run_theharvester(domain: str) -> dict:
        """Run theHarvester with passive no-key sources in an isolated temp home."""

        with tempfile.TemporaryDirectory(prefix="centaurus-theharvester-") as temp_dir:
            temp_path = Path(temp_dir)
            report_base = temp_path / "report"
            report_path = report_base.with_suffix(".json")
            sources = ",".join(_THEHARVESTER_SOURCES)
            command = [
                _THEHARVESTER_EXECUTABLE,
                "-d",
                domain,
                "-l",
                str(_THEHARVESTER_LIMIT),
                "-b",
                sources,
                "-f",
                str(report_base),
                "-q",
            ]

            # theHarvester creates an internal SQLite stash below ~/.local.
            # Point HOME at the same temporary boundary so this tool-internal
            # resource disappears together with the execution workspace.
            environment = os.environ.copy()
            environment["HOME"] = temp_dir

            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=_THEHARVESTER_TIMEOUT_SECONDS,
                    cwd=temp_dir,
                    env=environment,
                    shell=False,
                )
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "theHarvester executable is not available in the runtime environment."
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("theHarvester execution timed out.") from exc

            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "").strip()
                message = "theHarvester execution failed."
                if detail:
                    message = f"{message} {detail}"
                raise RuntimeError(message)

            if not report_path.is_file():
                raise RuntimeError(
                    "theHarvester completed without producing the expected JSON report."
                )

            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise RuntimeError(
                    "theHarvester produced an invalid JSON report."
                ) from exc

            if not isinstance(report, dict):
                raise ValueError("theHarvester JSON report must be an object.")

            return {
                "domain": domain,
                "sources": list(_THEHARVESTER_SOURCES),
                "limit": _THEHARVESTER_LIMIT,
                "report": report,
            }
