#!/bin/bash
set -Eeuo pipefail
IFS=$' \t\n'
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
unset BASH_ENV ENV CDPATH SUDO_ASKPASS SUDO_PROMPT

# Incremental C4-PRIV-2 installer.  It is intentionally separate from the
# C4-PRIV-1 runtime-broker installer and accepts only the already-certified
# C4-PRIV-1 appliance baseline as its prerequisite.

readonly ANALYST_USER="centaurus"
readonly ANALYST_UID="1000"
readonly EXPECTED_SUDO_VERSION="1.9.16p2-3+deb13u2"
readonly SOURCE_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
readonly COMMAND_SOURCE="${SOURCE_DIR}/centaurus_poweroff_command.sh"
readonly HELPER_SOURCE="${SOURCE_DIR}/centaurus_poweroff_helper.sh"
readonly SOURCE_MANIFEST="${SOURCE_DIR}/MANIFEST_SHA256.txt"
readonly COMMAND_TARGET="/usr/local/bin/centaurus-poweroff"
readonly HELPER_TARGET="/usr/local/libexec/centaurus-poweroff"
readonly SUDOERS_TARGET="/etc/sudoers.d/centaurus-poweroff"
readonly CONFIG_DIR="/etc/centaurus"
readonly MANIFEST="${CONFIG_DIR}/poweroff-helper.manifest"
readonly RUNTIME_COMMAND="/usr/local/bin/centaurus"
readonly RUNTIME_BROKER="/usr/local/libexec/centaurus-runtime"
readonly RUNTIME_SUDOERS="/etc/sudoers.d/centaurus-runtime"
readonly RUNTIME_MANIFEST="${CONFIG_DIR}/runtime-broker.manifest"
readonly EXPECTED_RUNTIME_COMMAND_SHA256="f717407c525704a57acd99963a8a51a7208a063de4e66c5378e7f04d2794b070"
readonly EXPECTED_RUNTIME_BROKER_SHA256="0dbc75b58d743427e9f1edc8219636a2ddfa7b52ce1c3b461f7714ed18978ccd"

fail() {
    echo "ERROR: $*" >&2
    exit 1
}

file_sha256() {
    /usr/bin/sha256sum "$1" | /usr/bin/awk '{print $1}'
}

