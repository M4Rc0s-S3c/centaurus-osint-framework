# Local Core on Windows

[Español](DEPLOYMENT_WINDOWS.md) | [English](DEPLOYMENT_WINDOWS.en.md)

[Home](../README.en.md) · [`INSTALL.en.md`](INSTALL.en.md) · [`USER_GUIDE.en.md`](USER_GUIDE.en.md)

## 1. Scope and limits

Native Windows runs Core, CLI, persistence and both LLM roles through Python, without Docker. It is an option for development and local use when the required dependencies are available. OVA remains the main distribution; to use it from Windows, follow [`DEPLOYMENT_OVA.en.md`](DEPLOYMENT_OVA.en.md).

Installing the package does not reproduce Docker isolation or guarantee parity across all six tools. Core accesses Ollama through HTTP and stores investigations in the user workspace.

## 2. Requirements and preparation

You need a Windows account with write access to its profile, Python 3.12 or later, source code from an identified release and networking to download dependencies and query OSINT sources. For LLM functions, prepare Ollama for Windows and the `qwen3:4b` model.

From PowerShell, check Python and, if already installed, Ollama:

```powershell
python --version
python -m pip --version
ollama --version
ollama list
```

Run the following steps from the repository root containing `pyproject.toml`. Retain the identity of the tag/commit or ZIP used. Neither virtual-environment activation nor a PowerShell execution-policy change is required.

## 3. Core installation

Using locked dependencies aligns the Core environment with the distribution lock versions:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip check
```

`-e` installs in editable mode: code runs from the checkout. The lock reduces dependency variation; it does not certify complete Windows/Linux equivalence. Do not install the DNSRecon, Sublist3r and TheHarvester locks into this same environment.

For development without locking dependencies to the distribution lock, `pip install -e .` is an alternative after creating the environment. To install a non-editable copy while retaining the prepared dependencies, replace the editable installation with:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-deps .
.\.venv\Scripts\python.exe -m pip check
```

## 4. Launcher and offline checks

Packaging generates `.venv\Scripts\centaurus.exe` from `centaurus = "centaurus.main:main"`. It is a launcher tied to its Python environment, not a standalone portable executable. Do not copy it on its own.

```powershell
.\.venv\Scripts\centaurus.exe --help
.\.venv\Scripts\centaurus.exe --version
.\.venv\Scripts\centaurus.exe capabilities
.\.venv\Scripts\centaurus.exe capabilities --rules
.\.venv\Scripts\centaurus.exe rules
```

These commands need no Ollama and create no investigation. The alternative that avoids relying on the launcher or `PATH` is:

```powershell
.\.venv\Scripts\python.exe -m centaurus --help
```

## 5. Persistent workspace

The `/workspace` default targets Linux/Docker. Set an explicit Windows path for the session:

```powershell
$env:CENTAURUS_WORKSPACE = "$env:USERPROFILE\CENTAURUS\workspace"
New-Item -ItemType Directory -Force $env:CENTAURUS_WORKSPACE | Out-Null
```

Optionally persist the variable in the user profile for new consoles:

```powershell
[Environment]::SetEnvironmentVariable(
    "CENTAURUS_WORKSPACE",
    "$env:USERPROFILE\CENTAURUS\workspace",
    "User"
)
```

Normal operation creates `logs\centaurus.log` and `investigations\<investigation-id>\`, containing evidence, findings, reports and execution failures. `report.json` is authoritative and `report.md` is its deterministic projection; LLM #2 assistance is ephemeral. See [`STORAGE.en.md`](STORAGE.en.md).

## 6. Local Ollama and configuration

Direct Core defaults are `OLLAMA_BASE_URL=http://localhost:11434` and `OLLAMA_MODEL=qwen3:4b`. If they match your local installation, there is no need to change the endpoint or add Docker. Check `ollama list` and, only if the model is missing, download it:

```powershell
ollama pull qwen3:4b
ollama list
```

A matching model name in the list does not establish byte-for-byte identity with the appliance-pinned model. Changing the model or Ollama version requires your own functional validation. Full configuration, including the 300-second assistance timeout and 8192 context window, is in [`CONFIGURATION.en.md`](CONFIGURATION.en.md).

## 7. Tools and coverage

| Capability | Windows dependency |
| --- | --- |
| WHOIS | `python-whois`, installed with Core. |
| RDAP and crt.sh | HTTP client `httpx`, installed with Core. |
| DNSRecon | `dnsrecon` executable accessible to the process. |
| Sublist3r | `sublist3r` executable accessible to the process. |
| TheHarvester | `theHarvester` executable accessible to the process. |

The IP capability uses RDAP. DOMAIN also depends on external tools; listing them in `capabilities` does not prove they are installed. Missing executables or failed sources can yield partial coverage with `ExecutionFailure`. Installing and validating these Windows runtimes is a separate extension, not part of Core installation. Docker uses separate environments because their dependencies can conflict.

## 8. Session and functional validation


```powershell
.\.venv\Scripts\centaurus.exe shell
```

Inside the shell use `/help`, `/capabilities`, `/rules` and `/exit`. Follow [`USER_GUIDE.en.md`](USER_GUIDE.en.md) to formulate an authorized request and interpret results. Check that the workspace receives artifacts and retains results after the session closes. Offline commands only check the CLI: they do not validate inference, sources or full parity.

## 9. Security and GPU

Native execution inherits the Windows account’s permissions, filesystem and network access. Use a non-administrative account for routine operation and a dedicated workspace. Docker controls such as a read-only root, fixed UID, process/tmpfs limits, `cap_drop`, `no-new-privileges` and internal networks are not reproduced.

CPU/GPU selection belongs to Ollama for Windows, using the same HTTP API. [`GPU_OLLAMA_DOCKER.en.md`](GPU_OLLAMA_DOCKER.en.md) covers only the experimental Linux + Docker variant; its overlays do not apply to native Windows.

## 10. Updates and removal

Before updating, end sessions, back up the workspace and preserve local changes and the previous version identity. Explicitly select the new tag/commit, then repeat section 3 using that version’s locks and `pip check`. Reinstall when dependencies, metadata or entry points change.

To remove the package from the environment:

```powershell
.\.venv\Scripts\python.exe -m pip uninstall centaurus
```

Uninstalling the package does not remove the workspace or Ollama and its models. Preserve results before removing a dedicated virtual environment.

## 11. Troubleshooting and references

Launcher, Python environment, permissions, Ollama and external-tool issues are covered in [`TROUBLESHOOTING.en.md`](TROUBLESHOOTING.en.md).

- [`USER_GUIDE.en.md`](USER_GUIDE.en.md)
- [`CONFIGURATION.en.md`](CONFIGURATION.en.md)
- [`STORAGE.en.md`](STORAGE.en.md)
- [`SECURITY_ARCHITECTURE.en.md`](SECURITY_ARCHITECTURE.en.md)
- [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)
