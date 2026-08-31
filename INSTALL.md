# CENTAURUS OSINT Framework

# Nota técnica: despliegue y uso mediante Git + Docker sobre Linux

**Versión:** v1.0  
**Fecha:** 29/08/2026  
**Estado:** NOTA TÉCNICA · MODALIDAD GIT + DOCKER LINUX · GUÍA OPERATIVA  
**Ámbito:** despliegue reproducible de CENTAURUS desde una copia de trabajo Git fijada a una revisión exacta sobre un host Linux con Docker Engine y Docker Compose  
**Distribución relacionada:** modalidad Git + Docker Linux; distinta de la OVA y del modo Windows nativo  

> **Naturaleza de la nota.** Este documento explica cómo obtener, construir, validar y utilizar CENTAURUS directamente desde Git sobre Linux mediante Docker. No sustituye al proceso formal de Release Factory/resellado de una OVA ni convierte una rama `main` mutable en una versión de entrega. La identidad de una instalación debe fijarse siempre mediante un commit o tag de versión concreto.

## 1. Objetivo y alcance

La modalidad Git + Docker permite reconstruir el entorno de ejecución de CENTAURUS a partir del repositorio versionado, sin necesidad de importar una OVA. El host Linux aporta kernel, sistema de archivos, Git, Python 3, Docker Engine y Docker Compose; el repositorio aporta el código del Core, ficheros de bloqueo de dependencias, definición Compose, cadena de suministro, scripts de inicialización y verificadores.

La arquitectura resultante conserva las mismas fronteras fundamentales del producto:

- `centaurus-core` contiene el framework completo y las herramientas OSINT integradas;
- `centaurus-ollama` ejecuta el LLM local;
- las investigaciones y logs se persisten en un directorio del host;
- el modelo Ollama se conserva fuera del contenedor;
- el Core se ejecuta bajo demanda, no como servicio persistente;
- Docker no cambia los contratos de dominio ni la autoridad del Core, RuleEngine o Evidence/Report.

Esta nota cubre:

- prerrequisitos del host Linux;
- clonado y fijación de una versión Git exacta;
- directorio de datos persistentes;
- ejecución de `bootstrap_linux_release.sh`;
- construcción determinista de `centaurus-core`;
- aprovisionamiento/verificación de Ollama y `qwen3:4b`;
- operación interactiva y ejecución puntual con Docker Compose;
- localización de investigaciones y logs;
- endurecimiento y redes del entorno de ejecución;
- actualización, parada, reversión operativa básica y resolución de problemas;
- criterios de aceptación y límites de soporte.

## 2. Estado de soporte y frontera de la modalidad

| Área | Git + Docker Linux | Observación |
|---|---|---|
| Host Linux | SOPORTADO / CERTIFICADO EN G2 | La certificación G2 se realizó sobre Debian GNU/Linux 13.6 amd64. |
| Git | REQUERIDO | La copia de trabajo identifica el código de la versión. |
| Python 3 en host | REQUERIDO PARA INICIALIZACIÓN | No ejecuta el Core productivo; genera/verifica artefactos. |
| Docker Engine | REQUERIDO | Debe ser accesible por el usuario que ejecuta la inicialización. |
| Docker Compose plugin | REQUERIDO | Se utiliza `docker compose`. |
| Core | CONTENEDORIZADO | Imagen local `centaurus-core:local`. |
| Ollama | CONTENEDORIZADO | Imagen fijada por digest; no requiere Ollama instalado en el host. |
| Modelo | PERSISTENTE EN HOST | `qwen3:4b`, identidad verificada contra cadena de suministro. |
| Seis herramientas OSINT | INCLUIDAS EN LA IMAGEN | DNSRecon, Sublist3r y TheHarvester usan venv aislados dentro de la imagen. |
| Workspace | PERSISTENTE EN HOST | Montaje bind configurable hacia `/workspace`. |
| Windows Docker Desktop | NO CERTIFICADO | La modalidad formal es Linux. |
| macOS / Docker Desktop | NO CERTIFICADO | No se declara paridad. |
| GPU | OPCIONAL, NO BASELINE | La baseline es CPU; la GPU se documenta en una nota separada. |

