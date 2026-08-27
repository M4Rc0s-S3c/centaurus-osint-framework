from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOST_COMMAND = (ROOT / "scripts/centaurus_host_command.sh").read_text(encoding="utf-8")
BROKER = (ROOT / "scripts/centaurus_runtime_broker.sh").read_text(encoding="utf-8")
INSTALLER = (ROOT / "scripts/install_ova_runtime_broker.sh").read_text(encoding="utf-8")
BOOTSTRAP = (ROOT / "scripts/bootstrap_linux_release.sh").read_text(encoding="utf-8")


def test_host_entrypoint_is_manual_authenticated_and_zero_argument() -> None:
    assert 'if [[ "$#" -ne 0 ]]' in HOST_COMMAND
    assert '"$SUDO" -k' in HOST_COMMAND
    assert 'exec "$SUDO" -u root -- "$RUNTIME_BROKER"' in HOST_COMMAND
    assert "NOPASSWD" not in HOST_COMMAND
    assert "profile.d" not in HOST_COMMAND
    assert "autostart" not in HOST_COMMAND.lower()


def test_privileged_broker_accepts_no_arguments_or_user_docker_environment() -> None:
    assert '[[ "$#" -eq 0 ]]' in BROKER
    assert '[[ "${SUDO_USER:-}" == "$ANALYST_USER" ]]' in BROKER
    assert '[[ "${SUDO_UID:-}" == "$ANALYST_UID" ]]' in BROKER
    assert '"$ENV_BIN" -i' in BROKER
    assert "DOCKER_HOST" in BROKER
    assert 'readonly DOCKER_HOST_URI="unix:///var/run/docker.sock"' in BROKER
    assert '"$DOCKER" -H "$DOCKER_HOST_URI"' in BROKER
    assert "DOCKER_CONTEXT" in BROKER
    assert "COMPOSE_FILE" in BROKER
    assert "COMPOSE_PROFILES" in BROKER
    assert "eval " not in BROKER
    assert "bash -c" not in BROKER
    assert "sh -c" not in BROKER
    assert 'readonly LOCK_FILE="/run/centaurus-runtime.lock"' in BROKER
    assert '"$FLOCK" -n 9' in BROKER
    assert "another CENTAURUS runtime session is already active" in BROKER


def test_privileged_broker_does_not_manage_docker_daemon_or_grant_generic_docker_access() -> None:
    assert '"$SYSTEMCTL" is-active --quiet docker' in BROKER
    assert "systemctl start" not in BROKER
    assert "systemctl restart" not in BROKER
    assert "systemctl enable" not in BROKER
    assert "usermod" not in BROKER
    assert "gpasswd" not in BROKER
    assert "/var/run/docker.sock:" not in BROKER
    assert '/usr/bin/grep -Fxq docker' in BROKER


def test_privileged_broker_uses_fixed_root_controlled_compose_inputs() -> None:
    assert 'readonly COMPOSE_DIR="/opt/osint-framework/centaurus/docker"' in BROKER
    assert 'readonly COMPOSE_FILE="${COMPOSE_DIR}/compose.yml"' in BROKER
    assert 'readonly COMPOSE_ENV="/etc/centaurus/compose.env"' in BROKER
    assert 'readonly RUNTIME_MANIFEST="/etc/centaurus/runtime-broker.manifest"' in BROKER
    assert "COMPOSE_FILE_SHA256" in BROKER
    assert "COMPOSE_ENV_SHA256" in BROKER
    assert "CORE_IMAGE_ID" in BROKER
    assert "Compose definition changed after broker installation" in BROKER
    assert "Core image changed after broker installation" in BROKER
    assert 'require_root_owned_not_writable "$COMPOSE_FILE"' not in BROKER
    assert 'require_root_owned_not_writable "$path"' in BROKER
    assert '[[ ! -e "${COMPOSE_DIR}/.env" ]]' in BROKER
    assert '--project-directory "$COMPOSE_DIR"' in BROKER
    assert '--file "$COMPOSE_FILE"' in BROKER
    assert '--env-file "$COMPOSE_ENV"' in BROKER
    assert 'run --rm centaurus-core' in BROKER
    assert '"1000:1000"' in BROKER


