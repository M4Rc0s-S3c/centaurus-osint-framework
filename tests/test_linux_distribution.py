import hashlib
import json
from pathlib import Path

import pytest

from scripts.verify_ollama_model import verify_model


ROOT = Path(__file__).resolve().parents[1]
COMPOSE = (ROOT / "docker" / "compose.yml").read_text(encoding="utf-8")
BOOTSTRAP = (ROOT / "scripts" / "bootstrap_linux_release.sh").read_text(
    encoding="utf-8"
)


def test_compose_parameterizes_host_persistence_without_changing_ova_defaults() -> None:
    assert (
        "${CENTAURUS_OLLAMA_HOST_DIR:-/opt/osint-framework/runtime/ollama}:"
        "/root/.ollama:ro"
        in COMPOSE
    )
    assert "${CENTAURUS_WORKSPACE_HOST_DIR:-/workspace}:/workspace" in COMPOSE


def test_linux_bootstrap_requires_clean_exact_release_checkout() -> None:
    assert 'git status --porcelain --untracked-files=all' in BOOTSTRAP
    assert "CENTAURUS_RELEASE_COMMIT" in BOOTSTRAP
    assert '"$(uname -s)" = "Linux"' in BOOTSTRAP


def test_linux_bootstrap_builds_from_deterministic_bundle_and_isolated_locks() -> None:
    assert "scripts/create_core_build_bundle.py" in BOOTSTRAP
    assert "centaurus-core:g2-candidate" in BOOTSTRAP
    assert "/opt/centaurus-tools/dnsrecon/bin/python" in BOOTSTRAP
    assert "/opt/centaurus-tools/sublist3r/bin/python" in BOOTSTRAP
    assert "/opt/centaurus-tools/theharvester/bin/python" in BOOTSTRAP


def test_linux_bootstrap_provisions_model_writable_then_uses_release_compose() -> None:
    assert 'ollama pull "$MODEL_NAME"' in BOOTSTRAP
    assert "scripts/verify_ollama_model.py" in BOOTSTRAP
    assert "--env-file" in BOOTSTRAP
    assert "up -d --force-recreate centaurus-ollama" in BOOTSTRAP
    assert "LINUX_BOOTSTRAP=PASS" in BOOTSTRAP


def test_model_verifier_accepts_exact_manifest_and_blobs(tmp_path: Path) -> None:
    models_root = tmp_path / "models"
    manifest_path = (
        models_root
        / "manifests"
        / "registry.ollama.ai"
        / "library"
        / "demo"
        / "1b"
    )
    blobs = models_root / "blobs"
    blobs.mkdir(parents=True)
    manifest_path.parent.mkdir(parents=True)

    payloads = {
        "config_digest": b"config",
        "model_blob_digest": b"model",
        "template_digest": b"template",
        "license_digest": b"license",
        "params_digest": b"params",
    }
    digests = {
        key: "sha256:" + hashlib.sha256(value).hexdigest()
        for key, value in payloads.items()
    }

    for key, value in payloads.items():
        digest = digests[key].split(":", 1)[1]
        (blobs / f"sha256-{digest}").write_bytes(value)

    manifest = {
        "config": {"digest": digests["config_digest"]},
        "layers": [
            {"digest": digests["model_blob_digest"]},
            {"digest": digests["template_digest"]},
            {"digest": digests["license_digest"]},
            {"digest": digests["params_digest"]},
        ],
    }
    manifest_bytes = json.dumps(manifest, separators=(",", ":")).encode()
    manifest_path.write_bytes(manifest_bytes)

    supply = {
        "model": {
            "name": "demo:1b",
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            **digests,
        }
    }
    supply_path = tmp_path / "supply.json"
    supply_path.write_text(json.dumps(supply), encoding="utf-8")

    verify_model(models_root, supply_path)


def test_model_verifier_rejects_modified_blob(tmp_path: Path) -> None:
    models_root = tmp_path / "models"
    manifest_path = (
        models_root
        / "manifests"
        / "registry.ollama.ai"
        / "library"
        / "demo"
        / "1b"
    )
    blobs = models_root / "blobs"
    blobs.mkdir(parents=True)
    manifest_path.parent.mkdir(parents=True)

    values = [b"config", b"model", b"template", b"license", b"params"]
    names = [
        "config_digest",
        "model_blob_digest",
        "template_digest",
        "license_digest",
        "params_digest",
    ]
    digests = {
        name: "sha256:" + hashlib.sha256(value).hexdigest()
        for name, value in zip(names, values, strict=True)
    }
    for name, value in zip(names, values, strict=True):
        digest = digests[name].split(":", 1)[1]
        (blobs / f"sha256-{digest}").write_bytes(value)

    manifest = {
        "config": {"digest": digests["config_digest"]},
        "layers": [{"digest": digests[name]} for name in names[1:]],
    }
    manifest_bytes = json.dumps(manifest, separators=(",", ":")).encode()
    manifest_path.write_bytes(manifest_bytes)

    supply = {
        "model": {
            "name": "demo:1b",
            "manifest_sha256": hashlib.sha256(manifest_bytes).hexdigest(),
            **digests,
        }
    }
    supply_path = tmp_path / "supply.json"
    supply_path.write_text(json.dumps(supply), encoding="utf-8")

    model_digest = digests["model_blob_digest"].split(":", 1)[1]
    (blobs / f"sha256-{model_digest}").write_bytes(b"tampered")

    with pytest.raises(ValueError, match="blob SHA-256 mismatch"):
        verify_model(models_root, supply_path)