**Decisión operativa:** para una instalación nueva, usar un host Linux dedicado o controlado, fijar un commit/tag de versión exacto y ejecutar la inicialización oficial. No construir directamente desde una copia de trabajo con cambios ni desde una rama móvil sin congelar identidad.

## 3. Arquitectura resultante

```text
HOST LINUX
│
├── checkout Git CENTAURUS
│   ├── docker/Dockerfile
│   ├── docker/compose.yml
│   ├── docker/supply-chain.lock.json
│   ├── requirements-*.lock
│   └── scripts/bootstrap_linux_release.sh
│
├── CENTAURUS_DATA_ROOT
│   ├── compose.env                 # 0600
│   ├── compose.rendered.yml
│   ├── ollama/
│   │   └── models/                 # qwen3:4b persistente
│   └── workspace/
│       ├── logs/centaurus.log
│       └── investigations/<id>/...
│
└── Docker Engine
    │
    ├── centaurus-ollama
    │   ├── red centaurus-llm-network (internal=true)
    │   ├── sin puerto publicado al host
    │   └── /root/.ollama <- bind RO del host
    │
    └── centaurus-core:local
        ├── ejecución efímera mediante docker compose run --rm
        ├── UID:GID 1000:1000
        ├── rootfs read-only
        ├── /tmp tmpfs efímero
        ├── /workspace <- bind RW del host
        ├── red LLM interna
        └── red egress para fuentes OSINT
```

El Core es el único servicio que necesita egress externo. Ollama queda aislado en la red LLM interna y `OLLAMA_NO_CLOUD=1` permanece activo.

## 4. Baseline utilizada para esta nota

Fotografía de código revisada para preparar esta guía:

```text
ARTEFACTO=centaurus-osint-framework_29_08_26_14_23.zip
SIZE_BYTES=1989931
SHA256=A9FDFB5E015EDE31D7AB8FCA04E5D00BF5C097CE0864DD93C9C9B09DCC068195
GIT_HEAD=fe6ae9c9d81362d456f4cb35f5700a535d13b4bc
GIT_SUBJECT=feat: harden Ollama analyst assistance runtime
PROJECT_VERSION=0.4.0-dev
REQUIRES_PYTHON=>=3.12
CORE_IMAGE=centaurus-core:local
OLLAMA_MODEL=qwen3:4b
```

La certificación histórica G2 de la modalidad Git + Docker se cerró sobre otra identidad de versión. Por ello, **los hashes/commit de G2 no deben reutilizarse como identidad de una versión posterior**. En una instalación real, `<RELEASE_COMMIT>` debe sustituirse por el commit/tag autoritativo de la versión que se vaya a desplegar.

La fotografía actual mantiene la corrección OLLAMA-D2 en Compose:

```text
OLLAMA_INTERPRETATION_TIMEOUT=60
OLLAMA_ANALYST_ASSISTANCE_TIMEOUT=300
OLLAMA_ANALYST_ASSISTANCE_NUM_CTX=8192
```

## 5. Prerrequisitos del host

La inicialización aplica una comprobación previa con cierre ante fallo y exige:

```bash
command -v git
command -v python3
command -v docker
[ "$(uname -s)" = "Linux" ]
docker info
docker compose version
```

Requisitos prácticos:

1. Linux amd64/x86-64 para reproducir la plataforma certificada.
2. Git disponible.
3. Python 3 disponible en el host.
4. Docker Engine instalado y activo.
5. Plugin Docker Compose disponible como `docker compose`.
6. El usuario del despliegue debe poder ejecutar `docker info` sin elevar privilegios dentro del flujo certificado.
7. Acceso a Internet durante el primer proceso de construcción/aprovisionamiento para obtener imágenes, dependencias fijadas y el modelo Ollama.
8. Espacio suficiente para imágenes Docker, caché de construcción, modelo y workspace. Como referencia de proyecto, 8 GiB de RAM y del orden de 30 GiB de almacenamiento proporcionan margen razonable para la baseline CPU y datos de investigación.

