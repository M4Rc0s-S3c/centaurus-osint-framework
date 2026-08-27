"""Create the deterministic host-integration bundle for the CENTAURUS OVA.

This artifact is appliance-specific.  It is intentionally separate from the
Core Docker build bundle so the G2 Git+Docker deployment contract remains
unchanged.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

_FIXED_TIMESTAMP = (2026, 8, 26, 0, 0, 0)
_PAYLOADS = (
    "centaurus_host_command.sh",
    "centaurus_runtime_broker.sh",
    "install_ova_runtime_broker.sh",
)


def _zip_info(name: str) -> ZipInfo:
    info = ZipInfo(name, date_time=_FIXED_TIMESTAMP)
    info.compress_type = ZIP_STORED
    info.create_system = 0
    info.external_attr = 0o644 << 16
    info.internal_attr = 0
    info.extra = b""
    info.comment = b""
    return info


def create_bundle(project_root: Path, destination: Path) -> Path:
    """Create the canonical OVA runtime-broker bundle."""

    project_root = project_root.resolve()
    destination = destination.resolve()
    scripts_dir = project_root / "scripts"

    sources = tuple(scripts_dir / name for name in _PAYLOADS)
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing OVA broker input(s): {', '.join(missing)}")

    manifest_lines = []
    payloads: list[tuple[str, bytes]] = []
    for source in sources:
        data = source.read_bytes()
        payloads.append((source.name, data))
        manifest_lines.append(f"{hashlib.sha256(data).hexdigest()}  {source.name}\n")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w") as archive:
        for name, data in payloads:
            archive.writestr(_zip_info(name), data)
        manifest = "".join(manifest_lines).encode("ascii")
        archive.writestr(_zip_info("MANIFEST_SHA256.txt"), manifest)

    return destination


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    destination = project_root / "dist" / "centaurus-ova-runtime-broker_v1.0.zip"
    print(create_bundle(project_root, destination))


if __name__ == "__main__":
    main()
