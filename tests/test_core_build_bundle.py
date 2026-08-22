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
    assert "requirements-core.lock" in names
    assert "requirements-dnsrecon.lock" in names
    assert "requirements-sublist3r.lock" in names
    assert "requirements-theharvester.lock" in names
    assert "supply-chain.lock.json" in names
    assert "src/centaurus/__init__.py" in names
    assert "src/centaurus/main.py" in names
    assert "src/centaurus/cli/app.py" in names
    assert "src/centaurus/capabilities/catalog.py" in names
    assert "src/centaurus/config/runtime.py" in names
    assert "src/centaurus/observability/logging.py" in names
    assert "src/centaurus/persistence/report_markdown.py" in names
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


def test_core_dockerfile_consumes_isolated_runtime_locks() -> None:
    """Core and external tools are built from separate validated locks."""

    dockerfile = (Path(__file__).resolve().parents[1] / "docker" / "Dockerfile").read_text(encoding="utf-8")

    assert "COPY requirements-core.lock ./" in dockerfile
    assert "COPY requirements-dnsrecon.lock ./locks/" in dockerfile
    assert "COPY requirements-sublist3r.lock ./locks/" in dockerfile
    assert "COPY requirements-theharvester.lock ./locks/" in dockerfile
    assert "-r requirements-core.lock" in dockerfile
    assert "/opt/centaurus-tools/dnsrecon" in dockerfile
    assert "/opt/centaurus-tools/sublist3r" in dockerfile
    assert "/opt/centaurus-tools/theharvester" in dockerfile
    assert "python -m pip install --no-cache-dir --no-deps ." in dockerfile
    assert "python -m pip check" in dockerfile


def test_core_dockerfile_uses_final_cli_command() -> None:
    dockerfile = (Path(__file__).resolve().parents[1] / "docker" / "Dockerfile").read_text(encoding="utf-8")

    assert 'CMD ["centaurus", "shell"]' in dockerfile
    assert "CENTAURUS framework initialized" not in dockerfile


def test_distribution_declares_console_script_and_cli_dependencies() -> None:
    pyproject = (Path(__file__).resolve().parents[1] / "pyproject.toml").read_text(encoding="utf-8")

    assert 'centaurus = "centaurus.main:main"' in pyproject
    assert 'typer>=0.26.3,<0.28' in pyproject
    assert 'rich>=15,<16' in pyproject
    assert 'prompt-toolkit>=3.0.52,<4' in pyproject


def test_compose_keeps_core_interactive_for_default_shell() -> None:
    compose = (Path(__file__).resolve().parents[1] / "docker" / "compose.yml").read_text(encoding="utf-8")

    assert "stdin_open: true" in compose
    assert "tty: true" in compose
    assert "CENTAURUS_LOG_LEVEL:" in compose
    assert "CENTAURUS_THEHARVESTER_TIMEOUT:" in compose
