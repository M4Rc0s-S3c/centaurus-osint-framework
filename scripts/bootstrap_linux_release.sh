#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

for command in git python3 docker; do
    command -v "$command" >/dev/null 2>&1 || fail "missing prerequisite: $command"
done

[ "$(uname -s)" = "Linux" ] || fail "Git + Docker distribution is certified on Linux only"

docker info >/dev/null 2>&1 || fail "Docker Engine is not available to the current user"
docker compose version >/dev/null 2>&1 || fail "Docker Compose plugin is required"

if [ -n "$(git status --porcelain --untracked-files=all)" ]; then
    fail "release checkout must be clean before bootstrap"
fi

COMMIT="$(git rev-parse HEAD)"
if [ -n "${CENTAURUS_RELEASE_COMMIT:-}" ] && [ "$COMMIT" != "$CENTAURUS_RELEASE_COMMIT" ]; then
    fail "checkout $COMMIT does not match CENTAURUS_RELEASE_COMMIT=$CENTAURUS_RELEASE_COMMIT"
fi

DATA_ROOT="${CENTAURUS_DATA_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/centaurus}"
case "$DATA_ROOT" in
    *$'\n'*|*$'\r'*) fail "CENTAURUS_DATA_ROOT contains a newline" ;;
esac

OLLAMA_DIR="$DATA_ROOT/ollama"
WORKSPACE_DIR="$DATA_ROOT/workspace"
ENV_FILE="$DATA_ROOT/compose.env"
SUPPLY_CHAIN="$ROOT/docker/supply-chain.lock.json"
CANDIDATE_IMAGE="centaurus-core:g2-candidate"
STABLE_IMAGE="centaurus-core:local"
BOOTSTRAP_CONTAINER="centaurus-ollama-bootstrap"

mkdir -p "$OLLAMA_DIR" "$WORKSPACE_DIR"

readarray -t SUPPLY_VALUES < <(
    python3 - "$SUPPLY_CHAIN" <<'PY'
import json
import sys
from pathlib import Path

data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
print(data["images"]["ollama"]["human_reference"] + "@" + data["images"]["ollama"]["digest"])
print(data["model"]["name"])
print(data["images"]["python_base"]["digest"])
PY
)

OLLAMA_IMAGE="${SUPPLY_VALUES[0]}"
MODEL_NAME="${SUPPLY_VALUES[1]}"
PYTHON_BASE_DIGEST="${SUPPLY_VALUES[2]}"

printf 'CENTAURUS_OLLAMA_HOST_DIR=%s\nCENTAURUS_WORKSPACE_HOST_DIR=%s\n' \
    "$OLLAMA_DIR" "$WORKSPACE_DIR" > "$ENV_FILE"
chmod 0600 "$ENV_FILE"

BUNDLE="$ROOT/dist/centaurus-core-build_v1.0.zip"
python3 "$ROOT/scripts/create_core_build_bundle.py"
BUNDLE_SHA256="$(sha256sum "$BUNDLE" | awk '{print $1}')"

echo "RELEASE_COMMIT=$COMMIT"
echo "DATA_ROOT=$DATA_ROOT"
echo "OLLAMA_IMAGE=$OLLAMA_IMAGE"
echo "MODEL_NAME=$MODEL_NAME"
echo "PYTHON_BASE_DIGEST=$PYTHON_BASE_DIGEST"
echo "CORE_BUILD_BUNDLE_SHA256=$BUNDLE_SHA256"

BUILD_DIR="$(mktemp -d)"
cleanup() {
    docker rm -f "$BOOTSTRAP_CONTAINER" >/dev/null 2>&1 || true
    rm -rf "$BUILD_DIR"
}
trap cleanup EXIT

python3 - "$BUNDLE" "$BUILD_DIR" <<'PY'
import sys
from pathlib import Path
from zipfile import ZipFile

archive = Path(sys.argv[1])
destination = Path(sys.argv[2]).resolve()
with ZipFile(archive) as z:
    for member in z.infolist():
        target = (destination / member.filename).resolve()
        if target != destination and destination not in target.parents:
            raise SystemExit(f"unsafe archive path: {member.filename}")
    z.extractall(destination)
PY

docker build \
    --no-cache \
    --progress=plain \
    --tag "$CANDIDATE_IMAGE" \
    "$BUILD_DIR"

