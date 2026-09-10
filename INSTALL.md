# Instalación y despliegue

[Inicio](README.md) · [Proyecto](PROJECT.md) · [Arquitectura](ARCHITECTURE.md)

Este documento describe la modalidad **Git + Docker sobre Linux**.

Para una instalación reproducible se recomienda utilizar una release/tag concreta en lugar de una rama mutable.

Release pública actual:

**[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**

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

## 9. Arranque y uso

Tras completar el bootstrap, sigue las instrucciones que emita el propio script.

La ejecución del Core en Docker se realiza bajo demanda mediante Docker Compose.

Para conocer las capacidades disponibles desde CENTAURUS:

```bash
centaurus capabilities
```

o desde el contexto de ejecución definido por la instalación.

Consulta la ayuda:

```bash
centaurus --help
```

## 10. Workspace

Las investigaciones se conservan bajo el workspace persistente.

El layout lógico se documenta en [`STORAGE.md`](STORAGE.md).

No borres el workspace si necesitas preservar trazabilidad o resultados históricos.

## 11. Credenciales de la appliance

Estas credenciales corresponden a las modalidades OVA/USB, no al repositorio Git.

### Usuario estándar

```text
Usuario: centaurus
Contraseña: centaurus
```

### Root

```text
Usuario: root
Contraseña: root
```

Cambia las credenciales por defecto después del primer uso cuando la appliance vaya a permanecer desplegada.

## 12. OVA y USB

La OVA y la imagen USB son artefactos externos a Git. El repositorio no contiene estos binarios de gran tamaño.

### OVA VMware

La OVA pública está disponible en:

**[CENTAURUS-C4-FINAL.ova — Google Drive](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)**

Antes de importarla, verifica su identidad:

```text
Fichero=CENTAURUS-C4-FINAL.ova
SIZE_BYTES=11828618752
SHA256=d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868
```

En Linux:

```bash
sha256sum CENTAURUS-C4-FINAL.ova
```

En PowerShell:

```powershell
Get-FileHash .\CENTAURUS-C4-FINAL.ova -Algorithm SHA256
```

El hash calculado debe coincidir exactamente con el valor publicado.

### Imagen USB

La imagen USB validada es:

```text
Fichero=CENTAURUS-USB.img
SIZE_BYTES=31457280000
SHA256=7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165
PUBLICATION_STATUS=PENDING
```

Su enlace público se incorporará cuando finalice la publicación externa.

La documentación de Git + Docker no debe interpretarse como procedimiento de materialización directa de la imagen USB ni como procedimiento de resellado de una OVA.

## 13. Windows

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

## 14. GPU

La baseline funcional no depende de GPU.

Ollama puede utilizar aceleración compatible cuando el host y el runtime la proporcionan, pero la GPU no forma parte del contrato mínimo de despliegue.

## 15. Verificación básica

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

## 16. Actualización

Para cambiar de versión:

```bash
git fetch --tags --prune
git checkout --detach <TAG_O_COMMIT>
```

Verifica el árbol limpio y vuelve a ejecutar el procedimiento de inicialización correspondiente a esa versión.

No reutilices identidades o hashes de una versión anterior para declarar válida una versión posterior.

## 17. Resolución de problemas

### Docker no accesible

```bash
docker info
```

Debe funcionar para el usuario de despliegue.

### Docker Compose no disponible

```bash
docker compose version
```

### Checkout modificado

```bash
git status --porcelain --untracked-files=all
```

Corrige o preserva tus cambios antes de ejecutar el bootstrap.

### El modelo no está disponible

Revisa el estado de Ollama y el directorio persistente configurado. Utiliza los verificadores/aprovisionadores versionados en `scripts/`.

### Una fuente OSINT falla

Una fuente externa puede fallar temporalmente. CENTAURUS puede conservar una investigación parcial cuando existe conocimiento válido; los fallos se registran como `ExecutionFailure`.

### LLM #2 agota el timeout

El `Report` determinista ya persistido sigue siendo autoritativo. La asistencia LLM #2 es fail-soft.

## 18. Seguridad

- no expongas Ollama innecesariamente al host o a redes externas;
- no montes el socket Docker dentro del Core;
- protege el workspace;
- no almacenes secretos en Git;
- cambia credenciales por defecto de la appliance;
- revisa permisos de `CENTAURUS_DATA_ROOT`;
- utiliza únicamente fuentes y objetivos para los que tengas autorización legal/organizativa.

## 19. Documentación relacionada

- [`README.md`](README.md)
- [`PROJECT.md`](PROJECT.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`STORAGE.md`](STORAGE.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)
