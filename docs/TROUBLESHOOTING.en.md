# Troubleshooting

[Español](TROUBLESHOOTING.md) | [English](TROUBLESHOOTING.en.md)

[Home](../README.en.md) · [INSTALL.en.md](INSTALL.en.md) · [USER_GUIDE.en.md](USER_GUIDE.en.md)

## 1. Identify the context

Before applying a check, identify the deployment mode and the stage where the problem occurs. On OVA/USB, `centaurus` is a zero-argument host wrapper; inside the `centaurus>` shell, use metacommands such as `/help`. In Git + Docker, Compose commands run on the deployment host. Native Windows uses the Python environment's CLI.

Keep the exact message and existing results. Administrative checks belong to the environment administrator; the appliance analyst does not need general Docker permissions to work.

## 2. OVA import and USB boot

| Symptom | Check and next step |
| --- | --- |
| Size or SHA-256 mismatch | Compare against the identity published in the deployment guide. Obtain the correct artifact again before importing or writing it. |
| VMware cannot import the OVA | Check available storage, import compatibility and preservation of the included hardware profile. |
| The image does not fit on the USB | Check actual capacity in bytes: it must be at least `31457280000`. |
| The USB does not boot | Check that the raw image was written to the whole disk and its UEFI entry is selected. Review firmware and hardware compatibility. |
| The host offers to format USB partitions | Cancel: these may be partitions the host does not recognize. |
| GPT warnings appear on reused USB media | Stop and request administrative review of the device and its metadata. Do not accept automatic repairs. |

Procedures and identities: [`DEPLOYMENT_OVA.en.md`](DEPLOYMENT_OVA.en.md) and [`DEPLOYMENT_USB.en.md`](DEPLOYMENT_USB.en.md). Verify the distribution image's hash before first use; booting changes the USB media.

## 3. Networking and appliance access

For administrative diagnosis on the OVA/USB host:

```bash
ip -br addr
ip route
findmnt /workspace
systemctl --failed --no-pager
```

The reference logical interface is `centaurus0` using DHCP. In VMware, check the E1000 adapter, its NAT connection and the environment's DHCP service. **The USB distribution requires wired Ethernet:** connect the cable and check link, a compatible NIC/driver and DHCP. No Wi-Fi driver or connection manager is deployed in the image; do not rely on Wi-Fi for networking. Validation on one computer does not guarantee compatibility with every Ethernet adapter. Avoid renaming interfaces without diagnosing the cause.

If `centaurus` fails before showing the shell, check that it runs as user `centaurus`, without arguments, from a TTY and without another active session. If the message indicates an integrity or Docker failure, retain the diagnosis and request administrative attention. Do not change manifests or grant general Docker access to bypass verification.

## 4. Git + Docker

On the deployment host, from the checkout in use:

```bash
docker info
docker compose version
git status --porcelain --untracked-files=all
```

`docker info` must work for the deployment user and Compose must be available. The last command should produce no output before bootstrap; preserve or resolve local changes and untracked files before rerunning it.

If results appear elsewhere or the workspace seems missing, check that `--env-file` selects the same bootstrap-generated `compose.env`. Do not create an alternative workspace or delete the original to resolve a path discrepancy.

See [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md) for startup and shutdown, and [`CONFIGURATION.en.md`](CONFIGURATION.en.md) for variable and path resolution.

### 4.1. Prerequisite and build failures

| Message or symptom | Likely cause and action |
| --- | --- |
| `missing prerequisite: git`, `missing prerequisite: python3` or `missing prerequisite: docker` | Install the missing host prerequisite and repeat the initial checks. |
| `Git + Docker distribution is certified on Linux only` | The host is not Linux; use the deployment mode appropriate to that system. |
| `Docker Engine is not available to the current user` | Check the service with `systemctl status docker`, then `docker info` and host access policy. |
| `Docker Compose plugin is required` | Check that the Compose plugin is installed and `docker compose version` works. |
| `release checkout must be clean before bootstrap` | Preserve or reconcile changes and untracked files; do not delete work merely to pass the check. |
| The checkout does not match `CENTAURUS_RELEASE_COMMIT` | Compare `git rev-parse HEAD` with the intended release. The variable may retain the previous release commit in the same terminal: update it to the independently verified full commit, or return to the intended checkout. Follow the update procedure in [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md); do not remove the check to hide a mismatch. |
| Downloading dependencies fails during build | Keep the error and review connectivity and pinned artifact availability. Do not treat an incomplete build as validated. |
| `pip check` fails | The candidate environment is inconsistent; do not promote or use that candidate as the new validated image. Bootstrap stops before updating the local tag. |
| Workspace write error | Check ownership, permissions and the generated host bind path. Normal Core uses `1000:1000`; bootstrap changes the workspace directory owner, not all existing files recursively. |
| `HOME` or `EROFS` error in an external tool | Check the Compose override `HOME=/tmp/centaurus` and `/tmp` tmpfs. Keep the read-only root filesystem. |
| Disk usage grows after repeated builds | Inspect `docker system df` and `docker builder du`. Plan selective cleanup while preserving images needed for rollback and persistent data; avoid indiscriminate pruning. |

