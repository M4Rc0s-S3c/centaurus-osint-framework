# Ollama GPU with Docker — experimental

[Español](GPU_OLLAMA_DOCKER.md) | [English](GPU_OLLAMA_DOCKER.en.md)

[Home](../README.en.md) · [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md) · [`TROUBLESHOOTING.en.md`](TROUBLESHOOTING.en.md)

## 1. Status and scope

**Experimental guidance, without CENTAURUS GPU hardware certification.** CPU remains the distributed baseline. The repository contains no GPU overlays: the examples below are proposals for local configuration requiring preparation and validation on the actual host. Publishing this guide does not imply those tests have been executed.

| Variant | CENTAURUS status |
| --- | --- |
| Linux + Docker CPU | Distribution baseline. |
| NVIDIA + Docker | Experimental proposal, pending host validation. |
| AMD ROCm + Docker | Experimental proposal; also requires its own image and supply-chain identity. |
| Vulkan | Separate experimental evaluation; no distributed profile. |
| GPU in OVA/VMware or USB | Out of scope; support or passthrough is not implied. |

Native Windows is covered in [`DEPLOYMENT_WINDOWS.en.md`](DEPLOYMENT_WINDOWS.en.md).

## 2. Contract to preserve

Only `centaurus-ollama` receives GPU access. Core retains its code, user, networks, workspace and `Evidence -> Finding -> Report` contracts. Preserve `OLLAMA_BASE_URL=http://centaurus-ollama:11434`, `OLLAMA_NO_CLOUD=1`, the read-only model mount, internal `centaurus-llm-network` and absence of published ports. Core remains the only service on the egress network.

Preserve `cap_drop: ALL`, `no-new-privileges` and process limits. Do not use `privileged` or publish `11434` to resolve GPU issues. If a combination fails with the current controls, leave that variant unvalidated and investigate compatibility; do not silently weaken the base Compose configuration.

## 3. Host preparation

First complete CPU installation through [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md). Preserve the workspace, image/model identity and reference results. GPU driver and runtime preparation is a host administration task.

For NVIDIA, check the GPU and driver with `nvidia-smi`. Install and configure NVIDIA Container Toolkit following its official documentation, and validate access from a test container before applying the overlay. Runtime configuration or restarting Docker may affect other host services; plan that intervention.

For AMD, check the GPU and driver against the Ollama/ROCm matrix and inspect `/dev/kfd` and `/dev/dri`. Device permissions must be handled explicitly. Compatibility must match the selected image version, not merely the latest version’s documentation.

## 4. NVIDIA example and Compose usage

Create the local overlay outside the checkout, for example in the dedicated data directory. This avoids introducing an untracked file that blocks bootstrap. This YAML adds a GPU reservation only to Ollama:

```yaml
services:
  centaurus-ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

To select a GPU, replace `count` with `device_ids` using identifiers checked on that host; do not combine both fields. The example preserves the base Compose Ollama digest: Docker accepting the reservation does not prove that image can use your GPU.

From the checkout, with `CENTAURUS_DATA_ROOT` set to the CPU installation’s data directory, after saving the YAML there as `compose.gpu-nvidia.yml`:

```bash
CENTAURUS_ENV_FILE="$CENTAURUS_DATA_ROOT/compose.env"
CENTAURUS_GPU_OVERLAY="$CENTAURUS_DATA_ROOT/compose.gpu-nvidia.yml"
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml -f "$CENTAURUS_GPU_OVERLAY" --profile framework config
```

Review the rendered result and section 2 controls. With Core sessions closed and the host prepared, locally applying the variant would use:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml -f "$CENTAURUS_GPU_OVERLAY" up -d --force-recreate centaurus-ollama
```

While evaluating GPU, use both files and the same `--env-file` for Compose operations, including Core sessions. The current bootstrap only uses `docker/compose.yml`: it neither activates nor certifies the overlay, and rerunning it may recreate Ollama with the CPU baseline.

## 5. AMD ROCm and Vulkan

The ROCm path requires an appropriate Ollama image and device access. This conceptual example requires `CENTAURUS_ROCM_IMAGE` to identify a reviewed, digest-pinned image; the current lock contains no certified ROCm digest:

```yaml
services:
  centaurus-ollama:
    image: "${CENTAURUS_ROCM_IMAGE:?Set a reviewed digest-pinned ROCm image}"
    devices:
      - /dev/kfd:/dev/kfd
      - /dev/dri:/dev/dri
```

Requiring the variable prevents omission but does not itself validate its digest. Do not use a mutable tag as the final identity or claim this variant passes CPU-bootstrap image checks. Record and check its image, version, hardware, model and compatibility with hardening before treating it as a validated deployment.

Vulkan is outside these examples. Current Ollama documentation describes its availability in current images, but that does not certify its behavior in the CENTAURUS-pinned digest. Experimental status here refers to project integration, independently of the provider’s stated status.

## 6. Validation and resources

Record GPU, driver, toolkit/runtime, Docker/Compose version, image digest, model identity and LLM configuration. Local acceptance must cover:

1. Working GPU access on the host and in an independent container.
2. Rendered Compose preserves networks, permissions, mounts and absence of ports; Core receives no GPU.
3. Ollama actually uses the accelerator during inference; observing a device reservation is insufficient.
4. Small and many-finding cases preserve report and assistance contracts, with known coverage.
5. Latency, RAM and VRAM measurements, without out-of-memory failures or unexpected CPU fallback; recheck after reboot.
6. Verified return to CPU with persistent data preserved.


```bash
docker inspect centaurus-ollama --format 'DeviceRequests={{json .HostConfig.DeviceRequests}}'
docker logs --tail 100 centaurus-ollama
docker port centaurus-ollama
```

The last command should produce no output. For NVIDIA, also observe `nvidia-smi` during inference; inspect the relevant backend metrics for AMD. A successful local test documents that host, not all GPUs.

VRAM depends on model, context, cache and concurrency. GPU does not fix truncation, grounding or output validation. Initially retain the LLM #2 profile documented in [`CONFIGURATION.en.md`](CONFIGURATION.en.md). Any adjustment needs its own measurement and validation.

## 7. Return to CPU

End Core sessions. Using the same environment paths, recreate Ollama with only the base Compose file:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml up -d --force-recreate centaurus-ollama
```

Check the image, absence of GPU requests/devices, service and CPU operation. Preserve the model and workspace; do not delete them to revert. Driver or toolkit removal is separate host maintenance.

## 8. Troubleshooting and references

See [`TROUBLESHOOTING.en.md`](TROUBLESHOOTING.en.md) for GPU diagnosis and [`SECURITY_ARCHITECTURE.en.md`](SECURITY_ARCHITECTURE.en.md) for deployment controls.

- [Ollama — Docker](https://docs.ollama.com/docker)
- [Ollama — Hardware support](https://docs.ollama.com/gpu)
- [Docker Compose — GPU access](https://docs.docker.com/compose/how-tos/gpu-support/)
- [NVIDIA Container Toolkit — Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