**Frontera administrativa:** pertenecer al grupo `docker` concede una capacidad elevada sobre el host. El socket Docker no se monta dentro de `centaurus-core`; el acceso Docker pertenece exclusivamente al plano de administración del host.

## 6. Obtener y congelar el código de la versión

Clonar el repositorio autorizado:

```bash
git clone <REPOSITORY_URL> centaurus-osint-framework
cd centaurus-osint-framework
```

Actualizar referencias y seleccionar una versión exacta:

```bash
git fetch --tags --prune
git checkout --detach <RELEASE_COMMIT>
```

Verificar identidad y limpieza:

```bash
git rev-parse HEAD
git status --porcelain --untracked-files=all
```

El segundo comando debe quedar sin salida.

Congelar la expectativa para la inicialización:

```bash
export CENTAURUS_RELEASE_COMMIT="<RELEASE_COMMIT>"
test "$(git rev-parse HEAD)" = "$CENTAURUS_RELEASE_COMMIT"
```

`CENTAURUS_RELEASE_COMMIT` es una **aserción**, no una instrucción de cambio de revisión Git. Si HEAD no coincide, la inicialización se detiene.

### 6.1 Qué no hacer

```text
NO -> ejecutar bootstrap con cambios locales
NO -> ejecutar bootstrap con untracked files
NO -> considerar "main" como identidad suficiente
NO -> embebir credenciales Git dentro del repositorio
NO -> copiar .git dentro de la imagen Core
```

Para una entrega reproducible se recomienda detached HEAD o un tag inmutable que resuelva a un commit conocido.

## 7. Directorio persistente de datos

Si no se define nada, la inicialización usa:

```text
${XDG_DATA_HOME:-$HOME/.local/share}/centaurus
```

Se recomienda fijarlo explícitamente en servidores o estaciones donde se quiera conocer de antemano la ubicación:

```bash
export CENTAURUS_DATA_ROOT="$HOME/.local/share/centaurus"
```

También puede apuntar a otra ruta dedicada:

```bash
export CENTAURUS_DATA_ROOT="/srv/centaurus"
```

La inicialización crea:

```text
$CENTAURUS_DATA_ROOT/
├── compose.env
├── compose.rendered.yml
├── ollama/
└── workspace/
```

`compose.env` contiene únicamente las rutas host de Ollama y workspace y se crea con modo `0600`.

**Importante:** la inicialización ajusta el propietario del workspace a `1000:1000` mediante una ejecución puntual como root dentro de la imagen. Por ello, `CENTAURUS_DATA_ROOT` debe apuntar a un directorio dedicado a CENTAURUS y no a una carpeta compartida que contenga otros datos.

## 8. Inicialización oficial

Con la copia de trabajo limpia, versión fijada y directorio raíz de datos decidido:

```bash
./scripts/bootstrap_linux_release.sh
```

El script no es un simple `docker compose up`. Ejecuta una cadena de control:

```text
PRECHECK HOST/GIT
    ↓
CREAR DATA ROOT + compose.env
    ↓
GENERAR BUNDLE DETERMINISTA DEL CORE
    ↓
EXTRAER EN DIRECTORIO TEMPORAL SEGURO
    ↓
BUILD centaurus-core:g2-candidate --no-cache
    ↓
pip check Core + DNSRecon + Sublist3r + TheHarvester
    ↓
TAG centaurus-core:local
    ↓
AJUSTAR /workspace A UID:GID 1000:1000
    ↓
VERIFICAR / APROVISIONAR qwen3:4b
    ↓
RENDERIZAR COMPOSE
    ↓
LEVANTAR centaurus-ollama
    ↓
VERIFICAR DIGEST EFECTIVO OLLAMA
    ↓
SMOKE centaurus capabilities
    ↓
LINUX_BOOTSTRAP=PASS
```

### 8.1 Paquete de construcción determinista del Core

La inicialización invoca:

```bash
python3 scripts/create_core_build_bundle.py
```

El resultado es:

```text
dist/centaurus-core-build_v1.0.zip
```

La construcción de imagen utiliza ese paquete de construcción, no el árbol Git completo. Esto evita introducir `.git`, tests, documentación o residuos de desarrollo en la imagen productiva.

### 8.2 Aislamiento de herramientas

