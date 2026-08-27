#!/bin/bash
set -Eeuo pipefail
IFS=$' \t\n'
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
unset BASH_ENV ENV CDPATH SUDO_ASKPASS SUDO_PROMPT

# Host-side analyst entrypoint for the CENTAURUS OVA.
# This wrapper intentionally exposes one operation only: open the interactive
# CENTAURUS runtime. Product commands remain inside the CENTAURUS shell.

readonly RUNTIME_BROKER="/usr/local/libexec/centaurus-runtime"
readonly SUDO="/usr/bin/sudo"

if [[ "$#" -ne 0 ]]; then
    printf '%s\n' \
        "Usage: centaurus" \
        "Run capabilities and rules from inside the CENTAURUS shell." >&2
    exit 64
fi

if [[ "$(/usr/bin/id -un)" != "centaurus" ]]; then
    echo "ERROR: this command is reserved for the centaurus analyst account." >&2
    exit 77
fi

if [[ ! -t 0 || ! -t 1 ]]; then
    echo "ERROR: CENTAURUS requires an interactive terminal." >&2
    exit 69
fi

if [[ ! -x "$SUDO" ]]; then
    echo "ERROR: authenticated CENTAURUS runtime broker is not installed." >&2
    exit 69
fi

# Invalidate any cached sudo timestamp before every launch.  Combined with
# timestamp_timeout=0 in sudoers, every new CENTAURUS session requires an
# explicit analyst authentication.
"$SUDO" -k
exec "$SUDO" -u root -- "$RUNTIME_BROKER"
