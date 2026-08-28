from __future__ import annotations

import hashlib
import importlib.util
import re
from pathlib import Path
from zipfile import ZipFile


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
COMMAND_PATH = SCRIPTS / "centaurus_poweroff_command.sh"
HELPER_PATH = SCRIPTS / "centaurus_poweroff_helper.sh"
INSTALLER_PATH = SCRIPTS / "install_ova_poweroff_helper.sh"
GENERATOR_PATH = SCRIPTS / "create_ova_poweroff_bundle.py"

COMMAND = COMMAND_PATH.read_text(encoding="utf-8")
HELPER = HELPER_PATH.read_text(encoding="utf-8")
INSTALLER = INSTALLER_PATH.read_text(encoding="utf-8")
GENERATOR = GENERATOR_PATH.read_text(encoding="utf-8")


def _load_generator():
    spec = importlib.util.spec_from_file_location("centaurus_poweroff_bundle", GENERATOR_PATH)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_poweroff_wrapper_is_authenticated_zero_argument_and_tty_only() -> None:
    assert 'if [[ "$#" -ne 0 ]]' in COMMAND
    assert '"$SUDO" -k' in COMMAND
    assert 'exec "$SUDO" -u root -- "$POWEROFF_HELPER"' in COMMAND
    assert 'readonly POWEROFF_HELPER="/usr/local/libexec/centaurus-poweroff"' in COMMAND
    assert '$(/usr/bin/id -un)' in COMMAND
    assert '!= "centaurus"' in COMMAND
    assert '[[ ! -t 0 || ! -t 1 ]]' in COMMAND
    assert "NOPASSWD" not in COMMAND
    assert "/usr/bin/systemctl" not in COMMAND


def test_privileged_helper_exposes_only_fixed_poweroff() -> None:
    assert '[[ "$#" -eq 0 ]]' in HELPER
    assert '[[ "$EUID" -eq 0 ]]' in HELPER
    assert '[[ "${SUDO_USER:-}" == "$ANALYST_USER" ]]' in HELPER
    assert '[[ "${SUDO_UID:-}" == "$ANALYST_UID" ]]' in HELPER
    assert '[[ -t 0 && -t 1 ]]' in HELPER
    assert 'readonly SYSTEMCTL="/usr/bin/systemctl"' in HELPER
    assert 'exec "$SYSTEMCTL" poweroff' in HELPER
    assert '"$@"' not in HELPER
    assert "eval " not in HELPER
    assert "bash -c" not in HELPER
    assert "sh -c" not in HELPER
    assert " systemctl reboot" not in HELPER
    assert " systemctl halt" not in HELPER
    assert " shutdown" not in HELPER


def test_helper_preserves_forbidden_group_invariants() -> None:
    assert "for forbidden_group in docker sudo" in HELPER
    assert "usermod" not in HELPER
    assert "gpasswd" not in HELPER
    assert "groupadd" not in HELPER


def test_installer_requires_exact_c4_priv1_prerequisite() -> None:
    assert 'readonly RUNTIME_COMMAND="/usr/local/bin/centaurus"' in INSTALLER
    assert 'readonly RUNTIME_BROKER="/usr/local/libexec/centaurus-runtime"' in INSTALLER
    assert 'readonly RUNTIME_SUDOERS="/etc/sudoers.d/centaurus-runtime"' in INSTALLER
    assert 'EXPECTED_RUNTIME_COMMAND_SHA256="f717407c525704a57acd99963a8a51a7208a063de4e66c5378e7f04d2794b070"' in INSTALLER
    assert 'EXPECTED_RUNTIME_BROKER_SHA256="0dbc75b58d743427e9f1edc8219636a2ddfa7b52ce1c3b461f7714ed18978ccd"' in INSTALLER
    assert "C4-PRIV-1 runtime broker identity mismatch" in INSTALLER
    assert "existing sudoers configuration is invalid" in INSTALLER


def test_installer_materializes_dedicated_digest_pinned_sudo_rule() -> None:
    assert 'readonly COMMAND_TARGET="/usr/local/bin/centaurus-poweroff"' in INSTALLER
    assert 'readonly HELPER_TARGET="/usr/local/libexec/centaurus-poweroff"' in INSTALLER
    assert 'readonly SUDOERS_TARGET="/etc/sudoers.d/centaurus-poweroff"' in INSTALLER
    assert 'PASSWD: sha256:${helper_sha} ${HELPER_TARGET} ""' in INSTALLER
    assert 'Defaults:${ANALYST_USER} timestamp_timeout=0' in INSTALLER
    assert 'Defaults:${ANALYST_USER} use_pty' in INSTALLER
    assert 'Defaults:${ANALYST_USER} requiretty' in INSTALLER
    assert 'Defaults:${ANALYST_USER} env_reset' in INSTALLER
    assert 'Defaults:${ANALYST_USER} !setenv' in INSTALLER
    assert 'chmod 0440 "$SUDOERS_TARGET"' in INSTALLER
    assert '/usr/sbin/visudo -cf "$SUDOERS_TARGET"' in INSTALLER
    assert "NOPASSWD: sha256:${helper_sha}" not in INSTALLER


