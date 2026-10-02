# Resolución de problemas

[Español](TROUBLESHOOTING.md) | [English](TROUBLESHOOTING.en.md)

[Inicio](../README.md) · [INSTALL.md](INSTALL.md) · [USER_GUIDE.md](USER_GUIDE.md)

## 1. Identifica el contexto

Antes de aplicar una comprobación, identifica la modalidad y el punto donde aparece el problema. En OVA/USB, `centaurus` es un wrapper del host con cero argumentos; dentro del shell `centaurus>` se utilizan metacomandos como `/help`. En Git + Docker, los comandos Compose se ejecutan desde el host de despliegue. Windows nativo utiliza la CLI del entorno Python.

Conserva el mensaje exacto y los resultados existentes. Las comprobaciones administrativas corresponden al responsable del entorno; el analista de la appliance no necesita permisos Docker generales para trabajar.

## 2. Importación OVA y arranque USB

| Síntoma | Comprobación y siguiente paso |
| --- | --- |
| Tamaño o SHA-256 no coinciden | Compara con la identidad publicada en la guía de la modalidad. Obtén de nuevo el artefacto correcto antes de importarlo o escribirlo. |
| VMware no importa la OVA | Comprueba espacio disponible, compatibilidad de importación y que se conserva el perfil de hardware incluido. |
| La imagen no cabe en el USB | Comprueba la capacidad real en bytes: debe ser al menos `31457280000`. |
| El USB no arranca | Comprueba que se escribió la imagen raw sobre el disco completo y que se selecciona su entrada UEFI. Revisa compatibilidad de firmware y hardware. |
| El host propone formatear particiones del USB | Cancela la propuesta: puede tratarse de particiones que el host no reconoce. |
| Aparecen avisos GPT en un USB reutilizado | Detén el procedimiento y solicita revisión administrativa del dispositivo y sus metadatos. No aceptes reparaciones automáticas. |

Procedimientos e identidades: [`DEPLOYMENT_OVA.md`](DEPLOYMENT_OVA.md) y [`DEPLOYMENT_USB.md`](DEPLOYMENT_USB.md). El hash de la imagen de distribución se verifica antes del primer uso; el sistema modifica el medio USB al arrancar.

## 3. Red y acceso a la appliance

Para diagnóstico administrativo desde el host OVA/USB:

```bash
ip -br addr
ip route
findmnt /workspace
systemctl --failed --no-pager
```

La interfaz lógica de referencia es `centaurus0` por DHCP. En VMware, revisa el adaptador E1000, su conexión a NAT y el servicio DHCP del entorno. **La distribución USB requiere conexión cableada Ethernet:** conecta el cable y comprueba enlace, tarjeta/controlador compatibles y DHCP. La imagen no tiene desplegados controlador ni gestor de conexiones Wi-Fi; no esperes obtener red por Wi-Fi. La validación en un equipo no garantiza compatibilidad con cualquier adaptador Ethernet. Evita renombrar interfaces sin diagnosticar la causa.

Si `centaurus` falla antes de mostrar el shell, comprueba que se ejecuta como usuario `centaurus`, sin argumentos, desde una TTY y sin otra sesión activa. Si el mensaje indica un fallo de integridad o de Docker, conserva el diagnóstico y solicita intervención administrativa. No cambies manifiestos ni concedas acceso genérico a Docker para eludir la comprobación.

## 4. Git + Docker

Desde el host de despliegue, en el checkout utilizado:

```bash
docker info
docker compose version
git status --porcelain --untracked-files=all
```

`docker info` debe funcionar para el usuario de despliegue y Compose debe estar disponible. El último comando debe quedar sin salida antes del bootstrap; conserva o resuelve los cambios locales y los ficheros sin seguimiento antes de repetirlo.

Si aparecen resultados en otra ubicación o parece faltar el workspace, comprueba que se está utilizando el mismo `compose.env` generado por el bootstrap mediante `--env-file`. No crees un workspace alternativo ni borres el anterior para resolver una discrepancia de rutas.

Consulta [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md) para arranque y parada, y [`CONFIGURATION.md`](CONFIGURATION.md) para la resolución de variables y rutas.

### 4.1. Fallos de prerrequisitos y construcción

| Mensaje o síntoma | Causa probable y actuación |
| --- | --- |
| `missing prerequisite: git`, `missing prerequisite: python3` o `missing prerequisite: docker` | Instala el prerrequisito que falta en el host y repite las comprobaciones iniciales. |
| `Git + Docker distribution is certified on Linux only` | El host no es Linux; utiliza la modalidad adecuada para ese sistema. |
| `Docker Engine is not available to the current user` | Revisa el servicio con `systemctl status docker`, después `docker info` y la política de acceso del host. |
| `Docker Compose plugin is required` | Comprueba que el plugin está instalado y funciona `docker compose version`. |
| `release checkout must be clean before bootstrap` | Conserva o reconcilia cambios y ficheros sin seguimiento; no borres trabajo solo para superar la comprobación. |
| El checkout no coincide con `CENTAURUS_RELEASE_COMMIT` | Contrasta `git rev-parse HEAD` con la release prevista y selecciona el commit correcto. |
| Falla la descarga de dependencias durante la construcción | Conserva el error y revisa conectividad y disponibilidad de los artefactos fijados. No consideres validada una construcción incompleta. |
| Falla `pip check` | El entorno candidato es inconsistente; no lo promociones ni lo uses como nueva imagen validada. El bootstrap se detiene antes de actualizar la etiqueta local. |
| Error de escritura en workspace | Comprueba propietario, permisos y ruta del montaje del host generado. El Core normal usa `1000:1000`; el bootstrap cambia el propietario del directorio workspace, no todos los ficheros existentes de forma recursiva. |
| Error de `HOME` o `EROFS` en una herramienta externa | Comprueba el ajuste Compose `HOME=/tmp/centaurus` y el tmpfs de `/tmp`. Conserva la raíz de solo lectura. |
| El disco crece tras construcciones repetidas | Revisa `docker system df` y `docker builder du`. Planifica una limpieza selectiva conservando imágenes necesarias para reversión y datos persistentes; evita purgas indiscriminadas. |