El Dockerfile instala el Core y crea tres entornos virtuales independientes:

```text
/opt/centaurus-tools/dnsrecon
/opt/centaurus-tools/sublist3r
/opt/centaurus-tools/theharvester
```

Después expone los ejecutables mediante enlaces en `/usr/local/bin`. Esta separación evita mezclar los árboles de dependencias incompatibles de herramientas de terceros dentro del entorno Python del Core.

### 8.3 Cadena de suministro

`docker/supply-chain.lock.json` fija, entre otros elementos:

- imagen base Python por digest;
- imagen Ollama por digest;
- versión/entorno de ejecución de Ollama;
- fuentes/versiones/hashes de DNSRecon, Sublist3r y TheHarvester;
- backends de construcción;
- identidad del modelo `qwen3:4b` y blobs asociados.

La inicialización construye con `--no-cache` y ejecuta `pip check` con red deshabilitada tras la construcción para comprobar coherencia de los cuatro entornos Python.

## 9. Provisionado del modelo Ollama

El modelo no se descarga dentro de la imagen Core. Se conserva en:

```text
$CENTAURUS_DATA_ROOT/ollama
```

Primero, la inicialización intenta verificar el modelo existente mediante:

```bash
python3 scripts/verify_ollama_model.py \
  --models-root "$CENTAURUS_DATA_ROOT/ollama/models" \
  --supply-chain docker/supply-chain.lock.json
```

Si la identidad ya coincide:

```text
MODEL_ALREADY_VALID=PASS
```

Si el directorio está vacío, la inicialización levanta temporalmente un contenedor Ollama con el montaje bind en escritura, ejecuta:

```text
ollama pull qwen3:4b
```

lo detiene y verifica la identidad del modelo. En el entorno de ejecución normal de Compose, el directorio se monta **solo lectura** en `/root/.ollama`.

### 9.1 Estado no compatible

Si existe contenido en el directorio Ollama pero no coincide con la identidad exigida por la versión, la inicialización se detiene. No borra ni sobrescribe silenciosamente un estado existente.

La resolución correcta es una de estas:

- seleccionar el directorio raíz de datos correcto para esa versión;
- restaurar el modelo esperado;
- utilizar un directorio raíz de datos nuevo y vacío si se desea una instalación paralela.

No eliminar el directorio Ollama de una instalación existente sin una decisión explícita.

## 10. Resultado esperado de la inicialización

El cierre correcto debe mostrar, como mínimo:

```text
CORE_IMAGE_ID=sha256:...
OLLAMA_IMAGE_ID=sha256:...
OLLAMA_CONFIG_IMAGE=ollama/ollama@sha256:...
CENTAURUS_ENV_FILE=<ruta>/compose.env
LINUX_BOOTSTRAP=PASS
```

Comprobaciones adicionales:

```bash
DATA_ROOT="${CENTAURUS_DATA_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/centaurus}"
ENV_FILE="$DATA_ROOT/compose.env"

ls -l "$ENV_FILE"
docker image inspect centaurus-core:local --format 'ID={{.Id}} USER={{.Config.User}} CMD={{json .Config.Cmd}}'
docker inspect centaurus-ollama --format 'IMAGE={{.Image}} CONFIG={{.Config.Image}} STATUS={{.State.Status}}'
docker compose --env-file "$ENV_FILE" -f docker/compose.yml ps
```

Resultado conceptual esperado:

```text
centaurus-core:local -> existe; USER 1000:1000; CMD ["centaurus","shell"]
centaurus-ollama    -> running
host port 11434     -> NO PUBLICADO
workspace           -> persistente en host
modelo              -> presente y verificado
```

## 11. Ejecutar CENTAURUS

Definir las rutas de operación en la sesión:

```bash
DATA_ROOT="${CENTAURUS_DATA_ROOT:-${XDG_DATA_HOME:-$HOME/.local/share}/centaurus}"
ENV_FILE="$DATA_ROOT/compose.env"
COMPOSE="docker/compose.yml"
```

### 11.1 Shell conversacional

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE" \
  --profile framework \
  run --rm centaurus-core
