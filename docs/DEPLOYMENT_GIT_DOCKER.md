# Despliegue Git + Docker sobre Linux

[Español](DEPLOYMENT_GIT_DOCKER.md) | [English](DEPLOYMENT_GIT_DOCKER.en.md)

[Inicio](../README.md) · [INSTALL.md](INSTALL.md) · [USER_GUIDE.md](USER_GUIDE.md)

Esta guía describe el despliegue desde código fuente sobre un host Linux. La OVA preconstruida es la distribución principal de CENTAURUS; consulta [`INSTALL.md`](INSTALL.md) para elegir modalidad.

Utiliza una release/tag concreta para un despliegue reproducible. Release pública: [v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0).

## 1. Requisitos

Host Linux con:

- Git;
- Python 3;
- Docker Engine;
- Docker Compose (`docker compose`);
- acceso Docker para el usuario de despliegue;
- acceso a Internet durante el primer aprovisionamiento cuando deban descargarse imágenes, dependencias o el modelo LLM;
- espacio suficiente para imágenes, caché, modelo y workspace.

La modalidad formal de Git + Docker está orientada a Linux.

Windows nativo puede utilizarse para desarrollo y ejecución local del Core, pero no se presenta como equivalente a la distribución completa Linux + Docker.

## 2. Arquitectura del despliegue

```text
HOST LINUX
│
├── checkout Git CENTAURUS
│   ├── docker/
│   ├── requirements-*.lock
│   └── scripts/bootstrap_linux_release.sh
│
├── CENTAURUS_DATA_ROOT
│   ├── compose.env
│   ├── compose.rendered.yml
│   ├── ollama/
│   └── workspace/
│
└── Docker Engine
    ├── centaurus-ollama
    └── centaurus-core:local
```

Principios:

- `centaurus-core` contiene el framework y las herramientas integradas;
- `centaurus-ollama` proporciona el LLM local;
- el Core se ejecuta bajo demanda;
- el modelo Ollama persiste fuera de la imagen;
- el workspace persiste fuera del contenedor;
- Ollama no necesita publicar su puerto al host en la modalidad normal.

## 3. Obtener el código

```bash
git clone https://github.com/M4Rc0s-S3c/centaurus-osint-framework.git
cd centaurus-osint-framework
```

Actualizar referencias:

```bash
git fetch --tags --prune
```

Para desplegar la release pública actual:

```bash
git checkout --detach v1.0.0
```

Verificar:

```bash
git rev-parse HEAD
git status --porcelain --untracked-files=all
```

El segundo comando debe quedar sin salida.

También puede fijarse explícitamente el commit esperado:

```bash
export CENTAURUS_RELEASE_COMMIT="$(git rev-parse HEAD)"
```

`CENTAURUS_RELEASE_COMMIT` actúa como aserción de identidad para la inicialización.

## 4. Qué no hacer

```text
NO → ejecutar bootstrap con cambios locales
NO → ejecutar bootstrap con untracked files
NO → utilizar una rama móvil como única identidad de release
NO → introducir credenciales Git en el repositorio
NO → copiar .git dentro de la imagen Core
```

## 5. Directorio persistente

Si no se define otra ubicación, el bootstrap utiliza el directorio de datos previsto por el script.

Para fijarlo explícitamente:

```bash
export CENTAURUS_DATA_ROOT="$HOME/.local/share/centaurus"
```

En un servidor puede utilizarse una ruta dedicada:

```bash
export CENTAURUS_DATA_ROOT="/srv/centaurus"
```

El directorio se utiliza para:

```text
$CENTAURUS_DATA_ROOT/
├── compose.env
├── compose.rendered.yml
├── ollama/
└── workspace/
```

No utilices como `CENTAURUS_DATA_ROOT` una carpeta compartida que contenga otros datos sin revisar previamente permisos/ownership.

## 6. Inicialización oficial

Con el checkout limpio:

```bash
./scripts/bootstrap_linux_release.sh
```

El bootstrap realiza controles de host/Git, prepara la raíz persistente, construye la imagen Core, valida dependencias, aprovisiona/verifica Ollama y realiza comprobaciones de runtime.

