# Core local en Windows

[Español](DEPLOYMENT_WINDOWS.md) | [English](DEPLOYMENT_WINDOWS.en.md)

[Inicio](../README.md) · [INSTALL.md](INSTALL.md) · [USER_GUIDE.md](USER_GUIDE.md)

Windows nativo es una opción para desarrollo y ejecución local del Core. Para utilizar la distribución principal preconstruida desde un host Windows, sigue [`DEPLOYMENT_OVA.md`](DEPLOYMENT_OVA.md) en un entorno VMware compatible.

## 1. Preparación

Utiliza un checkout de la release seleccionada y Python 3.12 o posterior, según `pyproject.toml`. Ejecuta los comandos PowerShell siguientes desde la raíz del repositorio. Necesitarás acceso a Internet cuando deban descargarse dependencias.

## 2. Entorno y workspace

Windows nativo puede utilizarse para desarrollo/ejecución local del Core.

Ejemplo:

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

Para utilizar funciones LLM localmente, Ollama debe estar instalado y disponer del modelo correspondiente.

La modalidad Windows no declara paridad completa con la distribución Linux + Docker.

## 3. Verificación

```powershell
.\.venv\Scripts\centaurus.exe --help
.\.venv\Scripts\centaurus.exe capabilities --rules
```

Estos comandos comprueban la CLI y el catálogo estático; no validan que todas las herramientas externas estén instaladas o funcionen en Windows. Para abrir el shell, utiliza `.\.venv\Scripts\centaurus.exe shell` después de preparar Ollama y las dependencias de ejecución necesarias para el flujo elegido.

## 4. Documentación relacionada

- [`CONFIGURATION.md`](CONFIGURATION.md)
- [`USER_GUIDE.md`](USER_GUIDE.md)
- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)