## 5. Ollama, requests and results

| Situation | Interpretation and action |
| --- | --- |
| `centaurus-ollama` does not start | Inspect `docker logs --tail 50 centaurus-ollama` and `docker inspect centaurus-ollama`; check image, model and configuration. |
| Core cannot reach Ollama | Review service status and the internal LLM network in Compose. Do not publish port `11434` on the host as a diagnostic shortcut. |
| `existing Ollama state does not match the release` | Bootstrap found incompatible existing content and stops; follow section 5.1 before retrying. |
| Model unavailable | Check the Ollama service, configured URL and persistent store. In Git + Docker use the versioned verification/provisioning scripts; on the appliance request administrative diagnosis. |
| LLM error during interpretation | LLM #1 can prevent investigation startup. Keep the message and check the service/model before retrying. |
| `Invalid request` | Check the target and write a simple request using a supported type; see `/capabilities` inside the shell. |
| A source fails or returns HTTP errors | Assess coverage by reviewing the report and the separate `ExecutionFailure` artifacts in `execution/failures/` together. A valid partial result may exist; retrying does not guarantee source availability. |
| All tasks fail | The investigation fails. Isolated files do not establish that a valid report exists. |
| No findings | Review evidence and applicable rules; zero findings does not certify absence of risk. |
| LLM #2 is slow, fails or times out | Keep the already-persisted deterministic `Report`. Review logs and resources; additional assistance is non-authoritative and fail-soft. |
| A previous investigation cannot be found in the shell | The CLI has no historical query feature. Check the workspace used by the deployment. |

Local inference does not remove the need for networking when querying OSINT sources. Timeout and context settings are in [`CONFIGURATION.en.md`](CONFIGURATION.en.md); increasing them does not guarantee sufficient resources or valid responses.

On native Windows, use the virtual environment prepared in [`DEPLOYMENT_WINDOWS.en.md`](DEPLOYMENT_WINDOWS.en.md). A tool appearing in the catalog does not demonstrate that its executable or dependencies are available on Windows.

### 5.1. Existing Ollama state incompatible with the release

Git + Docker bootstrap verifies the model against `docker/supply-chain.lock.json`. If it matches, it reuses the model and prints `MODEL_ALREADY_VALID=PASS`. If the Ollama directory is empty, it provisions the required model. If the directory contains data but verification fails, it stops instead of silently deleting or overwriting that state.

From the selected release checkout, with `CENTAURUS_DATA_ROOT` set to the data directory actually used, inspect verification output:

```bash
python3 scripts/verify_ollama_model.py \
  --models-root "$CENTAURUS_DATA_ROOT/ollama/models" \
  --supply-chain docker/supply-chain.lock.json
```

Resolve the mismatch by selecting the correct data root for that release, restoring the expected model from a verified copy, or explicitly choosing a new empty data root for a separate installation. Do not delete an existing Ollama directory automatically. A separate data root does not itself isolate Compose project/container names or enable simultaneous deployments.

A model-stage failure does not mean bootstrap made no changes: the Core local tag and workspace directory ownership have already been updated at that point. Preserve the error, inspect the resulting state and use the previously recorded image identity if rollback is needed. Bootstrap provides no automatic rollback of those changes.

## 6. Native Windows

