#!/bin/bash
set -Eeuo pipefail
IFS=$' \t\n'
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
unset BASH_ENV ENV CDPATH SUDO_ASKPASS SUDO_PROMPT
unset DOCKER_HOST DOCKER_CONTEXT DOCKER_CONFIG DOCKER_CERT_PATH DOCKER_TLS_VERIFY
unset COMPOSE_FILE COMPOSE_PROJECT_NAME COMPOSE_PROFILES COMPOSE_PATH_SEPARATOR
unset COMPOSE_ENV_FILES COMPOSE_PARALLEL_LIMIT COMPOSE_IGNORE_ORPHANS

# Privileged OVA runtime broker.
# Security contract:
#   * root-owned and digest-pinned in sudoers;
#   * zero command-line arguments;
#   * callable through sudo only by the centaurus analyst account;
#   * never starts/stops the Docker daemon;
#   * never consumes analyst-controlled Docker/Compose environment variables;
#   * executes one fixed Compose service from one fixed, hash-pinned definition;
#   * requires the exact Core image identity recorded at broker installation.

readonly ANALYST_USER="centaurus"
readonly ANALYST_UID="1000"
readonly DOCKER="/usr/bin/docker"
readonly SYSTEMCTL="/usr/bin/systemctl"
readonly ENV_BIN="/usr/bin/env"
readonly FLOCK="/usr/bin/flock"
readonly SHA256SUM="/usr/bin/sha256sum"
readonly AWK="/usr/bin/awk"
readonly DOCKER_HOST_URI="unix:///var/run/docker.sock"
readonly DOCKER_CONFIG_DIR="/etc/centaurus/docker-cli"
readonly COMPOSE_DIR="/opt/osint-framework/centaurus/docker"
readonly COMPOSE_FILE="${COMPOSE_DIR}/compose.yml"
readonly COMPOSE_ENV="/etc/centaurus/compose.env"
readonly RUNTIME_MANIFEST="/etc/centaurus/runtime-broker.manifest"
readonly CORE_IMAGE="centaurus-core:local"
readonly LOCK_FILE="/run/centaurus-runtime.lock"

fail() {
    echo "ERROR: $*" >&2
    exit 69
}