def test_installer_creates_password_required_digest_pinned_sudoers_rule() -> None:
    assert 'EXPECTED_SUDO_VERSION="1.9.16p2-3+deb13u2"' in INSTALLER
    assert 'EXPECTED_COMPOSE_SHA256="4cf550272796af58449759630dcb7793e847fa116083cb05322e7ee6e5c6989c"' in INSTALLER
    assert "CORE_IMAGE_ID=${core_image_id}" in INSTALLER
    assert 'apt-cache policy sudo' in INSTALLER
    assert '"sudo=${EXPECTED_SUDO_VERSION}"' in INSTALLER
    assert 'timestamp_timeout=0' in INSTALLER
    assert 'use_pty' in INSTALLER
    assert 'requiretty' in INSTALLER
    assert 'env_reset' in INSTALLER
    assert '!setenv' in INSTALLER
    assert '!rootpw, !targetpw, !runaspw' in INSTALLER
    assert 'secure_path="/usr/sbin:/usr/bin:/sbin:/bin"' in INSTALLER
    assert 'PASSWD: sha256:${broker_sha} ${BROKER_TARGET} ""' in INSTALLER
    policy_line = '${ANALYST_USER} ALL=(root) PASSWD: sha256:${broker_sha} ${BROKER_TARGET} ""'
    assert policy_line in INSTALLER
    assert 'NOPASSWD: sha256:${broker_sha}' not in INSTALLER
    assert 'chmod 0440 "$SUDOERS_TARGET"' in INSTALLER
    assert '/usr/sbin/visudo -cf "$SUDOERS_TARGET"' in INSTALLER
    assert 'readonly PLATFORM_INPUT_DIR="/opt/osint-framework/centaurus"' in INSTALLER
    assert 'readonly COMPOSE_DIR="${PLATFORM_INPUT_DIR}/docker"' in INSTALLER
    assert 'harden_platform_input_dir "$PLATFORM_INPUT_DIR"' in INSTALLER
    assert 'harden_platform_input_dir "$COMPOSE_DIR"' in INSTALLER
    assert '/usr/bin/chmod 0755 "$path"' in INSTALLER
    assert 'unexpected platform input directory mode' in INSTALLER
    assert 'TRUST_PATH_HARDENING=YES' in INSTALLER


def test_installer_never_adds_analyst_to_docker_or_sudo_groups() -> None:
    assert "usermod" not in INSTALLER
    assert "gpasswd" not in INSTALLER
    assert 'for forbidden_group in docker sudo' in INSTALLER
    assert 'ANALYST_DOCKER_GROUP=NO' in INSTALLER
    assert 'NOPASSWD=NO' in INSTALLER
    assert 'AUTORUN=NO' in INSTALLER


def test_g2_bootstrap_remains_free_of_ova_privilege_installation() -> None:
    assert "install_ova_runtime_broker" not in BOOTSTRAP
    assert "centaurus_runtime_broker" not in BOOTSTRAP
    assert "apt-get install" not in BOOTSTRAP
    assert "sudoers" not in BOOTSTRAP


def test_ova_broker_bundle_is_deterministic_and_manifested(tmp_path: Path) -> None:
    import hashlib
    from zipfile import ZipFile

    from scripts.create_ova_runtime_broker_bundle import create_bundle

    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    create_bundle(ROOT, first)
    create_bundle(ROOT, second)

    assert first.read_bytes() == second.read_bytes()

    with ZipFile(first) as archive:
        names = archive.namelist()
        assert names == [
            "centaurus_host_command.sh",
            "centaurus_runtime_broker.sh",
            "install_ova_runtime_broker.sh",
            "MANIFEST_SHA256.txt",
        ]
        manifest = archive.read("MANIFEST_SHA256.txt").decode("ascii")
        for name in names[:-1]:
            digest = hashlib.sha256(archive.read(name)).hexdigest()
            assert f"{digest}  {name}\n" in manifest


def test_ova_broker_bundle_uses_canonical_cross_platform_zip_metadata(tmp_path: Path) -> None:
    from zipfile import ZIP_STORED, ZipFile

    from scripts.create_ova_runtime_broker_bundle import create_bundle

    bundle = tmp_path / "broker.zip"
    create_bundle(ROOT, bundle)

    with ZipFile(bundle) as archive:
        for info in archive.infolist():
            assert info.compress_type == ZIP_STORED
            assert info.create_system == 0
            assert info.date_time == (2026, 8, 26, 0, 0, 0)
            assert info.extra == b""
            assert info.comment == b""