No debe sustituirse por un `docker compose up` manual si se busca reproducir la modalidad documentada.

## 7. Cadena de suministro

El repositorio incluye locks de dependencias y una cadena de suministro bajo `docker/`.

La construcción debe utilizar las versiones/digests fijados por el repositorio de la release seleccionada.

Los entornos de herramientas que requieren dependencias incompatibles se aíslan en la imagen de ejecución.

## 8. Modelo Ollama

Modelo utilizado:

```text
qwen3:4b
```

El modelo se almacena de forma persistente fuera del contenedor de aplicación.

La inicialización verifica/aprovisiona el modelo según los scripts y la cadena de suministro versionados.

## 9. Arranque, uso y parada

Los siguientes comandos se ejecutan desde el checkout utilizado para el bootstrap, en el host Linux. Usa exactamente el directorio de datos elegido en el paso 5. En cada nueva terminal, prepara las rutas; si elegiste otra ubicación, sustituye el valor del ejemplo:

```bash
export CENTAURUS_DATA_ROOT="$HOME/.local/share/centaurus"
CENTAURUS_ENV_FILE="$CENTAURUS_DATA_ROOT/compose.env"
```

Antes de continuar, comprueba que `CENTAURUS_ENV_FILE` apunta al fichero generado por el bootstrap. No uses un fichero vacío ni omitas `--env-file`: las rutas por defecto de Compose pueden apuntar a otro workspace.

Abre la sesión interactiva del Core:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework run --rm centaurus-core
```

El comando por defecto abre `centaurus shell`. Sigue [`USER_GUIDE.md`](USER_GUIDE.md) para usar la sesión y salir. El Core se elimina al terminar; el workspace del host se conserva.

Para consultar capacidades y ayuda sin iniciar una investigación ni arrancar dependencias:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework run -T --rm --no-deps centaurus-core centaurus capabilities --rules
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework run -T --rm --no-deps centaurus-core centaurus --help
```

Ejecuta una sesión cada vez. Para detener el despliegue, sal antes de todas las sesiones del Core y después ejecuta:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml --profile framework down
```

Los directorios persistentes del host no se borran. Para volver a iniciar el servicio LLM:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml up -d centaurus-ollama
```

Después puede abrirse otra sesión del Core con el comando anterior. Si el servicio acaba de arrancar, espera a que esté disponible antes de utilizar funciones LLM.

Para consultar logs y diagnosticar incidencias, sigue [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md). Los ajustes admitidos están en [`CONFIGURATION.md`](CONFIGURATION.md).

## 10. Workspace

Las investigaciones se conservan bajo el workspace persistente.

El layout lógico se documenta en [`STORAGE.md`](STORAGE.md).

No borres el workspace si necesitas preservar trazabilidad o resultados históricos.

Antes de mantenimiento o cambios de versión, detén las investigaciones y el despliegue. Respalda `workspace/` y `compose.env` del host; conserva también `ollama/` si necesitas restaurar sin descargar de nuevo el modelo. Guarda la identidad de release/commit junto a la copia y conserva permisos y propietarios al restaurar.

## 11. GPU

La baseline funcional no depende de GPU.

Ollama puede utilizar aceleración compatible cuando el host y el runtime la proporcionan, pero la GPU no forma parte del contrato mínimo de despliegue.

## 12. Verificación básica

Después de la instalación, comprobar:

```bash
git status --porcelain --untracked-files=all
docker info
docker compose version
```

y ejecutar las comprobaciones/smoke tests proporcionados por el bootstrap.

Para desarrollo:

```bash
python -m pytest
```

## 13. Actualización

Para cambiar de versión:

```bash
git fetch --tags --prune
git checkout --detach <TAG_O_COMMIT>
```

Verifica el árbol limpio y vuelve a ejecutar el procedimiento de inicialización correspondiente a esa versión.

No reutilices identidades o hashes de una versión anterior para declarar válida una versión posterior.

## 14. Documentación relacionada

- [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)
- [`CONFIGURATION.md`](CONFIGURATION.md)
- [`STORAGE.md`](STORAGE.md)
- [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)