require_root_owned_not_writable() {
    local path="$1"
    local uid mode mode_octal

    [[ -e "$path" ]] || fail "required path is missing: $path"
    [[ ! -L "$path" ]] || fail "security-sensitive path must not be a symlink: $path"

    uid="$(/usr/bin/stat -Lc '%u' "$path")"
    mode="$(/usr/bin/stat -Lc '%a' "$path")"
    mode_octal=$((8#$mode))

    [[ "$uid" == "0" ]] || fail "security-sensitive path is not root-owned: $path"
    (( (mode_octal & 8#022) == 0 )) || \
        fail "security-sensitive path is writable by group/other: $path mode=$mode"
}

manifest_value() {
    local key="$1"
    "$AWK" -F= -v wanted="$key" '
        $1 == wanted {
            sub(/^[^=]*=/, "")
            print
            found = 1
            exit
        }
        END {
            if (!found) exit 1
        }
    ' "$RUNTIME_MANIFEST"
}

file_sha256() {
    "$SHA256SUM" "$1" | "$AWK" '{print $1}'
}

docker_local() {
    "$ENV_BIN" -i \
        HOME=/root \
        PATH=/usr/sbin:/usr/bin:/sbin:/bin \
        LANG=C.UTF-8 \
        DOCKER_CONFIG="$DOCKER_CONFIG_DIR" \
        "$DOCKER" -H "$DOCKER_HOST_URI" "$@"
}

[[ "$#" -eq 0 ]] || fail "runtime broker accepts no command-line arguments"
[[ "$EUID" -eq 0 ]] || fail "runtime broker must execute as root"
[[ "${SUDO_USER:-}" == "$ANALYST_USER" ]] || fail "runtime broker requires sudo analyst identity"
[[ "${SUDO_UID:-}" == "$ANALYST_UID" ]] || fail "unexpected sudo analyst uid"
[[ -t 0 && -t 1 ]] || fail "interactive terminal required"

[[ -x "$DOCKER" ]] || fail "Docker CLI is unavailable at $DOCKER"
[[ -x "$SYSTEMCTL" ]] || fail "systemctl is unavailable at $SYSTEMCTL"
[[ -x "$ENV_BIN" ]] || fail "env is unavailable at $ENV_BIN"
[[ -x "$FLOCK" ]] || fail "flock is unavailable at $FLOCK"
[[ -x "$SHA256SUM" ]] || fail "sha256sum is unavailable at $SHA256SUM"
[[ -x "$AWK" ]] || fail "awk is unavailable at $AWK"

# Only one analyst runtime may be active at a time.  This protects bounded host
# resources and avoids concurrent writers against the same workspace.
exec 9>"$LOCK_FILE"
"$FLOCK" -n 9 || fail "another CENTAURUS runtime session is already active"

# The ordinary analyst must never acquire generic Docker authority.
if /usr/bin/id -nG "$ANALYST_USER" | /usr/bin/tr ' ' '\n' | /usr/bin/grep -Fxq docker; then
    fail "centaurus must not belong to the docker group"
fi

[[ -S /var/run/docker.sock ]] || fail "Docker socket is unavailable"
[[ "$(/usr/bin/stat -Lc '%U:%G' /var/run/docker.sock)" == "root:docker" ]] || \
    fail "unexpected Docker socket ownership"
[[ "$(/usr/bin/stat -Lc '%a' /var/run/docker.sock)" == "660" ]] || \
    fail "unexpected Docker socket permissions"

# Fail closed when platform administration is required.  The analyst is not
# granted an indirect systemctl capability.
"$SYSTEMCTL" is-active --quiet docker || \
    fail "Docker daemon is not active; administrator intervention is required"

# Every input consumed by root-level Compose is part of the privilege boundary.
for path in \
    /opt \
    /opt/osint-framework \
    /opt/osint-framework/centaurus \
    "$COMPOSE_DIR" \
    "$COMPOSE_FILE" \
    /etc \
    /etc/centaurus \
    "$DOCKER_CONFIG_DIR" \
    "$COMPOSE_ENV" \
    "$RUNTIME_MANIFEST"
do
    require_root_owned_not_writable "$path"
done

[[ ! -e "${COMPOSE_DIR}/.env" ]] || \
    fail "implicit Compose .env files are forbidden in the appliance runtime"

# The broker only executes the deployment inputs that were sealed during its
# installation.  Any later platform/image change requires an explicit admin
# reconciliation instead of silently expanding analyst authority.
expected_compose_path="$(manifest_value COMPOSE_FILE_PATH)" || fail "manifest lacks COMPOSE_FILE_PATH"
expected_compose_sha="$(manifest_value COMPOSE_FILE_SHA256)" || fail "manifest lacks COMPOSE_FILE_SHA256"
expected_env_sha="$(manifest_value COMPOSE_ENV_SHA256)" || fail "manifest lacks COMPOSE_ENV_SHA256"
expected_image="$(manifest_value CORE_IMAGE)" || fail "manifest lacks CORE_IMAGE"
expected_image_id="$(manifest_value CORE_IMAGE_ID)" || fail "manifest lacks CORE_IMAGE_ID"

[[ "$expected_compose_path" == "$COMPOSE_FILE" ]] || fail "manifest compose path mismatch"
[[ "$expected_image" == "$CORE_IMAGE" ]] || fail "manifest Core image name mismatch"
[[ "$(file_sha256 "$COMPOSE_FILE")" == "$expected_compose_sha" ]] || \
    fail "Compose definition changed after broker installation"
[[ "$(file_sha256 "$COMPOSE_ENV")" == "$expected_env_sha" ]] || \
    fail "Compose environment changed after broker installation"

core_user="$(docker_local image inspect "$CORE_IMAGE" --format '{{.Config.User}}' 2>/dev/null)" || \
    fail "required Core image is unavailable: $CORE_IMAGE"
core_image_id="$(docker_local image inspect "$CORE_IMAGE" --format '{{.Id}}' 2>/dev/null)" || \
    fail "cannot resolve Core image identity"
[[ "$core_user" == "1000:1000" ]] || \
    fail "Core image runtime identity is not 1000:1000"
[[ "$core_image_id" == "$expected_image_id" ]] || \
    fail "Core image changed after broker installation"

running_core="$(docker_local ps --quiet --filter label=com.docker.compose.service=centaurus-core)"
[[ -z "$running_core" ]] || \
    fail "a CENTAURUS Core container is already running; administrator review is required"

# A clean environment plus an explicit local Docker endpoint prevents
# DOCKER_HOST, DOCKER_CONTEXT, COMPOSE_FILE, COMPOSE_PROFILES and similar
# analyst-controlled values from crossing the privilege boundary.
exec "$ENV_BIN" -i \
    HOME=/root \
    PATH=/usr/sbin:/usr/bin:/sbin:/bin \
    LANG=C.UTF-8 \
    DOCKER_CONFIG="$DOCKER_CONFIG_DIR" \
    "$DOCKER" -H "$DOCKER_HOST_URI" compose \
        --project-directory "$COMPOSE_DIR" \
        --file "$COMPOSE_FILE" \
        --env-file "$COMPOSE_ENV" \
        --profile framework \
        run --rm centaurus-core