```

La imagen tiene como comando por defecto:

```text
CMD ["centaurus", "shell"]
```

Por tanto, el usuario obtiene el prompt interactivo de CENTAURUS. Para salir del shell se utiliza `/exit`.

### 11.2 Ayuda y capacidades

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE" \
  --profile framework \
  run -T --rm --no-deps centaurus-core \
  centaurus --help
```

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE" \
  --profile framework \
  run -T --rm --no-deps centaurus-core \
  centaurus capabilities
```

`--no-deps` solo es apropiado para comandos que no necesitan Ollama. Para investigaciones reales, mantener el servicio Ollama disponible.

### 11.3 Investigación puntual

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f "$COMPOSE" \
  --profile framework \
  run --rm centaurus-core \
  centaurus investigate "<PETICION_EN_LENGUAJE_NATURAL>"
```

Utilizar únicamente objetivos sobre los que exista autorización para realizar la investigación.

## 12. Localizar investigaciones, reports y logs

La ruta física del workspace es:

```text
$CENTAURUS_DATA_ROOT/workspace
```

Investigaciones:

```text
$CENTAURUS_DATA_ROOT/workspace/investigations/<investigation-id>/
```

Contenido típico:

```text
<investigation-id>/
├── evidences/
│   ├── raw/
│   └── normalized/
├── findings/
└── reports/
    ├── report.json
    └── report.md
```

Log operacional:

```text
$CENTAURUS_DATA_ROOT/workspace/logs/centaurus.log
```

Comandos útiles:

```bash
tail -n 100 "$DATA_ROOT/workspace/logs/centaurus.log"
find "$DATA_ROOT/workspace/investigations" -maxdepth 2 -type d | sort
```

Logs de Ollama:

```bash
docker logs --tail 100 centaurus-ollama
```

## 13. Configuración vigente del entorno de ejecución

El Compose revisado publica hacia el Core los siguientes defaults principales:

| Variable | Default | Función |
|---|---:|---|
| `CENTAURUS_WORKSPACE` | `/workspace` | Ruta interna del montaje bind persistente. |
| `CENTAURUS_LOG_LEVEL` | `INFO` | Nivel de logging. |
| `OLLAMA_BASE_URL` | `http://centaurus-ollama:11434` | Endpoint interno del LLM. |
| `OLLAMA_MODEL` | `qwen3:4b` | Modelo local. |
| `OLLAMA_TIMEOUT` | `60` | Timeout general. |
| `OLLAMA_INTERPRETATION_TIMEOUT` | `60` | LLM #1. |
| `OLLAMA_ANALYST_ASSISTANCE_TIMEOUT` | `300` | LLM #2. |
| `OLLAMA_ANALYST_ASSISTANCE_NUM_CTX` | `8192` | Contexto de LLM #2. |
| `CENTAURUS_WHOIS_TIMEOUT` | `10` | WHOIS. |
| `CENTAURUS_RDAP_TIMEOUT` | `10` | RDAP. |
| `CENTAURUS_CRTSH_TIMEOUT` | `30` | crt.sh. |
| `CENTAURUS_DNSRECON_TIMEOUT` | `120` | DNSRecon. |
| `CENTAURUS_SUBLIST3R_TIMEOUT` | `180` | Sublist3r. |
| `CENTAURUS_THEHARVESTER_TIMEOUT` | `300` | TheHarvester. |

No cambiar modelo, timeouts o contexto durante una instalación básica salvo que exista una necesidad concreta y se repitan las validaciones correspondientes.

## 14. Endurecimiento del entorno de ejecución

### 14.1 `centaurus-core`

El Compose aplica:

```text
USER=1000:1000                    # definido en imagen
read_only=true
/tmp=tmpfs rw,nosuid,nodev,noexec,size=256m
cap_drop=ALL
no-new-privileges=true
pids_limit=256
init=true
HOME=/tmp/centaurus
/workspace=RW bind persistente
```

`HOME=/tmp/centaurus` es deliberado: algunas herramientas externas necesitan escribir configuración/estado efímero en HOME. No debe hacerse writable `/home/centaurus` como atajo.

### 14.2 `centaurus-ollama`

