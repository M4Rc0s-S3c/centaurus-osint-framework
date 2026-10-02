# Core local en Windows

[Español](DEPLOYMENT_WINDOWS.md) | [English](DEPLOYMENT_WINDOWS.en.md)

[Inicio](../README.md) · [`INSTALL.md`](INSTALL.md) · [`USER_GUIDE.md`](USER_GUIDE.md)

## 1. Alcance y límites

Windows nativo permite ejecutar Core, CLI, persistencia y las dos funciones LLM desde Python, sin Docker. Es una opción para desarrollo y uso local con las dependencias necesarias disponibles. La OVA sigue siendo la distribución principal; para utilizarla desde Windows, sigue [`DEPLOYMENT_OVA.md`](DEPLOYMENT_OVA.md).

La instalación del paquete no reproduce el aislamiento Docker ni garantiza paridad de las seis herramientas. El Core accede a Ollama por HTTP y guarda las investigaciones en el workspace del usuario.

## 2. Requisitos y preparación

Necesitas una cuenta Windows con escritura en su perfil, Python 3.12 o posterior, código fuente de una release identificada y acceso de red para descargar dependencias y consultar fuentes OSINT. Para las funciones LLM, prepara Ollama para Windows y el modelo `qwen3:4b`.

Desde PowerShell, comprueba Python y, si ya está instalado, Ollama:

```powershell
python --version
python -m pip --version
ollama --version
ollama list
```

Ejecuta los pasos siguientes desde la raíz del repositorio, donde está `pyproject.toml`. Conserva la identidad del tag/commit o ZIP utilizado. No es necesario activar el entorno virtual ni cambiar la política de ejecución de PowerShell.

## 3. Instalación del Core

La opción con dependencias fijadas aproxima el entorno del Core a las versiones del lock de la distribución:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip check
```

`-e` instala en modo editable: el código se ejecuta desde el checkout. El lock reduce variación de dependencias; no certifica equivalencia completa entre Windows y Linux. No instales los locks de DNSRecon, Sublist3r y TheHarvester en este mismo entorno.

Como alternativa para desarrollo sin fijar las dependencias al lock, tras crear el entorno se puede usar `pip install -e .`. Para instalar una copia no editable conservando las dependencias ya preparadas, sustituye la instalación editable por:

```powershell
.\.venv\Scripts\python.exe -m pip install --no-deps .
.\.venv\Scripts\python.exe -m pip check
```

## 4. Lanzador y comprobaciones sin red

El empaquetado genera `.venv\Scripts\centaurus.exe` a partir de `centaurus = "centaurus.main:main"`. Es un lanzador ligado al entorno Python, no un ejecutable portable autónomo. No debe copiarse de forma aislada.

```powershell
.\.venv\Scripts\centaurus.exe --help
.\.venv\Scripts\centaurus.exe --version
.\.venv\Scripts\centaurus.exe capabilities
.\.venv\Scripts\centaurus.exe capabilities --rules
.\.venv\Scripts\centaurus.exe rules
```

Estos comandos no necesitan Ollama ni crean una investigación. La alternativa que evita depender del lanzador o de `PATH` es:

```powershell
.\.venv\Scripts\python.exe -m centaurus --help
```

## 5. Workspace persistente

El valor `/workspace` está pensado para Linux/Docker. Define una ruta Windows explícita para la sesión:

```powershell
$env:CENTAURUS_WORKSPACE = "$env:USERPROFILE\CENTAURUS\workspace"
New-Item -ItemType Directory -Force $env:CENTAURUS_WORKSPACE | Out-Null
```

Opcionalmente, conserva la variable en el perfil del usuario para las nuevas consolas:

```powershell
[Environment]::SetEnvironmentVariable(
    "CENTAURUS_WORKSPACE",
    "$env:USERPROFILE\CENTAURUS\workspace",
    "User"
)
```

La operación normal genera `logs\centaurus.log` e `investigations\<investigation-id>\`, con evidencias, hallazgos, informes y fallos de ejecución. `report.json` es autoritativo y `report.md` es su proyección determinista; la asistencia LLM #2 es efímera. Consulta [`STORAGE.md`](STORAGE.md).

## 6. Ollama local y configuración

Los valores directos del Core son `OLLAMA_BASE_URL=http://localhost:11434` y `OLLAMA_MODEL=qwen3:4b`. Si coinciden con tu instalación local, no necesitas cambiar el endpoint ni añadir Docker. Comprueba `ollama list` y, solo si falta el modelo, descárgalo:

