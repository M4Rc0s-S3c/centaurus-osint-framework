#!/bin/bash
set -Eeuo pipefail
IFS=$' \t\n'
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
unset BASH_ENV ENV CDPATH

# Install the authenticated, least-privilege CENTAURUS runtime broker into a
# C4 OVA development source.  This script is appliance-specific: G2 Git+Docker
# bootstrap must never invoke it.

readonly ANALYST_USER="centaurus"
readonly ANALYST_UID="1000"
readonly EXPECTED_SUDO_VERSION="1.9.16p2-3+deb13u2"
readonly SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly HOST_COMMAND_SOURCE="${SOURCE_DIR}/centaurus_host_command.sh"
readonly BROKER_SOURCE="${SOURCE_DIR}/centaurus_runtime_broker.sh"
readonly SOURCE_MANIFEST="${SOURCE_DIR}/MANIFEST_SHA256.txt"
readonly HOST_COMMAND_TARGET="/usr/local/bin/centaurus"
readonly BROKER_TARGET="/usr/local/libexec/centaurus-runtime"
readonly SUDOERS_TARGET="/etc/sudoers.d/centaurus-runtime"
readonly CONFIG_DIR="/etc/centaurus"
readonly COMPOSE_ENV="${CONFIG_DIR}/compose.env"
readonly DOCKER_CONFIG_DIR="${CONFIG_DIR}/docker-cli"
readonly MANIFEST="${CONFIG_DIR}/runtime-broker.manifest"
readonly CORE_IMAGE="centaurus-core:local"
readonly PLATFORM_INPUT_DIR="/opt/osint-framework/centaurus"
readonly COMPOSE_DIR="${PLATFORM_INPUT_DIR}/docker"
readonly COMPOSE_FILE="${COMPOSE_DIR}/compose.yml"
readonly EXPECTED_COMPOSE_SHA256="4cf550272796af58449759630dcb7793e847fa116083cb05322e7ee6e5c6989c"

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

# C3 used root:root 0775 on the two Compose parent directories.  That state did
# not give the centaurus account effective write access, but C4 deliberately
# removes the redundant group-write bit before these paths become inputs to a
# root-level broker.  Only the two known C3 modes (0755/0775) are accepted; an
# unexpected permission state fails closed instead of being silently repaired.
harden_platform_input_dir() {
    local path="$1"
    local owner group mode

    [[ -d "$path" ]] || fail "required platform input directory is missing: $path"
    [[ ! -L "$path" ]] || fail "platform input directory must not be a symlink: $path"

    owner="$(/usr/bin/stat -Lc '%U' "$path")"
    group="$(/usr/bin/stat -Lc '%G' "$path")"
    mode="$(/usr/bin/stat -Lc '%a' "$path")"

    [[ "$owner" == "root" ]] || fail "platform input directory is not root-owned: $path"
    [[ "$group" == "root" ]] || fail "platform input directory group is not root: $path"

    case "$mode" in
        755)
            ;;
        775)
            /usr/bin/chmod 0755 "$path"
            ;;
        *)
            fail "unexpected platform input directory mode: $path mode=$mode"
            ;;
    esac

    [[ "$(/usr/bin/stat -Lc '%U:%G %a' "$path")" == "root:root 755" ]] || \
        fail "platform input directory hardening failed: $path"
}

[[ "$EUID" -eq 0 ]] || fail "installer must run as root"
[[ "$#" -eq 0 ]] || fail "installer accepts no command-line arguments"

/usr/bin/getent passwd "$ANALYST_USER" >/dev/null || fail "centaurus user is missing"
[[ "$(/usr/bin/id -u "$ANALYST_USER")" == "$ANALYST_UID" ]] || fail "unexpected centaurus uid"

for forbidden_group in docker sudo; do
    if /usr/bin/id -nG "$ANALYST_USER" | /usr/bin/tr ' ' '\n' | /usr/bin/grep -Fxq "$forbidden_group"; then
        fail "centaurus must not belong to the $forbidden_group group"
    fi
done

[[ -f "$HOST_COMMAND_SOURCE" ]] || fail "host command source is missing"
[[ -f "$BROKER_SOURCE" ]] || fail "runtime broker source is missing"
[[ -f "$SOURCE_MANIFEST" ]] || fail "bundle manifest is missing"
(
    cd "$SOURCE_DIR"
    /usr/bin/sha256sum -c MANIFEST_SHA256.txt
)
/bin/bash -n "$HOST_COMMAND_SOURCE"
/bin/bash -n "$BROKER_SOURCE"

