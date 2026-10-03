# Security Architecture and Failure Handling

[Español](SECURITY_ARCHITECTURE.md) | [English](SECURITY_ARCHITECTURE.en.md)

[Home](../README.en.md) · [ARCHITECTURE.en.md](ARCHITECTURE.en.md) · [CONFIGURATION.en.md](CONFIGURATION.en.md)

## 1. Scope and trust boundaries

CENTAURUS separates analyst input, external-source responses, local inference, Core execution and persistence. Its controls seek to preserve traceability and limit each component's authority.

The host, its administrators, deployed images and installed plugins are part of the trusted base. Separate dependency environments do not make each plugin a sandbox for hostile code. Container controls also do not replace host security or protect against a compromised administrator.

## 2. Core and LLM authority

Core owns the investigation lifecycle. Intent validation, Target construction, the Planner and rules determine the operational flow and its persistent results.

LLM #1 interprets a request as an Intent constrained by a schema and permitted values. It has no authority to execute arbitrary tools, change the catalog or write findings. An invalid interpretation must stop that flow before investigation.

LLM #2 operates after the deterministic report is persisted. It receives a controlled projection that excludes `Evidence.data`, retains relevant references and metadata and limits the supplied information. Its output undergoes structural validation and factual checks against the permitted context; items that fail those checks are discarded. These checks assess consistency with the supplied context; they do not independently verify source accuracy or guarantee the truth of every generated statement.

JSON validation does not establish truth. These controls reduce the input surface and constrain response usage without claiming universal immunity to prompt injection or model errors. Assistance is ephemeral, non-authoritative and does not modify `report.json`.

## 3. Containers and networking

The reference deployment applies:

| Component | Controls |
| --- | --- |
| Core | User `1000:1000`, read-only root, persistent workspace and temporary `/tmp` limited to 256 MiB with `nosuid,nodev,noexec`. |
| Core | All Linux capabilities dropped, `no-new-privileges`, 256-process limit and `init` to reap child processes. |
| Ollama | Capabilities dropped, `no-new-privileges`, 512-process limit and read-only model-store mount. |
| LLM network | Internal network with no Ollama port published on the host; Ollama has no route to external networks. |
| Core network | Ollama access through the internal network and OSINT-source egress through a separate network. |

The reference Ollama image runs as root inside the container; it is not presented as rootless. Its isolation relies on the specific controls above. Core does not mount the Docker socket.

No published ports refers to the supplied Compose configuration. Administrative changes to networks, mounts or privileges change that security posture.

## 4. Appliance access

On OVA/USB, the analyst user belongs to neither the `sudo` nor the `docker` group. Authorized commands are exposed through restricted wrappers requiring zero arguments, a TTY and fresh authentication through `sudo -k`; they do not use `NOPASSWD` access.

The broker verifies user identity, ownership and permissions of critical paths, Compose configuration, the environment file and Core image. It clears the inherited environment, uses a fixed local Docker connection and prevents concurrent sessions through locking. If Docker is unavailable, it fails instead of starting the daemon automatically.

`centaurus-poweroff` provides a constrained, authenticated shutdown. These controls belong to the appliance. The administrator of a Git + Docker installation retains the Docker privileges required for that deployment.

## 5. Supply chain

The build uses locked dependencies, versioned supply references and digest-pinned images where defined in the repository. Tools with incompatible dependencies have separate environments, and bootstrap performs consistency checks with `pip check`.

Model identity is checked during provisioning; normal operation does not require model downloads from Ollama. Changing images, models or locks requires renewed consistency checks.

These mechanisms alone do not constitute a complete signed SBOM, hashes for every dependency artifact or universal binary reproducibility. Published OVA/USB hashes verify identity against the distributed value; they do not replace an independent publisher signature.

## 6. Failures and result preservation

| Situation | Behavior |
| --- | --- |
| Core structural or contract error | Flow stops; an already-started investigation is marked failed where applicable. |
| Task or source failure | `ExecutionFailure` is recorded; a partial investigation may continue if valid knowledge remains. |
| All tasks fail without valid knowledge | Failed investigation, without a valid results report. |
| LLM #2 assistance unavailable, invalid or timed out | The already-persisted deterministic report is retained. |
| Progress notification failure | Must not invalidate knowledge produced by the main flow. |

`COMPLETED` denotes completion of the domain lifecycle; it does not guarantee that every source responded. Always review execution failures and report coverage.

There is no global transactional rollback of all files. A later failure can leave earlier artifacts useful for diagnosis; their isolated presence does not prove successful investigation completion. [`STORAGE.en.md`](STORAGE.en.md) defines authoritative persistence.

## 7. Inference resources

LLM #2 assistance defaults to a 300-second timeout and an 8192 context window, with an optional generation limit. Its request disables extended reasoning through `think=false` and requests `keep_alive=0`. These options belong to that flow, rather than being a global guarantee for every Ollama client.

Universal out-of-memory recovery, automatic retries and implicit parallelism are not promised. A timeout limits client waiting; operators should inspect the service if resource problems persist. Supported settings are documented in [`CONFIGURATION.en.md`](CONFIGURATION.en.md).

## 8. Data protection and operation

Protect the workspace and backups: they may contain collected public information, personal data, targets and operational context. Apply deployment-appropriate permissions and retention, and review artifacts before sharing them.

Assistance telemetry is not intended to dump full prompts or reports. This does not mean that every log is free of sensitive information; error messages and execution context require review.

Change initial appliance credentials in persistent deployments, keep secrets outside Git and maintain consistent backups before changing the runtime. Specific procedures are in [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md), [`DEPLOYMENT_OVA.en.md`](DEPLOYMENT_OVA.en.md) and [`DEPLOYMENT_USB.en.md`](DEPLOYMENT_USB.en.md).
