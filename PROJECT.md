# Visión general del proyecto

[Español](PROJECT.md) | [English](PROJECT.en.md)
[Inicio](README.md) · [Arquitectura](ARCHITECTURE.md) · [Instalación](INSTALL.md) · [Especificación](SPECIFICATION.md)

## 1. Identidad

**CENTAURUS OSINT Framework** es un framework OSINT modular y orientado a ejecución local para equipos Blue Team, análisis de seguridad y departamentos IT.

Su objetivo es proporcionar una plataforma reproducible para realizar evaluaciones pasivas de exposición pública, preservando la trazabilidad entre fuentes, evidencias, hallazgos e informes.

La release pública actual es **[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**.

## 2. Objetivo

CENTAURUS permite:

- interpretar una petición de investigación expresada en lenguaje natural;
- construir una `Investigation` estructurada;
- seleccionar de forma determinista las capacidades que deben ejecutarse;
- ejecutar herramientas OSINT mediante plugins;
- preservar observaciones originales y evidencias normalizadas;
- producir `Findings` mediante `Rules` deterministas;
- consolidar el conocimiento en un `Report` persistente;
- presentar el resultado mediante CLI y asistencia LLM local acotada.

## 3. Usuarios objetivo

El proyecto está orientado principalmente a:

- equipos Blue Team;
- departamentos IT de PYMEs;
- analistas de seguridad;
- investigación y evaluación defensiva autorizada de exposición pública.

CENTAURUS no sustituye a un SIEM, una plataforma de pentesting o un escáner activo.

## 4. Cobertura funcional

### DOMAIN

Cobertura principal mediante:

- WHOIS;
- RDAP;
- DNSRecon;
- Sublist3r;
- TheHarvester;
- crt.sh.

### IP

Cobertura limitada mediante RDAP.

### EMAIL y CERTIFICATE

Se mantienen como conceptos de evolución. No forman parte de la cobertura operacional completa actual como `Target` de investigación directa.

## 5. Arquitectura

CENTAURUS separa explícitamente:

- interfaz e interpretación de entrada;
- orquestación del Core;
- planificación;
- ejecución;
- plugins/herramientas;
- normalización;
- persistencia;
- `RuleEngine`;
- reporting;
- asistencia LLM;
- infraestructura Docker/Ollama.

El **Core** es el custodio del ciclo de vida de `Investigation`.

`Planner` determina las capacidades a ejecutar a partir del `Target` y del `Intent`. El modelo de lenguaje no selecciona herramientas ni genera `Findings`.

Consulta [`ARCHITECTURE.md`](ARCHITECTURE.md) para el detalle.

## 6. Inteligencia artificial: dos roles lógicos

CENTAURUS utiliza un servicio LLM local a través de Ollama con dos responsabilidades distintas.

### LLM #1 — interpretación

- participa en `RequestInterpreter`;
- clasifica un `Intent` permitido;
- no detecta ni normaliza el `Target`;
- no selecciona herramientas;
- no ejecuta acciones.

La construcción del `Target` es determinista.

### LLM #2 — asistencia al analista

- actúa únicamente después de que exista un `Report` determinista;
- trabaja con una proyección controlada del informe;
- genera una ayuda de síntesis/explicación;
- es efímero;
- no es autoritativo;
- funciona en modo fail-soft.

Un fallo de LLM #2 no invalida `Evidence`, `Findings` ni `Report`.

## 7. Tecnologías principales

| Área | Tecnología |
|---|---|
| Sistema objetivo | Debian GNU/Linux 13 |
| Framework | Python 3.12 |
| Contenedorización | Docker + Docker Compose |
| CLI | Typer + Rich + Prompt Toolkit |
| HTTP | httpx |
| LLM local | Ollama |
| Modelo | `qwen3:4b` |
| Persistencia | Filesystem + JSON |
| Logging | `logging` stdlib + `RotatingFileHandler` |
| Testing | pytest |

Perfil operacional de LLM #2:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

## 8. Modalidades de distribución

CENTAURUS puede utilizarse mediante tres modalidades.

### Git + Docker

Despliegue reproducible desde el repositorio público sobre un host Linux compatible.

Consulta [`INSTALL.md`](INSTALL.md).

### Appliance VMware

La OVA preconstruida se distribuye mediante almacenamiento externo:

**[CENTAURUS-C4-FINAL.ova — Google Drive](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)**

```text
SIZE_BYTES=11828618752
SHA256=d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868
```

### Imagen USB arrancable

La imagen raw USB está validada y pendiente de publicación externa:

```text
Fichero=CENTAURUS-USB.img
SIZE_BYTES=31457280000
SHA256=7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165
PUBLICATION_STATUS=PENDING
```

Los binarios OVA/USB no se almacenan directamente en este repositorio Git. La integridad de cada artefacto debe verificarse mediante su SHA-256.

## 9. Credenciales de la appliance

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

Se recomienda cambiar las credenciales por defecto después del primer acceso cuando el entorno vaya a permanecer desplegado.

## 10. Operación de la appliance

El usuario estándar inicia CENTAURUS mediante:

```bash
centaurus
```

El apagado controlado se realiza fuera del shell mediante:

```bash
centaurus-poweroff
```

La arquitectura evita conceder administración Docker genérica al usuario operativo.

## 11. Uso responsable

CENTAURUS está destinado a OSINT legítimo, seguridad defensiva, investigación y evaluaciones autorizadas.

El usuario es responsable de cumplir la legislación aplicable, los términos de las fuentes consultadas y las políticas de su organización.

## 12. Documentación relacionada

- [`README.md`](README.md)
- [`INSTALL.md`](INSTALL.md)
- [`ARCHITECTURE.md`](ARCHITECTURE.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`STORAGE.md`](STORAGE.md)
- [`STANDARDS.md`](STANDARDS.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)

## 13. Licencia

CENTAURUS se distribuye bajo **Apache License 2.0**.

Consulta [`LICENSE`](LICENSE) y [`NOTICE.md`](NOTICE.md).