def test_installer_does_not_grant_generic_system_or_group_authority() -> None:
    assert "usermod" not in INSTALLER
    assert "gpasswd" not in INSTALLER
    assert "groupadd" not in INSTALLER
    assert "/usr/bin/systemctl poweroff" not in INSTALLER
    assert "/usr/bin/systemctl reboot" not in INSTALLER
    assert "sudo -s" not in INSTALLER
    assert "sudo -i" not in INSTALLER
    assert "GENERIC_SYSTEMCTL_ACCESS=NO" in INSTALLER
    assert "ROOT_SHELL_GRANTED=NO" in INSTALLER
    assert "REBOOT_GRANTED=NO" in INSTALLER
    assert "HALT_GRANTED=NO" in INSTALLER


def test_installer_is_additive_and_does_not_rewrite_c4_priv1_policy() -> None:
    assert "Incremental C4-PRIV-2 installer" in INSTALLER
    assert '[[ ! -e "$path" ]]' in INSTALLER
    assert "runtime-broker.manifest" in INSTALLER
    assert "cat >\"$RUNTIME_SUDOERS\"" not in INSTALLER
    assert "install_ova_runtime_broker.sh" not in INSTALLER
    assert "/usr/bin/docker" not in INSTALLER


def test_bundle_generator_is_separate_and_deterministic(tmp_path: Path) -> None:
    module = _load_generator()
    destination_a = tmp_path / "a.zip"
    destination_b = tmp_path / "b.zip"
    module.create_bundle(ROOT, destination_a)
    module.create_bundle(ROOT, destination_b)
    assert destination_a.read_bytes() == destination_b.read_bytes()

    with ZipFile(destination_a) as archive:
        assert archive.namelist() == [
            "centaurus_poweroff_command.sh",
            "centaurus_poweroff_helper.sh",
            "install_ova_poweroff_helper.sh",
            "MANIFEST_SHA256.txt",
        ]
        assert all(info.date_time == (2026, 8, 28, 0, 0, 0) for info in archive.infolist())
        manifest = archive.read("MANIFEST_SHA256.txt").decode("ascii")
        for source_name in (
            "centaurus_poweroff_command.sh",
            "centaurus_poweroff_helper.sh",
            "install_ova_poweroff_helper.sh",
        ):
            data = (SCRIPTS / source_name).read_bytes()
            assert f"{hashlib.sha256(data).hexdigest()}  {source_name}\n" in manifest


PRIVATE_IPV4_PATTERN = (
    r"(?i)\b(?:10\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3}"
    r"|192\.168\.\d{1,3}\.\d{1,3})\b"
)

LOCAL_OR_EPHEMERAL_PATTERNS = (
    r"(?i)\b[A-Z]:[\\/]",
    PRIVATE_IPV4_PATTERN,
    r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b",
    r"\b20\d{6}T\d{6}Z-[0-9a-f]{8,}\b",
    r"(?i)\b[A-Z0-9_.-]*(?:TEST[-_ ]?FIXTURE|VALIDATION[-_ ]?VM)[A-Z0-9_.-]*\b",
    r"(?i)BEGIN (?:OPENSSH|RSA|EC) PRIVATE KEY",
    r"(?i)(?:api[_-]?key|token|password)\s*=\s*['\"][^'\"]+['\"]",
)


def test_bundle_does_not_absorb_runtime_broker_or_local_release_factory() -> None:
    assert '"centaurus_runtime_broker.sh"' not in GENERATOR
    assert '"install_ova_runtime_broker.sh"' not in GENERATOR
    assert "TFM-SCRIPT" not in GENERATOR
    assert "validation_vm" not in GENERATOR
    assert re.search(PRIVATE_IPV4_PATTERN, GENERATOR) is None


def test_new_sources_contain_no_local_machine_or_ephemeral_release_identifiers() -> None:
    combined = "\n".join((COMMAND, HELPER, INSTALLER, GENERATOR))
    for pattern in LOCAL_OR_EPHEMERAL_PATTERNS:
        assert re.search(pattern, combined) is None
