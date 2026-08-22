"""Verify the immutable Ollama model identity recorded by CENTAURUS.

This verifier uses only the Python standard library so it can run on a clean
Linux deployment host before the CENTAURUS Core container is started.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def verify_model(models_root: Path, supply_chain_path: Path) -> None:
    supply: dict[str, Any] = json.loads(
        supply_chain_path.read_text(encoding="utf-8")
    )
    model = supply["model"]
    model_name = model["name"]

    if ":" not in model_name:
        raise ValueError(f"model name must include a tag: {model_name}")

    repository, tag = model_name.rsplit(":", 1)
    manifest = (
        models_root
        / "manifests"
        / "registry.ollama.ai"
        / "library"
        / repository
        / tag
    )

    if not manifest.is_file():
        raise FileNotFoundError(f"model manifest not found: {manifest}")

    manifest_bytes = manifest.read_bytes()
    manifest_sha256 = hashlib.sha256(manifest_bytes).hexdigest()
    expected_manifest = model["manifest_sha256"]

    print(f"MODEL={model_name}")
    print(f"MANIFEST={manifest}")
    print(f"MANIFEST_SHA256={manifest_sha256}")

    if manifest_sha256 != expected_manifest:
        raise ValueError(
            "manifest SHA-256 mismatch: "
            f"expected {expected_manifest}, got {manifest_sha256}"
        )

    payload = json.loads(manifest_bytes)
    config_digest = payload["config"]["digest"]
    expected_config = model["config_digest"]

    if config_digest != expected_config:
        raise ValueError(
            "config digest mismatch: "
            f"expected {expected_config}, got {config_digest}"
        )

    expected_layers = {
        model["model_blob_digest"],
        model["template_digest"],
        model["license_digest"],
        model["params_digest"],
    }
    actual_layers = {layer["digest"] for layer in payload["layers"]}

    if actual_layers != expected_layers:
        raise ValueError(
            "model layer set mismatch: "
            f"expected {sorted(expected_layers)}, got {sorted(actual_layers)}"
        )

    for digest in [config_digest, *sorted(actual_layers)]:
        algorithm, expected = digest.split(":", 1)
        if algorithm != "sha256":
            raise ValueError(f"unsupported digest algorithm: {algorithm}")

        blob = models_root / "blobs" / f"sha256-{expected}"
        if not blob.is_file():
            raise FileNotFoundError(f"model blob not found: {blob}")

        actual = _sha256(blob)
        print(
            f"BLOB={blob.name} SIZE={blob.stat().st_size} SHA256={actual}"
        )
        if actual != expected:
            raise ValueError(
                f"blob SHA-256 mismatch for {blob.name}: "
                f"expected {expected}, got {actual}"
            )

    print("OLLAMA_MODEL_IDENTITY=PASS")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--models-root", type=Path, required=True)
    parser.add_argument("--supply-chain", type=Path, required=True)
    args = parser.parse_args()

    verify_model(
        args.models_root.resolve(),
        args.supply_chain.resolve(),
    )


if __name__ == "__main__":
    main()