| Symptom | Check and action |
| --- | --- |
| `centaurus` is not recognized | Use `.\.venv\Scripts\centaurus.exe` or `.\.venv\Scripts\python.exe -m centaurus`. Check `Get-Command centaurus -ErrorAction SilentlyContinue` and `where.exe centaurus` if you expected it in `PATH`. |
| `centaurus.exe` is missing or module not found appears | Check `.\.venv\Scripts\python.exe -m pip show centaurus` and reinstall the package in that same environment using the Windows guide. |
| The launcher environment is unclear | Run `.\.venv\Scripts\python.exe -c "import sysconfig; print(sysconfig.get_path('scripts'))"`. Do not copy the launcher outside its environment. |
| PowerShell blocks `.venv` activation | Run `.venv\Scripts` programs directly; changing `ExecutionPolicy` is unnecessary. |
| Workspace creation fails | Set `CENTAURUS_WORKSPACE` to a Windows user path and check permissions. A variable persisted in the profile applies to new consoles. |
| `ollama list` does not show `qwen3:4b` | Download the model with `ollama pull qwen3:4b` and check the list again. |
| LLM does not respond | Check the Ollama process and `OLLAMA_BASE_URL`; the direct default is `http://localhost:11434`. |
| DOMAIN ends with partial coverage | Review `ExecutionFailure` and availability of `dnsrecon`, `sublist3r` and `theHarvester`, as well as upstream failures. Do not mix their locks into Core. |
| LLM #2 is slow or fails | Use the persisted report and check resources and configuration; having a GPU does not itself solve context or validation problems. |

Procedure: [`DEPLOYMENT_WINDOWS.en.md`](DEPLOYMENT_WINDOWS.en.md). Capability inspection is static and does not establish tool parity with Docker.

## 7. Experimental GPU on Linux + Docker

These checks belong to the experimental variant in [`GPU_OLLAMA_DOCKER.en.md`](GPU_OLLAMA_DOCKER.en.md); they do not imply certified GPU support in OVA/USB.

| Symptom | Check and action |
| --- | --- |
| `nvidia-smi` fails on the host | Resolve compatibility and driver issues before changing CENTAURUS. |
| The host sees NVIDIA but a test container does not | Review NVIDIA Container Toolkit and Docker runtime configuration. Plan the effect of any Docker restart on other services. |
| Docker reserves a GPU but Ollama uses CPU | Check logs, pinned-image compatibility with GPU/driver and actual utilization during inference. A reservation does not establish acceleration. |
| `/dev/kfd` is absent for ROCm | Check the driver and host compatibility before applying the AMD profile. |
| ROCm reports permission denied | Review device access and groups; do not add `privileged` as a solution. |
| The ROCm image does not match the CPU identity | These are different images. The variant needs its own supply-chain identity and validation; do not skip bootstrap checks to declare it valid. |
| GPU runs out of memory | Review load, model, context and VRAM. Validate any parameter changes and avoid hiding the problem with automatic retries. |
| CPU fallback after suspend or reboot | Revalidate accelerator detection and consult provider guidance for that version. |
| Rerunning bootstrap disables the variant | The script only uses base Compose. After completing and verifying CPU deployment, evaluate the local overlay again using the GPU guide. |
| GPU works but the investigation fails | Separate inference, Core and source failures; retain diagnostic information and any existing deterministic report. |

## 8. Logs and diagnostic information

On OVA/USB, the operational log is `/workspace/logs/centaurus.log`. In Git + Docker it is under the selected persistent directory. On the host, with `CENTAURUS_DATA_ROOT` set to the path used for bootstrap:

```bash
tail -n 50 "$CENTAURUS_DATA_ROOT/workspace/logs/centaurus.log"
docker logs --tail 50 centaurus-ollama
```

Core creates its log when the application initializes. If it is absent, check the path, permissions and whether failure occurred before initialization. Source errors and investigation artifacts are stored separately as described in [`STORAGE.en.md`](STORAGE.en.md).

When reporting an issue, include deployment mode, version or artifact identity, stage, exact message and investigation identifier if one exists. Attach only the necessary excerpts and review targets, personal data and any sensitive information before sharing. Back up results before maintenance.

On native Windows, with `CENTAURUS_WORKSPACE` set in the current PowerShell session:

```powershell
Get-Content "$env:CENTAURUS_WORKSPACE\logs\centaurus.log" -Tail 100
```

For temporary additional detail, set `$env:CENTAURUS_LOG_LEVEL = "DEBUG"` before starting Core and restore `$env:CENTAURUS_LOG_LEVEL = "INFO"` afterward. Review log contents before sharing them.
