# Installation and Deployment

[Español](INSTALL.md) | [English](INSTALL.en.md)

[Home](README.en.md) · [Project](PROJECT.en.md) · [Architecture](ARCHITECTURE.en.md)

This document describes the **Git + Docker on Linux** deployment mode.

For reproducible installation, use a specific release/tag instead of a mutable branch.

Current public release:

**[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**

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

## 9. Start and use

After bootstrap completes, follow the instructions emitted by the script.

The Docker Core runs on demand through Docker Compose.

To inspect CENTAURUS capabilities:

```bash
centaurus capabilities
```

or from the execution context defined by the installation.

Help:

```bash
centaurus --help
```

## 10. Workspace

Investigations are stored under the persistent workspace.

The logical layout is documented in [`STORAGE.en.md`](STORAGE.en.md).

Do not delete the workspace if traceability or historical results must be preserved.

## 11. Appliance credentials

These credentials apply to OVA/USB distributions, not to the Git repository.

### Standard user

```text
Username: centaurus
Password: centaurus
```

### Root

```text
Username: root
Password: root
```

Change default credentials after first use when the appliance will remain deployed.

## 12. OVA and USB

OVA and USB are external artifacts. The repository does not contain these large binaries.

### VMware OVA

The public OVA is available at:

**[CENTAURUS-C4-FINAL.ova — Google Drive](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)**

Verify its identity before importing:

```text
File=CENTAURUS-C4-FINAL.ova
SIZE_BYTES=11828618752
SHA256=d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868
```

On Linux:

```bash
sha256sum CENTAURUS-C4-FINAL.ova
```

On PowerShell:

```powershell
Get-FileHash .\CENTAURUS-C4-FINAL.ova -Algorithm SHA256
```

The calculated hash must exactly match the published value.

### USB image

The validated USB image is:

```text
File=CENTAURUS-USB.img
SIZE_BYTES=31457280000
SHA256=7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165
PUBLICATION_STATUS=PENDING
```

Its public link will be added after external publication is complete.

The Git + Docker documentation must not be interpreted as a direct USB-image materialization procedure or an OVA resealing procedure.

## 13. Windows

Native Windows can be used for development/local Core execution.

Example:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip check
```

Workspace:

```powershell
$env:CENTAURUS_WORKSPACE = "$env:USERPROFILE\CENTAURUS\workspace"
New-Item -ItemType Directory -Force $env:CENTAURUS_WORKSPACE | Out-Null
```

For local LLM functions, Ollama must be installed with the corresponding model.

Windows mode does not claim complete parity with Linux + Docker.

## 14. GPU

The functional baseline does not depend on a GPU.

Ollama may use compatible acceleration when provided by the host/runtime, but GPU support is not part of the minimum deployment contract.

## 15. Basic verification

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

## 16. Updating

To move to another version:

```bash
git fetch --tags --prune
git checkout --detach <TAG_OR_COMMIT>
```

Verify a clean tree and rerun the initialization procedure for that version.

Do not reuse identities or hashes from an older version to declare a newer one valid.

## 17. Troubleshooting

### Docker unavailable

```bash
docker info
```

It must work for the deployment user.

### Docker Compose unavailable

```bash
docker compose version
```

### Modified checkout

```bash
git status --porcelain --untracked-files=all
```

Resolve or preserve changes before running bootstrap.

### Model unavailable

Review Ollama status and the configured persistent directory. Use the versioned provisioning/verification scripts under `scripts/`.

### OSINT source failure

An upstream source can fail temporarily. CENTAURUS may preserve a partial investigation when valid knowledge exists; failures are recorded as `ExecutionFailure`.

### LLM #2 timeout

The already-persisted deterministic `Report` remains authoritative. LLM #2 assistance is fail-soft.

## 18. Security

- do not expose Ollama unnecessarily to the host or external networks;
- do not mount the Docker socket inside Core;
- protect the workspace;
- do not store secrets in Git;
- change appliance default credentials;
- review `CENTAURUS_DATA_ROOT` permissions;
- use only sources and targets for which you have legal/organizational authorization.

## 19. Related documentation

- [`README.en.md`](README.en.md)
- [`PROJECT.en.md`](PROJECT.en.md)
- [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md)
- [`SPECIFICATION.en.md`](SPECIFICATION.en.md)
- [`STORAGE.en.md`](STORAGE.en.md)
- [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)
