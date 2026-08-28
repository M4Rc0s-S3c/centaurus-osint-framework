"""Create the deterministic C4-PRIV-2 appliance poweroff bundle."""

from __future__ import annotations

import hashlib
from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

_FIXED_TIMESTAMP = (2026, 8, 28, 0, 0, 0)
_PAYLOADS = (
    "centaurus_poweroff_command.sh",
    "centaurus_poweroff_helper.sh",
    "install_ova_poweroff_helper.sh",
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
    """Create the canonical deterministic C4-PRIV-2 bundle."""

    project_root = project_root.resolve()
    destination = destination.resolve()
    scripts_dir = project_root / "scripts"

    sources = tuple(scripts_dir / name for name in _PAYLOADS)
    missing = [str(path) for path in sources if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"missing C4-PRIV-2 input(s): {', '.join(missing)}")

    manifest_lines: list[str] = []
    payloads: list[tuple[str, bytes]] = []
    for source in sources:
        data = source.read_bytes()
        payloads.append((source.name, data))
        manifest_lines.append(f"{hashlib.sha256(data).hexdigest()}  {source.name}\n")

    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w") as archive:
        for name, data in payloads:
            archive.writestr(_zip_info(name), data)
        archive.writestr(
            _zip_info("MANIFEST_SHA256.txt"),
            "".join(manifest_lines).encode("ascii"),
        )

    return destination


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    destination = project_root / "dist" / "centaurus-ova-poweroff_v1.0.zip"
    print(create_bundle(project_root, destination))


if __name__ == "__main__":
    main()
