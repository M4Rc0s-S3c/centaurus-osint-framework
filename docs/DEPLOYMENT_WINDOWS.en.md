# Local Core on Windows

[Español](DEPLOYMENT_WINDOWS.md) | [English](DEPLOYMENT_WINDOWS.en.md)

[Home](../README.en.md) · [INSTALL.en.md](INSTALL.en.md) · [USER_GUIDE.en.md](USER_GUIDE.en.md)

Native Windows is an option for development and local Core execution. To use the main prebuilt distribution on a Windows host, follow [`DEPLOYMENT_OVA.en.md`](DEPLOYMENT_OVA.en.md) in a compatible VMware environment.

## 1. Preparation

Use a checkout of the selected release and Python 3.12 or later, as required by `pyproject.toml`. Run the following PowerShell commands from the repository root. Internet access is required when dependencies must be downloaded.

## 2. Environment and workspace

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

## 3. Verification

```powershell
.\.venv\Scripts\centaurus.exe --help
.\.venv\Scripts\centaurus.exe capabilities --rules
```

These commands inspect the CLI and static catalog; they do not validate that every external tool is installed or works on Windows. For the shell, use `.\.venv\Scripts\centaurus.exe shell` after preparing Ollama and the runtime dependencies needed by the chosen workflow.

## 4. Related documentation

- [`CONFIGURATION.en.md`](CONFIGURATION.en.md)
- [`USER_GUIDE.en.md`](USER_GUIDE.en.md)
- [`TROUBLESHOOTING.en.md`](TROUBLESHOOTING.en.md)
- [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)
