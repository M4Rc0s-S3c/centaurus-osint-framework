# Git + Docker Deployment on Linux

[Español](DEPLOYMENT_GIT_DOCKER.md) | [English](DEPLOYMENT_GIT_DOCKER.en.md)

[Home](../README.en.md) · [INSTALL.en.md](INSTALL.en.md) · [USER_GUIDE.en.md](USER_GUIDE.en.md)

This guide covers deployment from source on a Linux host. The prebuilt OVA is the main CENTAURUS distribution; see [`INSTALL.en.md`](INSTALL.en.md) to choose a deployment mode.

Use a specific release/tag for a reproducible deployment. Public release: [v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0).

## 1. Requirements

Linux host with:

- Git;
- Python 3;
- Docker Engine;
- Docker Compose (`docker compose`);
- Docker access for the deployment user;
- Internet access during first provisioning when images, dependencies or the LLM model must be downloaded;
- sufficient space for images, cache, model and workspace.

The formal Git + Docker mode targets Linux.

Native Windows can be used for development and local Core execution, but it is not presented as equivalent to the complete Linux + Docker distribution.

## 2. Deployment architecture

```text
LINUX HOST
│
├── CENTAURUS Git checkout
│   ├── docker/
│   ├── requirements-*.lock
│   └── scripts/bootstrap_linux_release.sh
│
├── CENTAURUS_DATA_ROOT
│   ├── compose.env
│   ├── compose.rendered.yml
│   ├── ollama/
│   └── workspace/
│
└── Docker Engine
    ├── centaurus-ollama
    └── centaurus-core:local
```

Principles:

- `centaurus-core` contains the framework and integrated tools;
- `centaurus-ollama` provides the local LLM;
- the Core runs on demand;
- the Ollama model persists outside the application image;
- the workspace persists outside the container;
- Ollama does not need to expose its port to the host in normal deployment.

## 3. Obtain the code

```bash
git clone https://github.com/M4Rc0s-S3c/centaurus-osint-framework.git
cd centaurus-osint-framework
```

Refresh references:

```bash
git fetch --tags --prune
```

To deploy the current public release:

```bash
git checkout --detach v1.0.0
```

Verify:

```bash
git rev-parse HEAD
git status --porcelain --untracked-files=all
```

The second command should produce no output.

You may also set the expected commit explicitly:

```bash
export CENTAURUS_RELEASE_COMMIT="$(git rev-parse HEAD)"
```

`CENTAURUS_RELEASE_COMMIT` acts as an identity assertion for initialization.

## 4. What not to do

```text
NO → run bootstrap with local changes
NO → run bootstrap with untracked files
NO → use a moving branch as the only release identity
NO → store Git credentials in the repository
NO → copy .git into the Core image
```

## 5. Persistent directory

If no other location is defined, bootstrap uses the data directory expected by the script.

To set it explicitly:

```bash
export CENTAURUS_DATA_ROOT="$HOME/.local/share/centaurus"
```

On a server:

```bash
export CENTAURUS_DATA_ROOT="/srv/centaurus"
```

The directory is used for:

```text
$CENTAURUS_DATA_ROOT/
├── compose.env
├── compose.rendered.yml
├── ollama/
└── workspace/
```

Do not use as `CENTAURUS_DATA_ROOT` a shared folder containing unrelated data without reviewing permissions/ownership first.

## 6. Official initialization

With a clean checkout:

```bash
./scripts/bootstrap_linux_release.sh
```

Bootstrap performs host/Git checks, prepares the persistent root, builds the Core image, validates dependencies, provisions/verifies Ollama and performs runtime checks.

Do not replace it with a manual `docker compose up` when trying to reproduce the documented mode.

## 7. Supply chain

The repository includes dependency locks and a supply chain under `docker/`.

Builds should use the versions/digests pinned by the selected release.

Tool environments requiring incompatible dependencies are isolated inside the execution image.

## 8. Ollama model

Model used:

```text
qwen3:4b
```

The model is stored persistently outside the application container.

Initialization verifies/provisions the model using versioned scripts and supply-chain definitions.

## 9. Startup, use and shutdown

Run these commands on the Linux host, from the checkout used for bootstrap. Use the exact data directory selected in step 5. Prepare the paths in each new terminal; replace the example value if you selected another location:

```bash
export CENTAURUS_DATA_ROOT="$HOME/.local/share/centaurus"
CENTAURUS_ENV_FILE="$CENTAURUS_DATA_ROOT/compose.env"
```

Before continuing, check that `CENTAURUS_ENV_FILE` points to the bootstrap-generated file. Do not use an empty file or omit `--env-file`: Compose defaults may point to a different workspace.

Open an interactive Core session:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework run --rm centaurus-core
```

The default command opens `centaurus shell`. Follow [`USER_GUIDE.en.md`](USER_GUIDE.en.md) to use and exit the session. Core is removed on exit; the host workspace persists.

To inspect capabilities and help without starting an investigation or dependencies:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework run -T --rm --no-deps centaurus-core centaurus capabilities --rules
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework run -T --rm --no-deps centaurus-core centaurus --help
```

Run one session at a time. To stop the deployment, exit all Core sessions first, then run:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework down
```

Host persistent directories are not deleted. To restart the LLM service:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml up -d centaurus-ollama
```

Then open another Core session using the earlier command. If the service has just started, wait for it to become available before using LLM functions.

For operational logs and diagnosis, see [`TROUBLESHOOTING.en.md`](TROUBLESHOOTING.en.md). Supported settings are in [`CONFIGURATION.en.md`](CONFIGURATION.en.md).

## 10. Workspace

Investigations are stored under the persistent workspace.

The logical layout is documented in [`STORAGE.en.md`](STORAGE.en.md).

Do not delete the workspace if traceability or historical results must be preserved.

Before maintenance or version changes, stop investigations and the deployment. Back up the host `workspace/` and `compose.env`; retain `ollama/` too if you need to restore without downloading the model again. Keep the release/commit identity with the backup and preserve permissions and ownership when restoring.

## 11. GPU

The functional baseline does not depend on a GPU.

Ollama may use compatible acceleration when provided by the host/runtime, but GPU support is not part of the minimum deployment contract.

## 12. Basic verification

After installation, check:

```bash
git status --porcelain --untracked-files=all
docker info
docker compose version
```

and run the bootstrap-provided checks/smoke tests.

For development:

```bash
python -m pytest
```

## 13. Updating

To move to another version:

```bash
git fetch --tags --prune
git checkout --detach <TAG_OR_COMMIT>
```

Verify a clean tree and rerun the initialization procedure for that version.

Do not reuse identities or hashes from an older version to declare a newer one valid.

## 14. Related documentation

- [`TROUBLESHOOTING.en.md`](TROUBLESHOOTING.en.md)
- [`CONFIGURATION.en.md`](CONFIGURATION.en.md)
- [`STORAGE.en.md`](STORAGE.en.md)
- [`SECURITY_ARCHITECTURE.en.md`](SECURITY_ARCHITECTURE.en.md)
- [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)