[[ -f "$COMPOSE_FILE" ]] || \
    fail "certified appliance Compose file is missing"
compose_sha="$(/usr/bin/sha256sum "$COMPOSE_FILE" | /usr/bin/awk '{print $1}')"
[[ "$compose_sha" == "$EXPECTED_COMPOSE_SHA256" ]] || \
    fail "unexpected appliance Compose SHA-256: $compose_sha"
[[ "$(/usr/bin/stat -Lc '%U:%G %a' "$COMPOSE_FILE")" == "root:root 644" ]] || \
    fail "unexpected appliance Compose ownership/mode"

# Materialize the stricter C4 trust-path invariant reproducibly.
harden_platform_input_dir "$PLATFORM_INPUT_DIR"
harden_platform_input_dir "$COMPOSE_DIR"

[[ -x /usr/bin/docker ]] || fail "Docker CLI is missing"
/usr/bin/docker compose version >/dev/null
/usr/bin/systemctl is-active --quiet docker || fail "Docker daemon must already be active"

# The C3 baseline deliberately has no sudo.  C4 changes that decision only to
# replace routine full-root shells with one authenticated, zero-argument broker.
if /usr/bin/dpkg-query -W -f='${Status}' sudo 2>/dev/null | /usr/bin/grep -Fq 'install ok installed'; then
    fail "sudo is already installed; baseline is not the expected C3 source state"
fi

export DEBIAN_FRONTEND=noninteractive
/usr/bin/apt-get update

sudo_candidate="$(
    /usr/bin/apt-cache policy sudo |
        /usr/bin/awk '/Candidate:/ {print $2; exit}'
)"
[[ "$sudo_candidate" == "$EXPECTED_SUDO_VERSION" ]] || \
    fail "unexpected sudo candidate version: ${sudo_candidate:-NONE}"

/usr/bin/apt-get install --yes --no-install-recommends "sudo=${EXPECTED_SUDO_VERSION}"

[[ -x /usr/bin/sudo ]] || fail "sudo installation failed"
[[ -x /usr/sbin/visudo ]] || fail "visudo is unavailable after sudo installation"

/usr/bin/install -d -o root -g root -m 0755 /usr/local/libexec
/usr/bin/install -d -o root -g root -m 0755 "$CONFIG_DIR"
/usr/bin/install -d -o root -g root -m 0755 "$DOCKER_CONFIG_DIR"
/usr/bin/install -o root -g root -m 0755 "$HOST_COMMAND_SOURCE" "$HOST_COMMAND_TARGET"
/usr/bin/install -o root -g root -m 0755 "$BROKER_SOURCE" "$BROKER_TARGET"

cat >"$COMPOSE_ENV" <<'ENVEOF'
CENTAURUS_OLLAMA_HOST_DIR=/opt/osint-framework/runtime/ollama
CENTAURUS_WORKSPACE_HOST_DIR=/workspace
ENVEOF
chown root:root "$COMPOSE_ENV"
chmod 0644 "$COMPOSE_ENV"

broker_sha="$(/usr/bin/sha256sum "$BROKER_TARGET" | /usr/bin/awk '{print $1}')"
host_sha="$(/usr/bin/sha256sum "$HOST_COMMAND_TARGET" | /usr/bin/awk '{print $1}')"
compose_env_sha="$(/usr/bin/sha256sum "$COMPOSE_ENV" | /usr/bin/awk '{print $1}')"
core_user="$(/usr/bin/env -i HOME=/root PATH=/usr/sbin:/usr/bin:/sbin:/bin DOCKER_CONFIG="$DOCKER_CONFIG_DIR" /usr/bin/docker -H unix:///var/run/docker.sock image inspect "$CORE_IMAGE" --format '{{.Config.User}}')" || fail "Core image is unavailable"
core_image_id="$(/usr/bin/env -i HOME=/root PATH=/usr/sbin:/usr/bin:/sbin:/bin DOCKER_CONFIG="$DOCKER_CONFIG_DIR" /usr/bin/docker -H unix:///var/run/docker.sock image inspect "$CORE_IMAGE" --format '{{.Id}}')" || fail "Core image identity is unavailable"
[[ "$core_user" == "1000:1000" ]] || fail "Core image runtime identity is not 1000:1000"
sudo_version="$(/usr/bin/dpkg-query -W -f='${Version}' sudo)"
[[ "$sudo_version" == "$EXPECTED_SUDO_VERSION" ]] || fail "installed sudo version mismatch"