```text
OLLAMA_NO_CLOUD=1
/root/.ollama=bind read-only
cap_drop=ALL
no-new-privileges=true
pids_limit=512
ports publicados=NINGUNO
red=solo centaurus-llm-network
```

### 14.3 Redes

```text
centaurus-llm-network
  internal=true
  miembros: Core + Ollama

centaurus-egress-network
  miembros: solo Core
  finalidad: acceso a fuentes OSINT
```

No añadir Ollama a la red de egress ni publicar `11434` en el host para facilitar diagnósticos. Los diagnósticos deben realizarse desde Docker/Compose.

## 15. Verificación rápida de endurecimiento

```bash
docker inspect centaurus-core:local \
  --format 'USER={{.Config.User}} CMD={{json .Config.Cmd}}'
```

El Core normalmente no queda como contenedor persistente porque se ejecuta con `run --rm`. Para inspeccionar el Compose renderizado:

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f docker/compose.yml \
  --profile framework \
  config > /tmp/centaurus-compose-check.yml
```

Comprobar Ollama:

```bash
docker port centaurus-ollama
```

Resultado esperado: sin salida.

Comprobar red interna:

```bash
docker network inspect centaurus_centaurus-llm-network \
  --format 'Internal={{.Internal}}'
```

El nombre real de la red puede variar si se cambia el nombre del proyecto Compose; `docker network ls` permite localizarla.

## 16. Arranque, parada y reanudación

### Arrancar/recrear Ollama

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f docker/compose.yml \
  up -d --force-recreate centaurus-ollama
```

### Estado

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f docker/compose.yml \
  ps
```

### Parada de la pila Compose

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f docker/compose.yml \
  --profile framework \
  down
```

`down` elimina contenedores/redes del proyecto, pero no borra el workspace ni el modelo almacenados en `CENTAURUS_DATA_ROOT`.

## 17. Actualizar a una versión posterior

No hacer `git pull && bootstrap` sin fijar identidad.

Flujo recomendado:

```bash
cd <RUTA_CHECKOUT_CENTAURUS>
git fetch --tags --prune
git status --porcelain --untracked-files=all
```

Si existe cualquier salida, detener y reconciliar la copia de trabajo.

Seleccionar la nueva versión:

```bash
git checkout --detach <NEW_RELEASE_COMMIT>
export CENTAURUS_RELEASE_COMMIT="<NEW_RELEASE_COMMIT>"
test "$(git rev-parse HEAD)" = "$CENTAURUS_RELEASE_COMMIT"
```

Mantener o cambiar `CENTAURUS_DATA_ROOT` de forma explícita y ejecutar:

```bash
./scripts/bootstrap_linux_release.sh
```

La inicialización vuelve a generar el paquete de construcción, reconstruye una candidata `--no-cache`, ejecuta `pip check`, etiqueta `centaurus-core:local`, verifica el modelo y recrea Ollama.

### 17.1 Precaución de reversión

El procedimiento básico de inicialización valida una candidata antes de etiquetarla como `centaurus-core:local`, pero no sustituye al flujo completo de promoción/reversión de Release Factory. Para cambios críticos de versión, preservar previamente la identidad de la imagen estable o utilizar el procedimiento oficial de candidata -> validación -> reversión -> promoción documentado por el proyecto.

No eliminar una imagen estable ni un directorio raíz de datos hasta haber confirmado la nueva instalación.

## 18. Copia de seguridad y retirada

El estado que realmente debe preservarse es:

```text
$CENTAURUS_DATA_ROOT/workspace
$CENTAURUS_DATA_ROOT/ollama
$CENTAURUS_DATA_ROOT/compose.env
```

Para una copia de seguridad coherente, detener primero las ejecuciones activas. El Core es efímero, pero Ollama puede mantenerse en ejecución; si se desea una copia fría del modelo, detener Compose antes de copiar.

Retirada de contenedores/redes:

```bash
docker compose \
  --env-file "$ENV_FILE" \
  -f docker/compose.yml \
  --profile framework \
  down
```

Las imágenes pueden eliminarse posteriormente si no son necesarias:

```bash
docker image rm centaurus-core:g2-candidate centaurus-core:local
```

