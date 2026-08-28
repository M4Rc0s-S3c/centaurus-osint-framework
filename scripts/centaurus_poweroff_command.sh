#!/bin/bash
set -Eeuo pipefail
IFS=$' \t\n'
umask 077
export PATH=/usr/sbin:/usr/bin:/sbin:/bin
unset BASH_ENV ENV CDPATH SUDO_ASKPASS SUDO_PROMPT

# Host-side, least-privilege shutdown entrypoint for the CENTAURUS appliance.
# It intentionally exposes one operation only: authenticated clean poweroff.

readonly POWEROFF_HELPER="/usr/local/libexec/centaurus-poweroff"
readonly SUDO="/usr/bin/sudo"

if [[ "$#" -ne 0 ]]; then
    printf '%s\n' \
        "Usage: centaurus-poweroff" \
        "This command only performs an authenticated clean appliance poweroff." >&2
    exit 64
fi

if [[ "$(/usr/bin/id -un)" != "centaurus" ]]; then
    echo "ERROR: this command is reserved for the centaurus analyst account." >&2
    exit 77
fi

if [[ ! -t 0 || ! -t 1 ]]; then
    echo "ERROR: centaurus-poweroff requires an interactive terminal." >&2
    exit 69
fi

if [[ ! -x "$SUDO" ]]; then
    echo "ERROR: authenticated appliance poweroff helper is not installed." >&2
    exit 69
fi

# Never reuse an earlier sudo authentication.  Together with the sudoers
# timestamp_timeout=0 contract, every poweroff requires explicit authentication.
"$SUDO" -k
exec "$SUDO" -u root -- "$POWEROFF_HELPER"