require_exact_mode() {
    local path="$1"
    local expected="$2"
    [[ -e "$path" ]] || fail "required path is missing: $path"
    [[ ! -L "$path" ]] || fail "security-sensitive path must not be a symlink: $path"
    [[ "$(/usr/bin/stat -Lc '%U:%G %a' "$path")" == "$expected" ]] || \
        fail "unexpected ownership/mode for $path"
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

[[ -x /usr/bin/sudo ]] || fail "sudo is missing from the C4-PRIV-1 prerequisite"
[[ -x /usr/sbin/visudo ]] || fail "visudo is unavailable"
sudo_version="$(/usr/bin/dpkg-query -W -f='${Version}' sudo 2>/dev/null)" || fail "cannot resolve sudo version"
[[ "$sudo_version" == "$EXPECTED_SUDO_VERSION" ]] || fail "unexpected installed sudo version: $sudo_version"

# Reconcile the exact C4-PRIV-1 privilege boundary before adding a second,
# independent command.  This installer never repairs or rewrites that boundary.
require_exact_mode "$RUNTIME_COMMAND" "root:root 755"
require_exact_mode "$RUNTIME_BROKER" "root:root 755"
require_exact_mode "$RUNTIME_SUDOERS" "root:root 440"
require_exact_mode "$RUNTIME_MANIFEST" "root:root 644"
[[ "$(file_sha256 "$RUNTIME_COMMAND")" == "$EXPECTED_RUNTIME_COMMAND_SHA256" ]] || \
    fail "C4-PRIV-1 host command identity mismatch"
[[ "$(file_sha256 "$RUNTIME_BROKER")" == "$EXPECTED_RUNTIME_BROKER_SHA256" ]] || \
    fail "C4-PRIV-1 runtime broker identity mismatch"
/usr/bin/grep -Fq "PASSWD: sha256:${EXPECTED_RUNTIME_BROKER_SHA256} ${RUNTIME_BROKER} \"\"" "$RUNTIME_SUDOERS" || \
    fail "C4-PRIV-1 runtime sudoers rule mismatch"
if /usr/bin/grep -Ev '^[[:space:]]*#' "$RUNTIME_SUDOERS" | /usr/bin/grep -Fq 'NOPASSWD:'; then
    fail "unexpected NOPASSWD in C4-PRIV-1 runtime policy"
fi
/usr/sbin/visudo -c >/dev/null || fail "existing sudoers configuration is invalid"

[[ -f "$COMMAND_SOURCE" ]] || fail "poweroff command source is missing"
[[ -f "$HELPER_SOURCE" ]] || fail "poweroff helper source is missing"
[[ -f "$SOURCE_MANIFEST" ]] || fail "bundle manifest is missing"
(
    cd "$SOURCE_DIR"
    /usr/bin/sha256sum -c MANIFEST_SHA256.txt
)
/bin/bash -n "$COMMAND_SOURCE"
/bin/bash -n "$HELPER_SOURCE"

# C4-PRIV-2 is an additive installation on the certified C4-PRIV-1 source.  Any
# pre-existing target is an unexpected state and therefore a hard NO-GO.
for path in "$COMMAND_TARGET" "$HELPER_TARGET" "$SUDOERS_TARGET" "$MANIFEST"; do
    [[ ! -e "$path" ]] || fail "C4-PRIV-2 target already exists: $path"
done

/usr/bin/install -d -o root -g root -m 0755 /usr/local/libexec
/usr/bin/install -d -o root -g root -m 0755 "$CONFIG_DIR"
/usr/bin/install -o root -g root -m 0755 "$COMMAND_SOURCE" "$COMMAND_TARGET"
/usr/bin/install -o root -g root -m 0755 "$HELPER_SOURCE" "$HELPER_TARGET"

command_sha="$(file_sha256 "$COMMAND_TARGET")"
helper_sha="$(file_sha256 "$HELPER_TARGET")"

cat >"$SUDOERS_TARGET" <<EOF2
# CENTAURUS C4-PRIV-2 authenticated minimal poweroff.
# No NOPASSWD. No arguments. No generic systemctl, shell, reboot or halt access.
Defaults:${ANALYST_USER} timestamp_timeout=0
Defaults:${ANALYST_USER} use_pty
Defaults:${ANALYST_USER} requiretty
Defaults:${ANALYST_USER} env_reset
Defaults:${ANALYST_USER} !setenv
Defaults:${ANALYST_USER} !rootpw, !targetpw, !runaspw
Defaults:${ANALYST_USER} secure_path="/usr/sbin:/usr/bin:/sbin:/bin"
${ANALYST_USER} ALL=(root) PASSWD: sha256:${helper_sha} ${HELPER_TARGET} ""
EOF2
chown root:root "$SUDOERS_TARGET"
chmod 0440 "$SUDOERS_TARGET"
/usr/sbin/visudo -cf "$SUDOERS_TARGET"
/usr/sbin/visudo -c >/dev/null

cat >"$MANIFEST" <<EOF2
CENTAURUS_POWEROFF_HELPER_VERSION=1
SUDO_PACKAGE_VERSION=${sudo_version}
COMMAND_PATH=${COMMAND_TARGET}
COMMAND_SHA256=${command_sha}
HELPER_PATH=${HELPER_TARGET}
HELPER_SHA256=${helper_sha}
SUDOERS_PATH=${SUDOERS_TARGET}
AUTHENTICATION=PASSWD
SUDO_TIMESTAMP_TIMEOUT=0
ANALYST_DOCKER_GROUP=NO
ANALYST_SUDO_GROUP=NO
HELPER_ARGUMENTS=ZERO
GENERIC_SYSTEMCTL_ACCESS=NO
ROOT_SHELL_GRANTED=NO
REBOOT_GRANTED=NO
HALT_GRANTED=NO
EOF2
chown root:root "$MANIFEST"
chmod 0644 "$MANIFEST"

require_exact_mode "$COMMAND_TARGET" "root:root 755"
require_exact_mode "$HELPER_TARGET" "root:root 755"
require_exact_mode "$SUDOERS_TARGET" "root:root 440"
require_exact_mode "$MANIFEST" "root:root 644"

if /usr/bin/grep -Ev '^[[:space:]]*#' "$SUDOERS_TARGET" | /usr/bin/grep -Fq 'NOPASSWD:'; then
    fail "unexpected NOPASSWD poweroff policy"
fi

for forbidden_group in docker sudo; do
    if /usr/bin/id -nG "$ANALYST_USER" | /usr/bin/tr ' ' '\n' | /usr/bin/grep -Fxq "$forbidden_group"; then
        fail "centaurus unexpectedly acquired $forbidden_group group membership"
    fi
done

sudo_list="$(LC_ALL=C /usr/bin/sudo -l -U "$ANALYST_USER")" || fail "cannot enumerate centaurus sudo policy"
printf '%s\n' "$sudo_list" | /usr/bin/grep -Fq "$RUNTIME_BROKER" || fail "runtime broker missing from sudo -l"
printf '%s\n' "$sudo_list" | /usr/bin/grep -Fq "$HELPER_TARGET" || fail "poweroff helper missing from sudo -l"
if printf '%s\n' "$sudo_list" | /usr/bin/grep -Fq '/usr/bin/systemctl'; then
    fail "generic systemctl unexpectedly exposed in sudo -l"
fi
if printf '%s\n' "$sudo_list" | /usr/bin/grep -Fq 'NOPASSWD:'; then
    fail "NOPASSWD unexpectedly exposed in sudo -l"
fi

printf '%s\n' \
    "CENTAURUS_C4_PRIV2_POWEROFF_INSTALL=PASS" \
    "SUDO_PACKAGE_VERSION=${sudo_version}" \
    "POWEROFF_COMMAND_SHA256=${command_sha}" \
    "POWEROFF_HELPER_SHA256=${helper_sha}" \
    "AUTHENTICATION=PASSWD" \
    "SUDO_TIMESTAMP_TIMEOUT=0" \
    "ANALYST_DOCKER_GROUP=NO" \
    "ANALYST_SUDO_GROUP=NO" \
    "HELPER_ARGUMENTS=ZERO" \
    "GENERIC_SYSTEMCTL_ACCESS=NO" \
    "ROOT_SHELL_GRANTED=NO" \
    "REBOOT_GRANTED=NO" \
    "HALT_GRANTED=NO"
