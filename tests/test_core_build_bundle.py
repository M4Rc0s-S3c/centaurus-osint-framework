from pathlib import Path
from zipfile import ZipFile

from scripts.create_core_build_bundle import create_bundle


def test_core_build_bundle_contains_only_required_build_inputs(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    bundle = tmp_path / "core-build.zip"

    create_bundle(project_root, bundle)

    with ZipFile(bundle) as archive:
        names = set(archive.namelist())

    assert "Dockerfile" in names
    assert "pyproject.toml" in names
    assert "src/centaurus/__init__.py" in names
    assert any(name.startswith("src/centaurus/core/") for name in names)
    assert not any(name.startswith("tests/") for name in names)
    assert not any(name.startswith(".git/") for name in names)
    assert not any("__pycache__" in name for name in names)
    assert not any(".egg-info/" in name for name in names)


def test_core_build_bundle_is_deterministic(tmp_path: Path) -> None:
    project_root = Path(__file__).resolve().parents[1]
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"

    create_bundle(project_root, first)
    create_bundle(project_root, second)

    assert first.read_bytes() == second.read_bytes()
