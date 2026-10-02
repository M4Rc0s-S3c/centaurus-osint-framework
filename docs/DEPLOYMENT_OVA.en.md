# OVA Appliance Deployment

[Español](DEPLOYMENT_OVA.md) | [English](DEPLOYMENT_OVA.en.md)

[Home](../README.en.md) · [INSTALL.en.md](INSTALL.en.md) · [USER_GUIDE.en.md](USER_GUIDE.en.md)

## 1. Scope and requirements

The OVA ships a prebuilt appliance with Debian, Docker, Core, tools and Ollama with `qwen3:4b`. It does not require cloning the repository or running the Git + Docker bootstrap inside the virtual machine.

Use a VMware environment supporting OVA import and the embedded x86-64 hardware profile. Allow enough capacity to import the virtual disks and retain workspace growth. Download size does not represent all storage required for operation.

The reference configuration uses three logical disks: SYSTEM, PLATFORM and WORKSPACE. Preserve the included hardware profile, firmware and E1000 interface with NAT networking for first boot. The baseline runs on CPU; GPU acceleration is not required.

## 2. Download and identity

Download the artifact through the link published in [`INSTALL.en.md`](INSTALL.en.md). Keep an original copy for future imports.

| Property | Value |
| --- | --- |
| File | `CENTAURUS-C4-FINAL.ova` |
| Size in bytes | `11828618752` |
| SHA-256 | `d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868` |

On Linux:

```bash
stat -c '%s' CENTAURUS-C4-FINAL.ova
sha256sum CENTAURUS-C4-FINAL.ova
```

On PowerShell:

```powershell
(Get-Item .\CENTAURUS-C4-FINAL.ova).Length
Get-FileHash .\CENTAURUS-C4-FINAL.ova -Algorithm SHA256
```

Check that size and hash match exactly before import. If they differ, retain diagnostic information and obtain the correct artifact again.

## 3. Import

1. Open VMware's OVA import/open function and select the verified file.
2. Choose a name and location with enough space for the virtual machine.
3. Check that all three disks, imported firmware and the expected network adapter are preserved. Avoid changing controllers during initial import.
4. Complete the import and start the appliance through its console.

First boot prepares the instance's local identity, including `machine-id` and SSH host keys. The presence of these keys does not imply that SSH should be exposed or additional ports opened to use CENTAURUS.

## 4. First session

Log in at the console as `centaurus`. Initial credentials and the administration account are documented in [`INSTALL.en.md`](INSTALL.en.md); change them if the appliance will remain deployed.

From an interactive TTY:

```bash
centaurus
```

The wrapper accepts no arguments and requires fresh authentication. It opens the Core shell through the broker; the analyst does not need direct Docker daemon access. See [`USER_GUIDE.en.md`](USER_GUIDE.en.md) for session use and result interpretation.

Inference uses the local model. OSINT queries require connectivity to the relevant external sources; having the model locally does not make collection an offline process.

## 5. Operational checks

On the appliance host, an administrator can inspect:

```bash
ip -br addr show centaurus0
ip route
findmnt /workspace
systemctl --failed --no-pager
```

The expected logical interface is `centaurus0`, configured through DHCP. If it receives no address, first check the virtual adapter, NAT network and virtualization environment's DHCP service.

If `centaurus` rejects startup, check that a TTY is in use and another session is not active. Integrity failures or an unavailable Docker daemon require administrative diagnosis; editing manifests to bypass verification is outside the usage procedure.

## 6. Persistence and maintenance

Investigations persist in `/workspace`; [`STORAGE.en.md`](STORAGE.en.md) describes their structure. Operational logs reside in `/workspace/logs/centaurus.log`.

Before maintenance, finish investigations and close the Core session. Keep a consistent workspace backup and record the appliance identity. A copy or snapshot of the powered-off VM complements result backups; it does not replace a retention policy.

The appliance does not retain a Git checkout for routine updates. Do not apply the Git + Docker tag-switching and bootstrap procedure inside it. Runtime changes require administrative maintenance that keeps the image, configuration and verified identities consistent.

## 7. Shutdown

Exit the Core shell, then run the following as `centaurus` from the host TTY:

```bash
centaurus-poweroff
```

The command accepts zero arguments and requires fresh authentication. Wait for shutdown to complete before closing or moving the virtual machine files.

## 8. Related documentation

- [`CONFIGURATION.en.md`](CONFIGURATION.en.md)
- [`SECURITY_ARCHITECTURE.en.md`](SECURITY_ARCHITECTURE.en.md)
- [`DEPLOYMENT_USB.en.md`](DEPLOYMENT_USB.en.md)
