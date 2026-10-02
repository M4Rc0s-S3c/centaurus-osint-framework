# USB Image Deployment

[Español](DEPLOYMENT_USB.md) | [English](DEPLOYMENT_USB.en.md)

[Home](../README.en.md) · [INSTALL.en.md](INSTALL.en.md) · [USER_GUIDE.en.md](USER_GUIDE.en.md)

## 1. Scope and requirements

`CENTAURUS-USB.img` is a complete raw disk image containing the appliance and its partition layout. It is written to a physical device; copying the file into a USB folder does not create bootable media.

The target computer must support x86-64 and UEFI boot. Reference validation used a Toshiba Z30-A with Intel I218-V Ethernet and the `e1000e` driver. That reference does not guarantee universal compatibility with other adapters, Wi-Fi or GPUs. The baseline uses CPU.

The device must provide **at least `31457280000` actual bytes**. Check its capacity in bytes: a commercial “32 GB” label is not a substitute. Allow additional storage for the original image on the computer performing the write.

## 2. Download and verification

Use the download link published in [`INSTALL.en.md`](INSTALL.en.md).

| Property | Value |
| --- | --- |
| File | `CENTAURUS-USB.img` |
| Size in bytes | `31457280000` |
| 512-byte sectors | `61440000` |
| SHA-256 | `7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165` |

On Linux:

```bash
stat -c '%s' CENTAURUS-USB.img
sha256sum CENTAURUS-USB.img
```

On PowerShell:

```powershell
(Get-Item .\CENTAURUS-USB.img).Length
Get-FileHash .\CENTAURUS-USB.img -Algorithm SHA256
```

Do not continue if the size or hash differs. This verifies the download before writing; it does not by itself verify the resulting device.

## 3. Identify the destination

**Writing the image overwrites the selected device's partition table and data.** Back up any content you need and identify the disk by model, serial number and capacity. Do not select it solely by drive letter or enumeration order.

On Linux, inspect the inventory without modifying it:

```bash
lsblk -b -o NAME,SIZE,MODEL,SERIAL,TRAN,TYPE,MOUNTPOINTS
```

On PowerShell:

```powershell
Get-Disk | Select-Object Number,FriendlyName,SerialNumber,Size,BusType,IsBoot,IsSystem
```

Select the **whole USB disk**, never a partition or the system disk. Disconnect other removable media if that helps avoid confusion. Close applications accessing the destination and unmount its volumes before writing.

## 4. Raw writing

1. Open a raw-image writing tool that supports selecting a physical disk, with the required administrative privileges.
2. Select `CENTAURUS-USB.img` as the source and recheck the destination's identity and capacity.
3. Use direct whole-image writing, preserving its partition layout. Do not select file extraction or conversion into an ISO installer.
4. Confirm erasure only for the identified device and allow writing and buffer flushing to finish.
5. If the tool offers post-write verification, run it before first boot. For larger devices, compare the written region of `31457280000` bytes, not a hash of the entire device.
6. Safely eject the media. Cancel any operating-system prompt to format unrecognized partitions.

A reused device larger than the image can retain previous partition metadata outside the overwritten region, including a backup GPT at its physical end. Preparing it requires prior administrative review, unambiguous identification and backup. Do not accept automatic GPT repairs or partition expansion as part of this procedure. Additional unallocated space does not mean the workspace has expanded.

## 5. First boot and use

Connect the USB to the target computer and select its UEFI entry in the boot menu. Keep internal disks outside the writing procedure; booting the appliance does not require installing it on them.

Log in as `centaurus` using the credentials published in [`INSTALL.en.md`](INSTALL.en.md). Change them if the media will remain in use. From an interactive TTY:

```bash
centaurus
```

The wrapper accepts zero arguments and requires fresh authentication. [`USER_GUIDE.en.md`](USER_GUIDE.en.md) describes the shell and result interpretation.

The reference logical interface is `centaurus0` with DHCP. An administrator can inspect `ip -br addr`, `ip route` and `findmnt /workspace`. If no usable interface appears, check hardware compatibility before attributing the problem to an OSINT source. Collection requires networking even though the LLM model is local.

## 6. Persistence and shutdown

The workspace persists on the media itself. Make consistent backups of `/workspace` with investigations stopped, following [`STORAGE.en.md`](STORAGE.en.md). Wear, loss or accidental USB removal can affect this data.

Exit the Core shell and run from the host TTY:

```bash
centaurus-poweroff
```

Wait for complete shutdown before removing the USB. Operation changes the media; after first boot, the written region is no longer expected to retain the distribution image's hash.

## 7. Related documentation

- [`DEPLOYMENT_OVA.en.md`](DEPLOYMENT_OVA.en.md)
- [`CONFIGURATION.en.md`](CONFIGURATION.en.md)
- [`SECURITY_ARCHITECTURE.en.md`](SECURITY_ARCHITECTURE.en.md)
