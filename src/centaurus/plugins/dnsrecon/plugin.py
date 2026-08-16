"""DNSRecon plugin implementation."""

from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import tempfile

from centaurus.evidence import EvidenceSource, RawObservation
from centaurus.plugins.base_plugin import BasePlugin


_DNSRECON_EXECUTABLE = "dnsrecon"
_DNSRECON_TIMEOUT_SECONDS = 120


class Plugin(BasePlugin):
    """DNSRecon standard DNS-enumeration plugin for domain targets."""

    def execute(
        self,
        parameters: dict,
    ) -> RawObservation:
        """Execute DNSRecon and return its original JSON records."""

        domain = str(parameters.get("domain", "")).strip().rstrip(".").lower()

        if not domain:
            data = {}
        else:
            data = self._run_dnsrecon(domain)

        return RawObservation(
            source=EvidenceSource.DNSRECON,
            data=data,
            collected_at=datetime.now(timezone.utc),
        )

    @staticmethod
    def _run_dnsrecon(domain: str) -> dict:
        """Run one bounded DNSRecon standard scan using a temporary JSON file."""

        with tempfile.TemporaryDirectory(prefix="centaurus-dnsrecon-") as temp_dir:
            output_path = Path(temp_dir) / "dnsrecon.json"
            command = [
                _DNSRECON_EXECUTABLE,
                "-d",
                domain,
                "-t",
                "std",
                "-j",
                str(output_path),
                "--disable_check_recursion",
                "--disable_check_bindversion",
            ]

            try:
                completed = subprocess.run(
                    command,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=_DNSRECON_TIMEOUT_SECONDS,
                )
            except FileNotFoundError as exc:
                raise RuntimeError(
                    "DNSRecon executable is not available in the runtime environment."
                ) from exc
            except subprocess.TimeoutExpired as exc:
                raise RuntimeError("DNSRecon execution timed out.") from exc

            if completed.returncode != 0:
                detail = (completed.stderr or completed.stdout or "").strip()
                message = "DNSRecon execution failed."
                if detail:
                    message = f"{message} {detail}"
                raise RuntimeError(message)

            if not output_path.is_file():
                raise RuntimeError("DNSRecon did not produce the expected JSON output file.")

            try:
                records = json.loads(output_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                raise RuntimeError("DNSRecon produced invalid JSON output.") from exc

            if not isinstance(records, list):
                raise RuntimeError("DNSRecon JSON output must be a list of records.")

            return {"records": records}