cat >"$SUDOERS_TARGET" <<EOF2
# CENTAURUS C4 authenticated runtime broker.
# No NOPASSWD.  No arbitrary arguments.  No generic Docker/systemctl access.
Defaults:${ANALYST_USER} timestamp_timeout=0
Defaults:${ANALYST_USER} use_pty
Defaults:${ANALYST_USER} requiretty
Defaults:${ANALYST_USER} env_reset
Defaults:${ANALYST_USER} !setenv
Defaults:${ANALYST_USER} !rootpw, !targetpw, !runaspw
Defaults:${ANALYST_USER} secure_path="/usr/sbin:/usr/bin:/sbin:/bin"
${ANALYST_USER} ALL=(root) PASSWD: sha256:${broker_sha} ${BROKER_TARGET} ""
EOF2
chown root:root "$SUDOERS_TARGET"
chmod 0440 "$SUDOERS_TARGET"
/usr/sbin/visudo -cf "$SUDOERS_TARGET"

cat >"$MANIFEST" <<EOF2
CENTAURUS_RUNTIME_BROKER_VERSION=1
SUDO_PACKAGE_VERSION=${sudo_version}
HOST_COMMAND_PATH=${HOST_COMMAND_TARGET}
HOST_COMMAND_SHA256=${host_sha}
BROKER_PATH=${BROKER_TARGET}
BROKER_SHA256=${broker_sha}
SUDOERS_PATH=${SUDOERS_TARGET}
COMPOSE_FILE_PATH=${COMPOSE_FILE}
COMPOSE_FILE_SHA256=${compose_sha}
COMPOSE_ENV_SHA256=${compose_env_sha}
CORE_IMAGE=${CORE_IMAGE}
CORE_IMAGE_ID=${core_image_id}
AUTORUN=NO
NOPASSWD=NO
ANALYST_DOCKER_GROUP=NO
BROKER_ARGUMENTS=ZERO
DOCKER_DAEMON_MANAGEMENT=NO
TRUST_PATH_HARDENING=YES
EOF2
chown root:root "$MANIFEST"
chmod 0644 "$MANIFEST"

# Post-install policy checks.  These do not authenticate as the analyst and do
# not start CENTAURUS; they only verify the installed privilege boundary.
[[ "$(stat -Lc '%U:%G %a' "$HOST_COMMAND_TARGET")" == "root:root 755" ]] || fail "bad host command ownership/mode"
[[ "$(stat -Lc '%U:%G %a' "$BROKER_TARGET")" == "root:root 755" ]] || fail "bad broker ownership/mode"
[[ "$(stat -Lc '%U:%G %a' "$SUDOERS_TARGET")" == "root:root 440" ]] || fail "bad sudoers ownership/mode"
[[ "$(stat -Lc '%U:%G %a' "$COMPOSE_ENV")" == "root:root 644" ]] || fail "bad compose env ownership/mode"
[[ "$(stat -Lc '%U:%G %a' "$PLATFORM_INPUT_DIR")" == "root:root 755" ]] || fail "bad platform input directory ownership/mode"
[[ "$(stat -Lc '%U:%G %a' "$COMPOSE_DIR")" == "root:root 755" ]] || fail "bad Compose directory ownership/mode"

if /usr/bin/grep -Ev '^[[:space:]]*#' "$SUDOERS_TARGET" | /usr/bin/grep -Fq 'NOPASSWD:'; then
    fail "unexpected NOPASSWD policy"
fi

if /usr/bin/id -nG "$ANALYST_USER" | /usr/bin/tr ' ' '\n' | /usr/bin/grep -Fxq docker; then
    fail "centaurus unexpectedly acquired docker group membership"
fi

if /usr/bin/id -nG "$ANALYST_USER" | /usr/bin/tr ' ' '\n' | /usr/bin/grep -Fxq sudo; then
    fail "centaurus unexpectedly acquired sudo group membership"
fi

printf '%s\n' \
    "CENTAURUS_C4_RUNTIME_BROKER_INSTALL=PASS" \
    "SUDO_PACKAGE_VERSION=${sudo_version}" \
    "HOST_COMMAND_SHA256=${host_sha}" \
    "BROKER_SHA256=${broker_sha}" \
    "COMPOSE_FILE_SHA256=${compose_sha}" \
    "CORE_IMAGE_ID=${core_image_id}" \
    "AUTORUN=NO" \
    "NOPASSWD=NO" \
    "ANALYST_DOCKER_GROUP=NO" \
    "BROKER_ARGUMENTS=ZERO" \
    "DOCKER_DAEMON_MANAGEMENT=NO" \
    "TRUST_PATH_HARDENING=YES"