**No ejecutar** un borrado del directorio raíz de datos salvo que se quiera destruir investigaciones y modelo persistentes.

## 19. Resolución de problemas

| Síntoma | Causa probable | Acción |
|---|---|---|
| `missing prerequisite: git/python3/docker` | Host incompleto | Instalar el prerrequisito y repetir. |
| `Git + Docker distribution is certified on Linux only` | Host no Linux | Esta modalidad no está certificada allí. |
| `Docker Engine is not available to the current user` | Servicio parado o permisos insuficientes | Verificar `systemctl status docker`, `docker info` y política del host. |
| `release checkout must be clean before bootstrap` | Cambios/ficheros no rastreados en Git | No construir; limpiar/reconciliar conscientemente la copia de trabajo. |
| `checkout ... does not match CENTAURUS_RELEASE_COMMIT` | Identidad equivocada | Seleccionar el commit correcto. |
| La construcción falla descargando dependencias | Red/cadena de suministro/proveedor externo | No promover; conservar el error y verificar conectividad/artefactos. |
| `pip check` falla | Entorno candidato inconsistente | NO-GO; no usar `centaurus-core:local` nuevo. |
| Estado Ollama existente no coincide | Directorio raíz de datos de otra versión o modelo modificado | Usar directorio raíz de datos correcto/restaurar; no borrar automáticamente. |
| `centaurus-ollama` no arranca | Imagen/modelo/configuración | `docker logs centaurus-ollama` y `docker inspect`. |
| CENTAURUS no alcanza Ollama | Red LLM/servicio | Revisar Compose y estado de `centaurus-ollama`; no publicar 11434 como atajo. |
| Error de escritura en workspace | propietario/permisos | Verificar UID/GID y que el montaje bind del host sea el generado por la inicialización. |
| `HOME`/EROFS en herramienta externa | Sobrescritura de HOME perdida | Confirmar `HOME=/tmp/centaurus` y tmpfs; no relajar rootfs RO. |
| Disco crece tras construcciones repetidas | caché de construcción/imágenes históricas | Auditar `docker system df`/`docker builder du`; usar limpieza controlada, no `docker system prune` indiscriminado. |

## 20. Criterios de aceptación de una instalación

| Hito | Objetivo | Criterio PASS |
|---|---|---|
| GD-G0 HOST | Prerrequisitos | Linux + Git + Python3 + Docker + Compose operativos. |
| GD-G1 GIT | Identidad | HEAD = versión autorizada y copia de trabajo limpia. |
| GD-G2 DATA | Persistencia | Directorio raíz de datos dedicado, rutas conocidas, `compose.env` 0600. |
| GD-G3 CONSTRUCCIÓN | Core | Paquete de construcción generado, candidata construida, cuatro `pip check` PASS. |
| GD-G4 MODEL | LLM | `qwen3:4b` exacto verificado contra cadena de suministro. |
| GD-G5 COMPOSE | Entorno de ejecución | Compose renderiza, Ollama en ejecución y digest correcto. |
| GD-G6 SECURITY | Endurecimiento | Ollama sin puerto publicado en el host; Core usuario no root / solo lectura; redes correctas. |
| GD-G7 CLI | Operación | `centaurus --help` y `centaurus capabilities` PASS. |
| GD-G8 PERSISTENCE | Workspace | escritura/lectura bajo bind host; logs e investigations localizables. |
| GD-G9 FUNCTIONAL | Uso | una investigación autorizada completa o PARTIAL solo por causas externas justificadas. |

Para una simple instalación técnica puede cerrarse hasta GD-G8. Para declarar aceptación funcional del host concreto debe ejecutarse GD-G9 con un objetivo autorizado y conservar la evidencia fuera de esta nota genérica.

## 21. Diferencias respecto de otros modos de despliegue

### Frente a OVA

```text
Git + Docker:
  host Linux preparado por el usuario
  copia de trabajo Git presente
  construcción reproducible local
  directorio raíz de datos configurable

OVA:
  appliance Debian preconstruida
  operación normal sin copia de trabajo Git
  imagen/Compose sellados por versión
  integración de host/appliance específica
```

