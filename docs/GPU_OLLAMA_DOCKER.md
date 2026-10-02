# GPU en Ollama con Docker — experimental

[Español](GPU_OLLAMA_DOCKER.md) | [English](GPU_OLLAMA_DOCKER.en.md)

[Inicio](../README.md) · [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md) · [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md)

## 1. Estado y alcance

**Guía experimental, sin certificación de hardware GPU por CENTAURUS.** La baseline distribuida sigue siendo CPU. El repositorio no incluye overlays GPU: los ejemplos siguientes son propuestas de configuración local que requieren preparación y validación en el host real. Publicar esta guía no implica que se hayan ejecutado esas pruebas.

| Variante | Estado en CENTAURUS |
| --- | --- |
| Linux + Docker CPU | Baseline de la distribución. |
| NVIDIA + Docker | Propuesta experimental, pendiente de validación del host. |
| AMD ROCm + Docker | Propuesta experimental; requiere además imagen y cadena de suministro propias. |
| Vulkan | Evaluación experimental separada; sin perfil distribuido. |
| GPU en OVA/VMware o USB | Fuera del alcance; no se infiere soporte ni passthrough. |

Windows nativo se documenta en [`DEPLOYMENT_WINDOWS.md`](DEPLOYMENT_WINDOWS.md).

## 2. Contrato que debe preservarse

Solo `centaurus-ollama` recibe acceso a la GPU. El Core conserva código, usuario, redes, workspace y contratos `Evidence -> Finding -> Report`. Se mantienen `OLLAMA_BASE_URL=http://centaurus-ollama:11434`, `OLLAMA_NO_CLOUD=1`, modelo montado en solo lectura, red `centaurus-llm-network` interna y ausencia de puertos publicados. El Core sigue siendo el único servicio con red de salida.

Conserva `cap_drop: ALL`, `no-new-privileges` y los límites de procesos. No uses `privileged` ni publiques `11434` para resolver problemas de GPU. Si una combinación no funciona con los controles actuales, deja esa variante sin validar y revisa la incompatibilidad; no relajes silenciosamente el Compose base.

## 3. Preparación del host

Completa primero la instalación CPU de [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md). Conserva el workspace, la identidad de imagen/modelo y los resultados de referencia. La preparación de drivers y runtime GPU es una tarea administrativa del host.

Para NVIDIA, comprueba la GPU y el driver con `nvidia-smi`. Instala y configura NVIDIA Container Toolkit siguiendo su documentación oficial y valida el acceso desde un contenedor de prueba antes de aplicar el overlay. Configurar el runtime o reiniciar Docker puede afectar a otros servicios del host; planifica esa intervención.

Para AMD, contrasta GPU y driver con la matriz de Ollama/ROCm y comprueba `/dev/kfd` y `/dev/dri`. Los permisos de dispositivos deben resolverse explícitamente. La compatibilidad debe corresponder a la versión de imagen elegida, no solo a la documentación de la versión más reciente.

## 4. Ejemplo NVIDIA y uso de Compose

Crea el overlay local fuera del checkout, por ejemplo en el directorio de datos dedicado. Así no introduces un fichero sin seguimiento que bloquee el bootstrap. El siguiente YAML añade una reserva GPU únicamente a Ollama:

```yaml
services:
  centaurus-ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

Para seleccionar una GPU, sustituye `count` por `device_ids` con los identificadores comprobados en ese host; no combines ambos campos. El ejemplo no cambia el digest Ollama del Compose base: que Docker acepte la reserva no demuestra que esa imagen pueda utilizar tu GPU.

Desde el checkout y con `CENTAURUS_DATA_ROOT` definido con la ruta de la instalación CPU, después de guardar el YAML como `compose.gpu-nvidia.yml` en ese directorio:

```bash
CENTAURUS_ENV_FILE="$CENTAURUS_DATA_ROOT/compose.env"
CENTAURUS_GPU_OVERLAY="$CENTAURUS_DATA_ROOT/compose.gpu-nvidia.yml"
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml -f "$CENTAURUS_GPU_OVERLAY" --profile framework config
```

Revisa el resultado renderizado y los controles del apartado 2. Con las sesiones del Core cerradas y el host preparado, la aplicación local de la variante sería:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml -f "$CENTAURUS_GPU_OVERLAY" up -d --force-recreate centaurus-ollama
```