## 5. Ollama, consultas y resultados

| Situación | Interpretación y acción |
| --- | --- |
| `centaurus-ollama` no arranca | Revisa `docker logs --tail 50 centaurus-ollama` y `docker inspect centaurus-ollama`; comprueba imagen, modelo y configuración. |
| El Core no alcanza Ollama | Revisa el estado del servicio y la red LLM interna en Compose. No publiques el puerto `11434` en el host como atajo de diagnóstico. |
| `existing Ollama state does not match the release` | El bootstrap ha encontrado contenido existente incompatible y se detiene; sigue el apartado 5.1 antes de repetir. |
| El modelo no está disponible | Revisa el servicio Ollama, la URL configurada y el almacén persistente. En Git + Docker utiliza los verificadores/aprovisionadores versionados; en la appliance solicita diagnóstico administrativo. |
| Error LLM durante la interpretación | LLM #1 puede impedir iniciar la investigación. Conserva el mensaje y comprueba servicio/modelo antes de repetir. |
| `Invalid request` | Revisa el objetivo y formula una petición simple con un tipo admitido; consulta `/capabilities` dentro del shell. |
| Una fuente falla o devuelve errores HTTP | Revisa `ExecutionFailure` y la cobertura del informe. Puede existir un resultado parcial válido; repetir no garantiza disponibilidad de la fuente. |
| Todas las tareas fallan | La investigación queda fallida. La presencia de ficheros aislados no equivale a disponer de un informe válido. |
| No hay hallazgos | Revisa evidencias y reglas aplicables; cero hallazgos no certifica ausencia de riesgo. |
| LLM #2 tarda, falla o agota el timeout | Conserva el `Report` determinista ya persistido. Revisa logs y recursos; la asistencia adicional es no autoritativa y fail-soft. |
| No encuentras una investigación anterior en el shell | La CLI no ofrece consulta histórica. Revisa el workspace correspondiente al despliegue. |

La inferencia local no elimina la necesidad de red para consultar fuentes OSINT. Los parámetros de timeout y contexto están en [`CONFIGURATION.md`](CONFIGURATION.md); aumentarlos no garantiza recursos suficientes ni respuestas válidas.

En Windows nativo, utiliza el entorno virtual preparado en [`DEPLOYMENT_WINDOWS.md`](DEPLOYMENT_WINDOWS.md). Que el catálogo enumere una herramienta no demuestra que su ejecutable o sus dependencias estén disponibles en Windows.

### 5.1. Estado Ollama existente incompatible con la release

El bootstrap Git + Docker verifica el modelo contra `docker/supply-chain.lock.json`. Si coincide, reutiliza el modelo y muestra `MODEL_ALREADY_VALID=PASS`. Si el directorio Ollama está vacío, aprovisiona el modelo requerido. Si contiene datos pero la verificación falla, se detiene en lugar de borrar o sobrescribir silenciosamente ese estado.

Desde el checkout de la release seleccionada, con `CENTAURUS_DATA_ROOT` definido con el directorio de datos realmente utilizado, consulta la salida del verificador:

```bash
python3 scripts/verify_ollama_model.py \
  --models-root "$CENTAURUS_DATA_ROOT/ollama/models" \
  --supply-chain docker/supply-chain.lock.json
```

Resuelve la discrepancia seleccionando el directorio de datos correcto para esa release, restaurando el modelo esperado desde una copia verificada o eligiendo explícitamente un directorio nuevo y vacío para otra instalación. No borres automáticamente el directorio Ollama existente. Un directorio de datos separado no aísla por sí solo los nombres del proyecto/contenedores Compose ni habilita despliegues simultáneos.

Un fallo en la fase de modelo no implica que el bootstrap no haya cambiado nada: en ese punto ya se han actualizado la etiqueta local del Core y el propietario del directorio workspace. Conserva el error, revisa el estado resultante y utiliza la identidad de imagen registrada previamente si necesitas revertir. El bootstrap no revierte automáticamente esos cambios.

## 6. Logs y datos para el diagnóstico

En OVA/USB, el log operativo es `/workspace/logs/centaurus.log`. En Git + Docker se encuentra bajo el directorio persistente elegido. Desde el host, con `CENTAURUS_DATA_ROOT` definido con la ruta utilizada en el bootstrap:

```bash
tail -n 50 "$CENTAURUS_DATA_ROOT/workspace/logs/centaurus.log"
docker logs --tail 50 centaurus-ollama
```

El log del Core se crea al inicializar la aplicación. Si no existe, comprueba la ruta, los permisos y si el fallo ocurrió antes de esa inicialización. Los errores de fuentes y los artefactos de investigación se conservan por separado según [`STORAGE.md`](STORAGE.md).

Al comunicar una incidencia incluye modalidad, versión o identidad del artefacto, etapa, mensaje exacto e identificador de investigación si existe. Adjunta solo los fragmentos necesarios y revisa objetivos, datos personales y cualquier información sensible antes de compartirlos. Conserva una copia de resultados antes de realizar mantenimiento.
