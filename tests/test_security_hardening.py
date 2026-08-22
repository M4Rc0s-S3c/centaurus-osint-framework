from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = (ROOT / "docker/compose.yml").read_text(encoding="utf-8")
DOCKERFILE = (ROOT / "docker/Dockerfile").read_text(encoding="utf-8")


def _service_block(name: str, next_name: str | None = None) -> str:
    start = COMPOSE.index(f"  {name}:")
    if next_name is None:
        end = COMPOSE.index("\nnetworks:\n", start)
    else:
        end = COMPOSE.index(f"\n  {next_name}:", start)
    return COMPOSE[start:end]


def test_core_image_uses_fixed_non_root_runtime_identity() -> None:
    assert "groupadd --gid 1000 centaurus" in DOCKERFILE
    assert "useradd --uid 1000 --gid 1000" in DOCKERFILE
    assert "chown 1000:1000 /workspace" in DOCKERFILE
    assert "USER 1000:1000" in DOCKERFILE


def test_core_container_applies_least_privilege_filesystem_and_process_controls() -> None:
    core = _service_block("centaurus-core")

    assert "read_only: true" in core
    assert "/tmp:rw,nosuid,nodev,noexec,size=256m" in core
    assert re.search(r"cap_drop:\s*\n\s*- ALL", core)
    assert "no-new-privileges:true" in core
    assert "pids_limit: 256" in core
    assert "init: true" in core
    assert (
        "${CENTAURUS_WORKSPACE_HOST_DIR:-/workspace}:/workspace"
        in core
    )


def test_ollama_is_not_published_to_host_and_cloud_features_are_disabled() -> None:
    ollama = _service_block("centaurus-ollama", "centaurus-core")

    assert "ports:" not in ollama
    assert "11434:11434" not in ollama
    assert 'OLLAMA_NO_CLOUD: "1"' in ollama
    assert (
        "${CENTAURUS_OLLAMA_HOST_DIR:-/opt/osint-framework/runtime/ollama}"
        ":/root/.ollama:ro" in ollama
    )
    assert re.search(r"cap_drop:\s*\n\s*- ALL", ollama)
    assert "no-new-privileges:true" in ollama
    assert "pids_limit: 512" in ollama


def test_networks_separate_llm_isolation_from_core_egress() -> None:
    ollama = _service_block("centaurus-ollama", "centaurus-core")
    core = _service_block("centaurus-core")
    networks = COMPOSE[COMPOSE.index("\nnetworks:\n") :]

    assert "- centaurus-llm-network" in ollama
    assert "centaurus-egress-network" not in ollama

    assert "- centaurus-llm-network" in core
    assert "- centaurus-egress-network" in core

    assert re.search(
        r"centaurus-llm-network:\s*\n\s*driver: bridge\s*\n\s*internal: true",
        networks,
    )
    assert re.search(
        r"centaurus-egress-network:\s*\n\s*driver: bridge",
        networks,
    )


def test_compose_does_not_grant_docker_or_privileged_host_access() -> None:
    lowered = COMPOSE.lower()

    assert "/var/run/docker.sock" not in lowered
    assert "docker.sock" not in lowered
    assert "privileged:" not in lowered
    assert "cap_add:" not in lowered
    assert "network_mode: host" not in lowered
    assert "pid: host" not in lowered
    assert "ipc: host" not in lowered


def test_no_runtime_credentials_are_added_to_compose() -> None:
    lowered = COMPOSE.lower()

    for marker in (
        "api_key",
        "password:",
        "token:",
        "secret:",
        "id_ed25519",
        "authorization:",
    ):
        assert marker not in lowered


def test_core_uses_ephemeral_home_on_tmpfs() -> None:
    core = _service_block("centaurus-core")
    assert "HOME: /tmp/centaurus" in core