Mientras evalúas GPU, utiliza los dos ficheros y el mismo `--env-file` en las operaciones Compose, incluidas las sesiones del Core. El bootstrap actual solo utiliza `docker/compose.yml`: no activa ni certifica el overlay y puede recrear Ollama con la baseline CPU al repetirse.

## 5. AMD ROCm y Vulkan

La vía ROCm requiere una imagen Ollama apropiada y acceso a los dispositivos. El ejemplo conceptual exige definir `CENTAURUS_ROCM_IMAGE` con una identidad revisada y fijada por digest; no hay un digest ROCm certificado en el lock actual:

```yaml
services:
  centaurus-ollama:
    image: "${CENTAURUS_ROCM_IMAGE:?Set a reviewed digest-pinned ROCm image}"
    devices:
      - /dev/kfd:/dev/kfd
      - /dev/dri:/dev/dri
```

El requisito de la variable impide omitirla, pero no valida por sí mismo su digest. No uses una etiqueta mutable como identidad final ni declares que esta variante pasa las comprobaciones de imagen del bootstrap CPU. Deben registrarse y comprobarse su imagen, versión, hardware, modelo y compatibilidad con el endurecimiento antes de utilizarla como despliegue validado.

Vulkan queda fuera de estos ejemplos. La documentación actual de Ollama describe su disponibilidad en imágenes actuales, pero eso no certifica su comportamiento en el digest fijado por CENTAURUS. Su estado experimental aquí corresponde a la integración del proyecto, independientemente del estado que anuncie el proveedor.

## 6. Validación y recursos

Registra GPU, driver, toolkit/runtime, versión Docker/Compose, digest de imagen, identidad del modelo y configuración LLM. La aceptación local debe cubrir:

1. GPU operativa en host y en un contenedor independiente.
2. Compose renderizado conserva redes, permisos, montajes y ausencia de puertos; el Core no recibe GPU.
3. Ollama utiliza realmente el acelerador durante inferencia; no basta con observar una reserva de dispositivo.
4. Casos pequeños y de muchos hallazgos mantienen los contratos del informe y de la asistencia, con cobertura conocida.
5. Medición de latencia, RAM y VRAM, sin falta de memoria ni cambio inesperado a CPU; nueva comprobación tras reiniciar.
6. Vuelta a CPU comprobada con los datos persistentes conservados.


```bash
docker inspect centaurus-ollama --format 'DeviceRequests={{json .HostConfig.DeviceRequests}}'
docker logs --tail 100 centaurus-ollama
docker port centaurus-ollama
```

El último comando debe quedar sin salida. En NVIDIA, observa también `nvidia-smi` durante la inferencia; revisa métricas del backend correspondiente para AMD. Una prueba local satisfactoria documenta ese host, no todas las GPU.

La VRAM depende del modelo, contexto, caché y concurrencia. La GPU no corrige truncamiento, grounding ni validación de salida. Mantén inicialmente el perfil actual de LLM #2: timeout 300 s, `num_ctx=8192`, `num_predict` opcional, `think=false` y `keep_alive=0`. Cualquier ajuste necesita medición y validación propias; consulta [`CONFIGURATION.md`](CONFIGURATION.md).

## 7. Reversión a CPU

Termina las sesiones del Core. Con las mismas rutas de entorno, recrea Ollama utilizando solo el Compose base:

```bash
docker compose --env-file "$CENTAURUS_ENV_FILE" -f docker/compose.yml up -d --force-recreate centaurus-ollama
```

Comprueba imagen, ausencia de peticiones/dispositivos GPU, servicio y funcionamiento CPU. Conserva el modelo y el workspace; no los borres para revertir. La retirada de drivers o toolkit es mantenimiento independiente del host.

## 8. Resolución de problemas y referencias

Consulta [`TROUBLESHOOTING.md`](TROUBLESHOOTING.md) para el diagnóstico GPU y [`SECURITY_ARCHITECTURE.md`](SECURITY_ARCHITECTURE.md) para los controles del despliegue.

- [Ollama — Docker](https://docs.ollama.com/docker)
- [Ollama — Hardware support](https://docs.ollama.com/gpu)
- [Docker Compose — GPU access](https://docs.docker.com/compose/how-tos/gpu-support/)
- [NVIDIA Container Toolkit — Install Guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)
