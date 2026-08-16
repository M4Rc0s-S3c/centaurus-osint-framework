"""Sublist3r plugin implementation."""

from datetime import datetime, timezone
from pathlib import Path
import subprocess
import tempfile

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


_SUBLIST3R_EXECUTABLE = "sublist3r"
_SUBLIST3R_TIMEOUT_SECONDS = 180


class Plugin(BasePlugin):
    """Passive Sublist3r subdomain-enumeration plugin for domain targets."""

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """Execute Sublist3r and return the textual subdomain results."""

        domain = str(parameters.get("domain", "")).strip().rstrip(".").lower()

        if not domain:
            data = {}
        else:
            data = self._run_sublist3r(domain)

        return RawObservation(
            source=EvidenceSource.SUBLIST3R,
            data=data,
            collected_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _run_sublist3r(domain: str) -> dict:
        """Run one bounded passive enumeration and read its output file."""

        with tempfile.TemporaryDirectory(prefix="centaurus-sublist3r-") as temp_dir:
            output_path = Path(temp_dir) / "subdomains.txt"
            command = [
                _SUBLIST3R_EXECUTABLE,
                "-d",
                domain,
                "-o",
                str(output_path),
                "-n",
            ]

            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=_SUBLIST3R_TIMEOUT_SECONDS,
                )
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "Sublist3r executable is not available in the runtime environment."
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("Sublist3r execution timed out.") from exc

            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "").strip()
                message = "Sublist3r execution failed."
                if detail:
                    message = f"{message} {detail}"
                raise RuntimeError(message)

            # Upstream writes the output file only when it finds subdomains.
            # A successful process with no file therefore represents a valid
            # zero-result observation, not a framework failure.
            if output_path.is_file():
                subdomains = [
                    line.strip()
                    for line in output_path.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ]
            else:
                subdomains = []

            return {
                "domain": domain,
                "subdomains": subdomains,
            }