No se debe convertir la OVA en un entorno Git simplemente porque esta modalidad utilice Git. Son rutas de distribución diferentes.

### Frente a Windows nativo

```text
Git + Docker Linux:
  seis herramientas empaquetadas
  entornos de ejecución de herramientas aislados
  Ollama en contenedor
  endurecimiento Docker aplicado
  modalidad formal de distribución

Windows nativo:
  Core/CLI/Ollama local pueden funcionar sin Docker
  pueden faltar entornos de ejecución externos
  el endurecimiento Docker no existe
  útil para desarrollo/uso local, no equivalente a esta modalidad
```

## 22. Referencias internas del proyecto

- `CENTAURUS_Git_Docker_Especificacion_Tecnica_Operativa_v1.1_24-08-2026.docx`.
- `CENTAURUS_Git_Docker_Resumen_Ejecutivo_Verificacion_v1.0_24-08-2026.docx`.
- `Docker-Despliegue-Runbook_v1.9_27-08-2026_CONSOLIDADO.docx`.
- `docker/Dockerfile` de la fotografía de código 29/08/2026.
- `docker/compose.yml` de la fotografía de código 29/08/2026.
- `docker/supply-chain.lock.json`.
- `scripts/bootstrap_linux_release.sh`.
- `scripts/create_core_build_bundle.py`.
- `scripts/verify_ollama_model.py`.
- Nota técnica GPU de Ollama para la modalidad Git + Docker.

## 23. Anexo A — instalación rápida

Sustituir `<REPOSITORY_URL>` y `<RELEASE_COMMIT>` por los valores autorizados:

```bash
git clone <REPOSITORY_URL> centaurus-osint-framework
cd centaurus-osint-framework

git fetch --tags --prune
git checkout --detach <RELEASE_COMMIT>

test -z "$(git status --porcelain --untracked-files=all)"
export CENTAURUS_RELEASE_COMMIT="<RELEASE_COMMIT>"
export CENTAURUS_DATA_ROOT="$HOME/.local/share/centaurus"

./scripts/bootstrap_linux_release.sh

DATA_ROOT="$CENTAURUS_DATA_ROOT"
ENV_FILE="$DATA_ROOT/compose.env"

docker compose \
  --env-file "$ENV_FILE" \
  -f docker/compose.yml \
  --profile framework \
  run --rm centaurus-core
```

Comprobación posterior:

```bash
docker inspect centaurus-ollama \
  --format 'IMAGE={{.Image}} CONFIG={{.Config.Image}} STATUS={{.State.Status}}'

docker port centaurus-ollama

tail -n 50 "$CENTAURUS_DATA_ROOT/workspace/logs/centaurus.log" 2>/dev/null || true
```

## 24. Estado

```text
GIT_DOCKER_LINUX_MODE=SUPPORTED
G2_HISTORICAL_CERTIFICATION=CLOSED_PASS
CERTIFIED_REFERENCE_PLATFORM=DEBIAN_13_6_AMD64
CURRENT_NOTE_CODE_SNAPSHOT=fe6ae9c9d81362d456f4cb35f5700a535d13b4bc
RELEASE_IDENTITY_MUST_BE_PINNED=YES
DOCKER_ENGINE_REQUIRED=YES
DOCKER_COMPOSE_PLUGIN_REQUIRED=YES
HOST_PYTHON3_REQUIRED_FOR_BOOTSTRAP=YES
HOST_OLLAMA_INSTALL_REQUIRED=NO
OLLAMA_CONTAINERIZED=YES
OLLAMA_HOST_PORT_REQUIRED=NO
CORE_RUNTIME_USER=1000:1000
CORE_READ_ONLY_ROOTFS=YES
CORE_EXECUTION_MODEL=ON_DEMAND_EPHEMERAL
TOOL_RUNTIME_ISOLATION=YES
PERSISTENCE_OUTSIDE_CONTAINERS=YES
WINDOWS_DOCKER_DESKTOP_CERTIFIED=NO
MACOS_DOCKER_CERTIFIED=NO
GPU_REQUIRED=NO
DOCUMENT_STATUS=TECHNICAL_DEPLOYMENT_GUIDE
```