```powershell
ollama pull qwen3:4b
ollama list
```

La presencia del nombre en la lista no prueba identidad byte a byte con el modelo fijado en la appliance. Cambiar modelo o versión de Ollama requiere validación funcional propia. La configuración completa, incluidos timeout de asistencia de 300 segundos y contexto de 8192, está en [`CONFIGURATION.md`](CONFIGURATION.md).

## 7. Herramientas y cobertura

| Capacidad | Dependencia en Windows |
| --- | --- |
| WHOIS | `python-whois`, instalado con el Core. |
| RDAP y crt.sh | Cliente HTTP `httpx`, instalado con el Core. |
| DNSRecon | Ejecutable `dnsrecon` accesible al proceso. |
| Sublist3r | Ejecutable `sublist3r` accesible al proceso. |
| TheHarvester | Ejecutable `theHarvester` accesible al proceso. |

La capacidad IP usa RDAP. DOMAIN depende también de herramientas externas; enumerarlas en `capabilities` no demuestra que estén instaladas. Si faltan ejecutables o fallan fuentes, puede quedar cobertura parcial con `ExecutionFailure`. La instalación y validación de esos runtimes Windows es una extensión separada, no incluida en la instalación del Core. Docker utiliza entornos separados porque sus dependencias pueden ser incompatibles.

## 8. Sesión y validación funcional


```powershell
.\.venv\Scripts\centaurus.exe shell
```

Dentro del shell utiliza `/help`, `/capabilities`, `/rules` y `/exit`. Sigue [`USER_GUIDE.md`](USER_GUIDE.md) para formular una petición autorizada e interpretar los resultados. Verifica que el workspace recibe los artefactos y conserva los resultados tras cerrar la sesión. Los comandos offline solo comprueban la CLI: no validan inferencia, fuentes ni paridad completa.

## 9. Seguridad y GPU

La ejecución nativa hereda permisos, filesystem y red de la cuenta Windows. Usa una cuenta sin privilegios administrativos para la operación ordinaria y un workspace dedicado. No se reproducen la raíz de solo lectura, UID fijo, límites de procesos/tmpfs, `cap_drop`, `no-new-privileges` ni redes internas del despliegue Docker.

La selección CPU/GPU corresponde a Ollama para Windows, conservando la misma API HTTP. La guía [`GPU_OLLAMA_DOCKER.md`](GPU_OLLAMA_DOCKER.md) trata exclusivamente la variante experimental Linux + Docker; sus overlays no se aplican a Windows nativo.

## 10. Actualización y retirada

Antes de actualizar, termina las sesiones, respalda el workspace y conserva los cambios locales y la identidad de la versión anterior. Selecciona explícitamente el nuevo tag/commit; después repite la instalación del apartado 3 con los locks de esa versión y `pip check`. Reinstala cuando cambien dependencias, metadatos o puntos de entrada.

Para retirar el paquete del entorno:

```powershell
.\.venv\Scripts\python.exe -m pip uninstall centaurus
```

Desinstalar el paquete no elimina el workspace ni Ollama y sus modelos. Conserva los resultados antes de retirar un entorno virtual dedicado.

## 11. Resolución de problemas y referencias

Los problemas de lanzador, entorno Python, permisos, Ollama y herramientas externas se recogen en [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md).

- [`USER_GUIDE.md`](USER_GUIDE.md)
- [`CONFIGURATION.md`](CONFIGURATION.md)
- [`STORAGE.md`](STORAGE.md)
- [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)