docker run --rm --network none --entrypoint python "$CANDIDATE_IMAGE" -m pip check
docker run --rm --network none --entrypoint /opt/centaurus-tools/dnsrecon/bin/python "$CANDIDATE_IMAGE" -m pip check
docker run --rm --network none --entrypoint /opt/centaurus-tools/sublist3r/bin/python "$CANDIDATE_IMAGE" -m pip check
docker run --rm --network none --entrypoint /opt/centaurus-tools/theharvester/bin/python "$CANDIDATE_IMAGE" -m pip check

docker tag "$CANDIDATE_IMAGE" "$STABLE_IMAGE"

docker run --rm \
    --user 0:0 \
    -v "$WORKSPACE_DIR:/workspace" \
    --entrypoint chown \
    "$STABLE_IMAGE" \
    1000:1000 /workspace

if python3 "$ROOT/scripts/verify_ollama_model.py" \
    --models-root "$OLLAMA_DIR/models" \
    --supply-chain "$SUPPLY_CHAIN" \
    >/dev/null 2>&1; then
    echo "MODEL_ALREADY_VALID=PASS"
else
    if [ -n "$(find "$OLLAMA_DIR" -mindepth 1 -print -quit 2>/dev/null)" ]; then
        fail "existing Ollama state does not match the release; choose an empty CENTAURUS_DATA_ROOT or restore the expected model"
    fi

    docker pull "$OLLAMA_IMAGE"
    docker rm -f "$BOOTSTRAP_CONTAINER" >/dev/null 2>&1 || true
    docker run -d \
        --name "$BOOTSTRAP_CONTAINER" \
        -e OLLAMA_NO_CLOUD=1 \
        -v "$OLLAMA_DIR:/root/.ollama" \
        "$OLLAMA_IMAGE" \
        serve >/dev/null

    READY=0
    for _ in $(seq 1 60); do
        if docker exec "$BOOTSTRAP_CONTAINER" ollama list >/dev/null 2>&1; then
            READY=1
            break
        fi
        sleep 1
    done
    [ "$READY" -eq 1 ] || fail "Ollama bootstrap service did not become ready"

    docker exec "$BOOTSTRAP_CONTAINER" ollama pull "$MODEL_NAME"
    docker rm -f "$BOOTSTRAP_CONTAINER" >/dev/null

    python3 "$ROOT/scripts/verify_ollama_model.py" \
        --models-root "$OLLAMA_DIR/models" \
        --supply-chain "$SUPPLY_CHAIN"
fi

docker compose \
    --env-file "$ENV_FILE" \
    -f "$ROOT/docker/compose.yml" \
    --profile framework \
    config > "$DATA_ROOT/compose.rendered.yml"

docker compose \
    --env-file "$ENV_FILE" \
    -f "$ROOT/docker/compose.yml" \
    up -d --force-recreate centaurus-ollama

OLLAMA_EFFECTIVE_IMAGE="$(docker inspect centaurus-ollama --format '{{.Image}}')"
OLLAMA_CONFIG_IMAGE="$(docker inspect centaurus-ollama --format '{{.Config.Image}}')"
EXPECTED_OLLAMA_ID="${OLLAMA_IMAGE##*@}"

[ "$OLLAMA_EFFECTIVE_IMAGE" = "$EXPECTED_OLLAMA_ID" ] || fail "Ollama image ID mismatch"
[ "$OLLAMA_CONFIG_IMAGE" = "$OLLAMA_IMAGE" ] || fail "Ollama config image is not digest-pinned"

docker compose \
    --env-file "$ENV_FILE" \
    -f "$ROOT/docker/compose.yml" \
    --profile framework \
    run -T --rm --no-deps centaurus-core \
    centaurus capabilities >/dev/null

echo "CORE_IMAGE_ID=$(docker image inspect "$STABLE_IMAGE" --format '{{.Id}}')"
echo "OLLAMA_IMAGE_ID=$OLLAMA_EFFECTIVE_IMAGE"
echo "OLLAMA_CONFIG_IMAGE=$OLLAMA_CONFIG_IMAGE"
echo "CENTAURUS_ENV_FILE=$ENV_FILE"
echo "LINUX_BOOTSTRAP=PASS"
