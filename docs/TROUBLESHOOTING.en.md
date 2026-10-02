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

The reference logical interface is `centaurus0` using DHCP. In VMware, check the E1000 adapter, its NAT connection and the environment's DHCP service. On USB, check the NIC and driver; validation on one computer does not guarantee universal compatibility. Avoid renaming interfaces without diagnosing the cause.

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

## 5. Ollama, requests and results

| Situation | Interpretation and action |
| --- | --- |
| Model unavailable | Check the Ollama service, configured URL and persistent store. In Git + Docker use the versioned verification/provisioning scripts; on the appliance request administrative diagnosis. |
| LLM error during interpretation | LLM #1 can prevent investigation startup. Keep the message and check the service/model before retrying. |
| `Invalid request` | Check the target and write a simple request using a supported type; see `/capabilities` inside the shell. |
| A source fails or returns HTTP errors | Review `ExecutionFailure` and report coverage. A valid partial result may exist; retrying does not guarantee source availability. |
| All tasks fail | The investigation fails. Isolated files do not establish that a valid report exists. |
| No findings | Review evidence and applicable rules; zero findings does not certify absence of risk. |
| LLM #2 is slow, fails or times out | Keep the already-persisted deterministic `Report`. Review logs and resources; additional assistance is non-authoritative and fail-soft. |
| A previous investigation cannot be found in the shell | The CLI has no historical query feature. Check the workspace used by the deployment. |

Local inference does not remove the need for networking when querying OSINT sources. Timeout and context settings are in [`CONFIGURATION.en.md`](CONFIGURATION.en.md); increasing them does not guarantee sufficient resources or valid responses.

On native Windows, use the virtual environment prepared in [`DEPLOYMENT_WINDOWS.en.md`](DEPLOYMENT_WINDOWS.en.md). A tool appearing in the catalog does not demonstrate that its executable or dependencies are available on Windows.

## 6. Logs and diagnostic information

On OVA/USB, the operational log is `/workspace/logs/centaurus.log`. In Git + Docker it is under the selected persistent directory. On the host, with `CENTAURUS_DATA_ROOT` set to the path used for bootstrap:

```bash
tail -n 50 "$CENTAURUS_DATA_ROOT/workspace/logs/centaurus.log"
docker logs --tail 50 centaurus-ollama
```

Core creates its log when the application initializes. If it is absent, check the path, permissions and whether failure occurred before initialization. Source errors and investigation artifacts are stored separately as described in [`STORAGE.en.md`](STORAGE.en.md).

When reporting an issue, include deployment mode, version or artifact identity, stage, exact message and investigation identifier if one exists. Attach only the necessary excerpts and review targets, personal data and any sensitive information before sharing. Back up results before maintenance.
