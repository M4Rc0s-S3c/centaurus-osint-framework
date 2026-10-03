# Configuración

[Español](CONFIGURATION.md) | [English](CONFIGURATION.en.md)

[Inicio](../README.md) · [INSTALL.md](INSTALL.md) · [USER_GUIDE.md](USER_GUIDE.md)

## 1. Alcance

La configuración externa ajusta rutas, servicios, logs y límites de espera. Las reglas, los esquemas de conocimiento y las decisiones del Planner permanecen versionados en código.

El Core lee las variables al construir el runtime. Cambiar el entorno requiere iniciar una nueva ejecución. No existe un fichero de configuración de reglas que el analista deba editar.

## 2. Variables del Core

Estos son los valores por defecto de la ejecución directa del Core. Los tiempos se expresan en segundos.

| Variable | Valor por defecto | Uso |
| --- | --- | --- |
| `CENTAURUS_WORKSPACE` | `/workspace` | Raíz persistente de investigaciones y logs. |
| `CENTAURUS_LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` o `CRITICAL`. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Servicio de inferencia. |
| `OLLAMA_MODEL` | `qwen3:4b` | Modelo solicitado. |
| `OLLAMA_TIMEOUT` | `60` | Tiempo base del cliente Ollama. |
| `OLLAMA_INTERPRETATION_TIMEOUT` | Hereda `OLLAMA_TIMEOUT` | Interpretación LLM #1. |
| `OLLAMA_ANALYST_ASSISTANCE_TIMEOUT` | `300` | Asistencia LLM #2; independiente del tiempo base. |
| `OLLAMA_ANALYST_ASSISTANCE_NUM_CTX` | `8192` | Ventana de contexto de LLM #2. |
| `OLLAMA_ANALYST_ASSISTANCE_NUM_PREDICT` | Sin valor | Límite opcional de generación de LLM #2. |
| `CENTAURUS_WHOIS_TIMEOUT` | `10` | Adaptador WHOIS. |
| `CENTAURUS_RDAP_TIMEOUT` | `10` | Adaptador RDAP. |
| `CENTAURUS_CRTSH_TIMEOUT` | `30` | Adaptador crt.sh. |
| `CENTAURUS_DNSRECON_TIMEOUT` | `120` | Adaptador DNSRecon. |
| `CENTAURUS_SUBLIST3R_TIMEOUT` | `180` | Adaptador Sublist3r. |
| `CENTAURUS_THEHARVESTER_TIMEOUT` | `300` | Adaptador TheHarvester. |

Los campos de texto obligatorios no admiten valores vacíos. Los tiempos deben ser números positivos; los límites de contexto y generación deben ser enteros positivos. `OLLAMA_ANALYST_ASSISTANCE_NUM_PREDICT` admite ausencia o texto vacío para no enviar ese límite. El nivel de log se normaliza a mayúsculas.

Una configuración rechazada impide iniciar la investigación y la CLI termina con código `1`.

El perfil actual de LLM #2 fija además `think=false` y el proveedor envía `keep_alive=0`. Son ajustes de implementación versionados, no variables de entorno expuestas al analista. El timeout de `300` segundos, `num_ctx=8192` y el límite opcional de generación son los valores configurables de la tabla anterior.

En ejecución nativa, define `CENTAURUS_WORKSPACE` con una ruta absoluta donde pueda escribir el usuario del runtime. En Windows, sigue la preparación de ruta explícita de [`DEPLOYMENT_WINDOWS.md`](DEPLOYMENT_WINDOWS.md); `/workspace` no es una ubicación portable de Windows.

## 3. Git + Docker

El bootstrap utiliza `CENTAURUS_DATA_ROOT`; si no está definida, toma `${XDG_DATA_HOME:-$HOME/.local/share}/centaurus`. Crea `compose.env` con permisos `0600` y las rutas persistentes:

| Variable de despliegue | Valor generado por el bootstrap |
| --- | --- |
| `CENTAURUS_OLLAMA_HOST_DIR` | `<data-root>/ollama` |
| `CENTAURUS_WORKSPACE_HOST_DIR` | `<data-root>/workspace` |

Son rutas del host. Dentro del Core, Compose fija `CENTAURUS_WORKSPACE=/workspace` y `HOME=/tmp/centaurus`. Exportar otra ruta interna en el host no cambia esos valores literales.

Compose utiliza `http://centaurus-ollama:11434` como URL por defecto y fija el tiempo de interpretación por defecto en `60`. Por tanto, cambiar solo `OLLAMA_TIMEOUT` **no cambia** `OLLAMA_INTERPRETATION_TIMEOUT` en esta modalidad. Si se desea cambiar ambos, hay que especificarlos por separado.

Después del bootstrap, el administrador de Git + Docker puede añadir las variables interpoladas por Compose al `compose.env` generado. Hay que conservar sus dos rutas y usar siempre `--env-file` con ese fichero. Las variables exportadas en el shell pueden prevalecer sobre los valores del fichero; revisa el entorno antes de diagnosticar diferencias.

El bootstrap vuelve a generar `compose.env`. Conserva una copia de los ajustes antes de repetirlo y revisa qué opciones admite la versión seleccionada. Para iniciar, detener y consultar logs, sigue [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md).

Cambiar `OLLAMA_MODEL` no descarga ni valida un modelo nuevo: el aprovisionamiento y su identidad pertenecen a la cadena de suministro. Ollama monta el almacén de modelos en modo solo lectura durante el uso normal.

## 4. OVA y USB

La appliance utiliza configuración administrada y verificada por el broker de ejecución. Este limpia el entorno heredado y comprueba la identidad de Compose, del fichero de entorno y de la imagen Core.

Los ajustes exportados por el analista no se trasladan automáticamente al contenedor. Modificar los ficheros protegidos puede bloquear el arranque por discrepancia de integridad. Su mantenimiento corresponde al administrador de la appliance; el flujo normal sigue siendo `centaurus` desde una TTY.

## 5. Logs y diagnóstico

El log operativo se escribe en `<workspace>/logs/centaurus.log`, separado de los artefactos de conocimiento. Utiliza UTF-8, timestamps UTC y rotación de 5 MiB con tres copias de respaldo.

En Git + Docker, el workspace del host es la ruta generada bajo el directorio de datos; en la appliance es `/workspace`. Los logs pueden contener contexto operativo de las investigaciones: protege sus permisos y revisa su contenido antes de compartirlos.

Un timeout de LLM #2 no invalida el informe determinista ya persistido. Aumentar ese timeout puede permitir más tiempo de inferencia, pero no garantiza memoria suficiente ni una respuesta válida. La ventana de contexto y el límite de generación también afectan al consumo de recursos.

## 6. Referencias

- [`runtime.py`](../src/centaurus/config/runtime.py): variables y validación.
- [`compose.yml`](../docker/compose.yml): valores y montajes del despliegue.
- [`bootstrap_linux_release.sh`](../scripts/bootstrap_linux_release.sh): directorio persistente y aprovisionamiento.
- [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md): límites de confianza y controles.
