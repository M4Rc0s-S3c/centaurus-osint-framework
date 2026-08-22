"""Create the Linux build bundle for the CENTAURUS Core image.

The resulting ZIP is a deployment artifact, not a source checkout.  It contains
only the files required by Docker to build ``centaurus-core:local`` on the OVA.
"""

from __future__ import annotations

from pathlib import Path
from zipfile import ZIP_STORED, ZipFile, ZipInfo

_FIXED_TIMESTAMP = (2026, 8, 16, 0, 0, 0)
_RUNTIME_LOCKS = (
    "requirements-core.lock",
    "requirements-dnsrecon.lock",
    "requirements-sublist3r.lock",
    "requirements-theharvester.lock",
)


def _write_file(archive: ZipFile, source: Path, arcname: str) -> None:
    info = ZipInfo(arcname, date_time=_FIXED_TIMESTAMP)
    # Canonical release serialization: do not depend on the host's DEFLATE
    # implementation (for example zlib versus zlib-ng) or host OS metadata.
    info.compress_type = ZIP_STORED
    info.create_system = 0
    info.external_attr = 0o644 << 16
    info.internal_attr = 0
    info.extra = b""
    info.comment = b""
    archive.writestr(info, source.read_bytes())


def create_bundle(project_root: Path, destination: Path) -> Path:
    """Create a deterministic Core build bundle and return its path."""

    project_root = project_root.resolve()
    destination = destination.resolve()

    dockerfile = project_root / "docker" / "Dockerfile"
    pyproject = project_root / "pyproject.toml"
    runtime_locks = tuple(project_root / name for name in _RUNTIME_LOCKS)
    supply_chain_lock = project_root / "docker" / "supply-chain.lock.json"
    source_root = project_root / "src"

    required = (dockerfile, pyproject, *runtime_locks, supply_chain_lock, source_root)
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing build input(s): {', '.join(missing)}")

    destination.parent.mkdir(parents=True, exist_ok=True)

    with ZipFile(destination, "w") as archive:
        _write_file(archive, dockerfile, "Dockerfile")
        _write_file(archive, pyproject, "pyproject.toml")
        for runtime_lock in runtime_locks:
            _write_file(archive, runtime_lock, runtime_lock.name)
        _write_file(archive, supply_chain_lock, "supply-chain.lock.json")

        for path in sorted(source_root.rglob("*")):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or path.suffix in {".pyc", ".pyo"}:
                continue
            if any(part.endswith(".egg-info") for part in path.parts):
                continue
            arcname = path.relative_to(project_root).as_posix()
            _write_file(archive, path, arcname)

    return destination


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    destination = project_root / "dist" / "centaurus-core-build_v1.0.zip"
    created = create_bundle(project_root, destination)
    print(created)


if __name__ == "__main__":
    main()
