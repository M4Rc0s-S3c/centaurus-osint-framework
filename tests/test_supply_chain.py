import json
from pathlib import Path

import tomllib


ROOT = Path(__file__).resolve().parents[1]
DOCKERFILE = (ROOT / "docker" / "Dockerfile").read_text(encoding="utf-8")
COMPOSE = (ROOT / "docker" / "compose.yml").read_text(encoding="utf-8")
SUPPLY_CHAIN = json.loads(
    (ROOT / "docker" / "supply-chain.lock.json").read_text(encoding="utf-8")
)

LOCK_NAMES = (
    "requirements-core.lock",
    "requirements-dnsrecon.lock",
    "requirements-sublist3r.lock",
    "requirements-theharvester.lock",
)


def _requirements(lock_name: str) -> list[str]:
    text = (ROOT / lock_name).read_text(encoding="utf-8")
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]


def test_python_base_image_is_pinned_to_validated_digest() -> None:
    assert (
        "FROM python:3.12.14-slim@"
        "sha256:2c941e860699f878900b0edc2403613c234d4b32eda3cc9fa7036991a2a63c4a"
        in DOCKERFILE
    )
    assert "FROM python:3.12-slim\n" not in DOCKERFILE


def test_build_backend_versions_are_exactly_pinned() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    assert data["build-system"]["requires"] == ["setuptools==83.0.0"]
    assert SUPPLY_CHAIN["build_backends"] == {
        "setuptools": "83.0.0",
        "flit_core": "3.12.0",
    }
    assert '"setuptools==83.0.0"' in DOCKERFILE
    assert '"flit_core==3.12.0"' in DOCKERFILE
    assert "--no-build-isolation" in DOCKERFILE


def test_all_runtime_locks_use_exact_or_hashed_direct_requirements() -> None:
    for lock_name in LOCK_NAMES:
        requirements = _requirements(lock_name)
        assert requirements
        assert all(
            "==" in requirement or " @ https://" in requirement
            for requirement in requirements
        )
        assert not any(
            marker in requirement
            for requirement in requirements
            for marker in (">=", "<=", "~=", "!=")
        )


def test_core_lock_excludes_external_tool_dependency_stacks() -> None:
    core = "\n".join(_requirements("requirements-core.lock")).lower()

    for marker in (
        "dnsrecon",
        "sublist3r",
        "theharvester",
        "fastapi",
        "slowapi",
        "ujson",
        "uvicorn",
    ):
        assert marker not in core

    for requirement in (
        "python-whois==0.9.6",
        "httpx==0.28.1",
        "typer==0.27.1",
        "rich==15.0.0",
        "prompt_toolkit==3.0.53",
    ):
        assert requirement.lower() in core


def test_tool_locks_preserve_incompatible_upstream_versions_separately() -> None:
    dnsrecon = _requirements("requirements-dnsrecon.lock")
    theharvester = _requirements("requirements-theharvester.lock")

    assert "fastapi==0.138.1" in dnsrecon
    assert "slowapi==0.1.10" in dnsrecon
    assert "ujson==5.13.0" in dnsrecon
    assert "uvicorn==0.49.0" in dnsrecon

    assert "fastapi==0.136.3" in theharvester
    assert "slowapi==0.1.9" in theharvester
    assert "ujson==5.12.1" in theharvester
    assert "uvicorn==0.48.0" in theharvester


def test_external_tool_sources_are_hash_pinned_in_their_own_locks() -> None:
    assert (
        "dnsrecon @ "
        "https://github.com/darkoperator/dnsrecon/archive/refs/tags/1.6.3.tar.gz"
        "#sha256=7f7e230bb3fae959ff37ac19d1c1deea25089ac6a1bbbbf3b4e26e78ed96bd7a"
        in _requirements("requirements-dnsrecon.lock")
    )
    assert (
        "Sublist3r @ "
        "https://github.com/aboul3la/Sublist3r/archive/"
        "6af1b8c22b5ca035818fbb04c54890896f9b181a.tar.gz"
        "#sha256=9ea8e76d03ad7c7819aded19c212fdc371484b18065afda93d78a21e94f31b0f"
        in _requirements("requirements-sublist3r.lock")
    )
    assert (
        "theHarvester @ "
        "https://github.com/laramies/theHarvester/archive/refs/tags/4.11.1.tar.gz"
        "#sha256=73a931f6e346972939203a82ae38fed24570b3137bfce5d1ae5517e8284df6df"
        in _requirements("requirements-theharvester.lock")
    )


def test_dockerfile_isolates_external_tools_and_exposes_stable_commands() -> None:
    expected = {
        "dnsrecon": "/opt/centaurus-tools/dnsrecon",
        "sublist3r": "/opt/centaurus-tools/sublist3r",
        "theHarvester": "/opt/centaurus-tools/theharvester",
    }

    for command, venv in expected.items():
        assert f"python -m venv {venv}" in DOCKERFILE
        assert f"{venv}/bin/python -m pip check" in DOCKERFILE
        assert f"ln -s {venv}/bin/{command} /usr/local/bin/{command}" in DOCKERFILE

    assert "github.com/" not in DOCKERFILE


def test_ollama_image_is_pinned_to_validated_digest() -> None:
    assert (
        "image: ollama/ollama@"
        "sha256:509fdf54e23bd50d87af646cb51c0a7a203d6a83cc4d6695b3b08c5be1c62c0a"
        in COMPOSE
    )
    assert "ollama/ollama:latest" not in COMPOSE


def test_supply_chain_manifest_records_isolated_tools_and_model_identities() -> None:
    assert SUPPLY_CHAIN["schema_version"] == 2
    assert (
        SUPPLY_CHAIN["validated_from"]["git_commit"]
        == "bb8426ab7979126f8c9e41e0a97db1c71688716b"
    )

    dependency_model = SUPPLY_CHAIN["dependency_model"]
    assert dependency_model["core_lock"] == "requirements-core.lock"
    assert dependency_model["tool_isolation_root"] == "/opt/centaurus-tools"

    tools = SUPPLY_CHAIN["tools"]
    assert tools["dnsrecon"]["lock"] == "requirements-dnsrecon.lock"
    assert tools["sublist3r"]["lock"] == "requirements-sublist3r.lock"
    assert tools["theharvester"]["lock"] == "requirements-theharvester.lock"
    assert tools["sublist3r"]["source_commit"] == (
        "6af1b8c22b5ca035818fbb04c54890896f9b181a"
    )

    model = SUPPLY_CHAIN["model"]
    assert model["name"] == "qwen3:4b"
    assert (
        model["manifest_sha256"]
        == "359d7dd4bcdab3d86b87d73ac27966f4dbb9f5efdfcc75d34a8764a09474fae7"
    )
    assert (
        model["model_blob_digest"]
        == "sha256:3e4cb14174460404e7a233e531675303b2fbf7749c02f91864fe311ab6344e4f"
    )


def test_compose_model_default_matches_supply_chain_manifest() -> None:
    assert (
        f'OLLAMA_MODEL: "${{OLLAMA_MODEL:-{SUPPLY_CHAIN["model"]["name"]}}}"'
        in COMPOSE
    )
