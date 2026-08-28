#!/bin/bash
set -Eeuo pipefail
IFS=$' \t\n'
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
export HOME=/root
unset BASH_ENV ENV CDPATH SUDO_ASKPASS SUDO_PROMPT

# C4-PRIV-2 privileged appliance poweroff helper.
# Security contract:
#   * root-owned and SHA-256 digest-pinned in sudoers;
#   * zero command-line arguments;
#   * callable through sudo only by the centaurus analyst account;
#   * requires an interactive terminal;
#   * exposes exactly one fixed host-administration action: systemctl poweroff.

readonly ANALYST_USER="centaurus"
readonly ANALYST_UID="1000"
readonly SYSTEMCTL="/usr/bin/systemctl"

fail() {
    echo "ERROR: $*" >&2
    exit 69
}

[[ "$#" -eq 0 ]] || fail "poweroff helper accepts no command-line arguments"
[[ "$EUID" -eq 0 ]] || fail "poweroff helper must execute as root"
[[ "${SUDO_USER:-}" == "$ANALYST_USER" ]] || fail "poweroff helper requires sudo analyst identity"
[[ "${SUDO_UID:-}" == "$ANALYST_UID" ]] || fail "unexpected sudo analyst uid"
[[ -t 0 && -t 1 ]] || fail "interactive terminal required"
[[ -x "$SYSTEMCTL" ]] || fail "systemctl is unavailable at $SYSTEMCTL"

# The analyst must remain outside generic privilege-bearing groups.  A future
# change to this invariant requires a separate security decision, not silent use
# of this helper as a compatibility path.
for forbidden_group in docker sudo; do
    if /usr/bin/id -nG "$ANALYST_USER" | /usr/bin/tr ' ' '\n' | /usr/bin/grep -Fxq "$forbidden_group"; then
        fail "centaurus must not belong to the $forbidden_group group"
    fi
done

# No user-controlled command, option or service name crosses this boundary.
exec "$SYSTEMCTL" poweroff
