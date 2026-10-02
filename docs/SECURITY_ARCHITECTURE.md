# Arquitectura de seguridad y tratamiento de fallos

[Español](SECURITY_ARCHITECTURE.md) | [English](SECURITY_ARCHITECTURE.en.md)

[Inicio](../README.md) · [ARCHITECTURE.md](ARCHITECTURE.md) · [CONFIGURATION.md](CONFIGURATION.md)

## 1. Alcance y límites de confianza

CENTAURUS separa la entrada del analista, las respuestas de fuentes externas, la inferencia local, la ejecución del Core y la persistencia. Los controles buscan mantener trazabilidad y limitar la autoridad de cada componente.

El host, sus administradores, las imágenes desplegadas y los plugins instalados forman parte de la base de confianza. La separación de entornos de dependencias no convierte cada plugin en un sandbox para código hostil. Los controles de contenedor tampoco sustituyen la seguridad del host ni protegen frente a un administrador comprometido.

## 2. Autoridad del Core y de los LLM

El Core controla el ciclo de vida de la investigación. La validación del Intent, la construcción del Target, el Planner y las reglas determinan el flujo operativo y sus resultados persistentes.

LLM #1 interpreta una petición como un Intent sujeto a esquema y valores admitidos. No recibe autoridad para ejecutar herramientas arbitrarias, cambiar el catálogo o escribir hallazgos. Una interpretación inválida debe detener ese flujo antes de la investigación.

LLM #2 actúa después de persistir el informe determinista. Recibe una proyección controlada que excluye `Evidence.data`, conserva referencias y metadatos pertinentes y limita la información suministrada. Su salida pasa validaciones estructurales y comprobaciones factuales contra el contexto permitido; los elementos que no superan esas comprobaciones se descartan.

La validación de JSON no demuestra veracidad. Estos controles reducen la superficie de entrada y restringen el uso de la respuesta, sin declarar inmunidad universal frente a prompt injection o errores del modelo. La asistencia es efímera, no autoritativa y no modifica `report.json`.

## 3. Contenedores y red

El despliegue de referencia aplica:

| Componente | Controles |
| --- | --- |
| Core | Usuario `1000:1000`, raíz de solo lectura, workspace persistente y `/tmp` temporal limitado a 256 MiB con `nosuid,nodev,noexec`. |
| Core | Eliminación de todas las capabilities Linux, `no-new-privileges`, límite de 256 procesos e `init` para recoger procesos hijos. |
| Ollama | Eliminación de capabilities, `no-new-privileges`, límite de 512 procesos y almacén de modelos montado en solo lectura. |
| Red LLM | Red interna sin puerto Ollama publicado en el host; Ollama sin ruta de salida a redes externas. |
| Red Core | Acceso a Ollama por la red interna y salida a fuentes OSINT por una red separada. |

La imagen Ollama de referencia utiliza identidad root dentro del contenedor; no se presenta como un servicio rootless. Su aislamiento depende de los controles concretos anteriores. El Core no monta el socket Docker.

La ausencia de publicación de puertos se refiere al Compose suministrado. Los cambios del administrador en redes, montajes o privilegios alteran esa postura de seguridad.

## 4. Acceso a la appliance

En OVA/USB, el usuario analista no pertenece a los grupos `sudo` ni `docker`. Los comandos autorizados se exponen mediante wrappers restringidos, con cero argumentos, TTY obligatoria y autenticación nueva mediante `sudo -k`; no utilizan acceso `NOPASSWD`.

El broker verifica identidad del usuario, permisos y propiedad de rutas críticas, configuración Compose, fichero de entorno e imagen Core. Limpia el entorno heredado, utiliza una conexión Docker local fija y evita sesiones concurrentes mediante bloqueo. Si Docker no está disponible, falla en lugar de iniciar automáticamente el daemon.

`centaurus-poweroff` proporciona un apagado acotado con autenticación. Estos controles son propios de la appliance. El usuario que administra una instalación Git + Docker mantiene los privilegios Docker necesarios para ese despliegue.

## 5. Cadena de suministro

La construcción utiliza dependencias bloqueadas, referencias de suministro versionadas e imágenes fijadas por digest cuando así se define en el repositorio. Las herramientas con dependencias incompatibles disponen de entornos separados y el bootstrap ejecuta comprobaciones de consistencia con `pip check`.

La identidad del modelo se verifica durante el aprovisionamiento; el uso normal no requiere descargar modelos desde Ollama. Cambiar imágenes, modelo o locks exige volver a comprobar su coherencia.

Estos mecanismos no equivalen por sí solos a una SBOM firmada completa, a hashes de todos los artefactos de dependencia ni a reproducibilidad binaria universal. Los hashes publicados de OVA/USB permiten comprobar identidad respecto del valor distribuido; no sustituyen una firma independiente del editor.

## 6. Fallos y conservación de resultados

| Situación | Comportamiento |
| --- | --- |
| Error estructural o de contrato del Core | Interrupción del flujo; la investigación iniciada se marca como fallida cuando corresponde. |
| Fallo de una tarea o fuente | Registro de `ExecutionFailure`; puede continuar una investigación parcial si queda conocimiento válido. |
| Todas las tareas fallan sin conocimiento válido | Investigación fallida, sin informe de resultados válido. |
| Asistencia LLM #2 no disponible, inválida o fuera de tiempo | Se conserva el informe determinista ya persistido. |
| Fallo de notificación de progreso | No debe invalidar el conocimiento producido por el flujo principal. |

`COMPLETED` expresa la finalización del ciclo de dominio; no garantiza que todas las fuentes hayan respondido. Revisa siempre los fallos de ejecución y la cobertura del informe.

No existe rollback transaccional global de todos los ficheros. Un fallo posterior puede dejar artefactos anteriores útiles para diagnóstico; su presencia aislada no demuestra que la investigación haya terminado correctamente. [`STORAGE.md`](STORAGE.md) define la persistencia autoritativa.

## 7. Recursos de inferencia

La asistencia LLM #2 usa por defecto timeout de 300 segundos y contexto de 8192, con límite de generación opcional. Su petición desactiva el razonamiento extendido mediante `think=false` y solicita `keep_alive=0`. Estas opciones pertenecen a ese flujo, no a una garantía global para cualquier cliente Ollama.

No se promete recuperación universal ante falta de memoria, reintento automático ni paralelismo implícito. Un timeout limita la espera del cliente; el operador debe revisar el estado del servicio si persiste un problema de recursos. Los parámetros admitidos están en [`CONFIGURATION.md`](CONFIGURATION.md).

## 8. Protección de datos y operación

Protege el workspace y sus copias: pueden incluir información pública recopilada, datos personales, objetivos y contexto operativo. Aplica permisos y retención adecuados al despliegue y revisa los artefactos antes de compartirlos.

La telemetría de asistencia no está concebida para volcar prompts o informes completos. Esto no significa que todos los logs carezcan de información sensible; mensajes de error y contexto de ejecución requieren revisión.

Cambia las credenciales iniciales de la appliance en despliegues persistentes, conserva los secretos fuera de Git y mantén respaldos consistentes antes de modificar el runtime. Los procedimientos específicos están en [`DEPLOYMENT_GIT_DOCKER.md`](DEPLOYMENT_GIT_DOCKER.md), [`DEPLOYMENT_OVA.md`](DEPLOYMENT_OVA.md) y [`DEPLOYMENT_USB.md`](DEPLOYMENT_USB.md).
