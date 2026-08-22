from pathlib import Path
from zipfile import ZIP_STORED, ZipFile

from scripts.create_core_build_bundle import create_bundle


def test_core_build_bundle_uses_cross_platform_canonical_zip_metadata(
    tmp_path: Path,
) -> None:
    """Release ZIP serialization must not depend on host OS or DEFLATE."""

    project_root = Path(__file__).resolve().parents[1]
    bundle = tmp_path / "core-build.zip"

    create_bundle(project_root, bundle)

    with ZipFile(bundle) as archive:
        infos = archive.infolist()

    assert infos
    assert all(info.compress_type == ZIP_STORED for info in infos)
    assert all(info.create_system == 0 for info in infos)
    assert all(info.date_time == (2026, 8, 16, 0, 0, 0) for info in infos)
    assert all(info.external_attr == 0o644 << 16 for info in infos)
    assert all(info.internal_attr == 0 for info in infos)
    assert all(info.extra == b"" for info in infos)
    assert all(info.comment == b"" for info in infos)
