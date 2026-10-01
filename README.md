# CENTAURUS OSINT Framework

[Español](README.md) | [English](README.en.md)

CENTAURUS es un framework OSINT modular y orientado a ejecución local, diseñado para equipos Blue Team, análisis de seguridad y entornos IT.

Proporciona un flujo reproducible para recopilar información pública, normalizar evidencias, aplicar reglas de análisis deterministas y generar informes de investigación trazables, manteniendo las decisiones operativas fuera del modelo de lenguaje.

## Características principales

- Arquitectura modular basada en plugins.
- Recopilación OSINT pasiva.
- Flujo determinista `Evidence -> Findings -> Report`.
- Integración con LLM local mediante Ollama.
- Separación entre el informe autoritativo determinista y la asistencia no autoritativa del LLM.
- Workspace persistente para investigaciones, evidencias, hallazgos, informes y logs.
- Despliegue Git + Docker sobre Linux.
- Distribución como appliance VMware.
- Distribución mediante imagen USB arrancable.
- Modelo de ejecución local-first.
- Licencia Apache 2.0.

## Capacidades OSINT incluidas

La versión actual integra seis herramientas/capacidades OSINT:

- WHOIS lookup
- RDAP lookup
- DNSRecon
- Sublist3r
- TheHarvester
- crt.sh lookup

La arquitectura permite incorporar nuevas herramientas mediante el modelo de plugins sin rediseñar el Core.

## Arquitectura resumida

```text
Analista
   |
   v
CLI / petición en lenguaje natural
   |
   v
LLM #1 - Interpretación del Intent
   |
   v
TargetFactory
   |
   v
Planner
   |
   v
Ejecución del Core
   |
   +--> Plugins / fuentes OSINT
   |        |
   |        v
   |   Observaciones raw
   |        |
   |        v
   |   Normalización
   |        |
   v        v
EvidenceManager
   |
   v
Evidence
   |
   v
RuleEngine
   |
   v
Findings
   |
   v
Report determinista
   |
   +--> report.json   (autoritativo)
   +--> report.md     (proyección determinista)
   |
   v
LLM #2 - Asistencia al analista
          grounded, efímera,
          no autoritativa, fail-soft
```

El modelo de lenguaje no ejecuta herramientas OSINT de forma autónoma ni genera hallazgos autoritativos. La ejecución operativa y las conclusiones técnicas permanecen trazables mediante componentes deterministas.

## Inicio rápido - Git + Docker

### Requisitos

Host Linux con:

- Git
- Python 3
- Docker Engine
- Docker Compose
- acceso a Docker para el usuario de despliegue

Clonar el repositorio:

```bash
git clone https://github.com/M4Rc0s-S3c/centaurus-osint-framework.git
cd centaurus-osint-framework
```

Para utilizar la release pública actual:

```bash
git checkout v1.0.0
```

A continuación, seguir el procedimiento documentado en [`INSTALL.md`](docs/INSTALL.md).

El bootstrap de release está disponible mediante:

```bash
./scripts/bootstrap_linux_release.sh
```

> Los prerrequisitos exactos, la preparación del entorno y los pasos de validación se definen en `docs/INSTALL.md`. Debe utilizarse ese documento como procedimiento de despliegue, no este README como runbook completo.

## Credenciales de la appliance

La appliance distribuida en OVA/USB utiliza por defecto:

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

Se recomienda cambiar las credenciales por defecto después del primer uso cuando el entorno vaya a permanecer desplegado.

## Modalidades de distribución

CENTAURUS contempla varias modalidades de distribución.

### Git + Docker

Recomendada cuando el framework se despliega desde código fuente sobre un host Linux compatible.

El repositorio incluye el Core, las definiciones Docker/Compose, locks de dependencias, scripts de inicialización y documentación de despliegue.

### Appliance VMware

La appliance VMware preconstruida está disponible mediante almacenamiento externo:

**[Acceder a la descarga de CENTAURUS-C4-FINAL.ova (Google Drive)](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)**

Identidad del artefacto publicado:

```text
Fichero: CENTAURUS-C4-FINAL.ova
SIZE_BYTES: 11828618752
SHA256: d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868
```

Se recomienda verificar siempre el SHA-256 después de la descarga.

### Imagen USB arrancable

La imagen raw USB está disponible mediante almacenamiento externo:

**[Acceder a la descarga de CENTAURUS-USB.img](https://tinyurl.com/42wumj8b)**

Identidad del artefacto publicado:

```text
Fichero: CENTAURUS-USB.img
SIZE_BYTES: 31457280000
SHA256: 7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165
```

Se recomienda verificar siempre el SHA-256 después de la descarga.

> Los binarios OVA/USB son artefactos externos y no se almacenan directamente en este repositorio Git.

## Windows

Windows nativo puede utilizarse para desarrollo, ejecución del Core y flujos locales con Ollama.

No se presenta Windows como equivalente a la distribución completa Linux + Docker para todas las herramientas OSINT integradas ni para el runtime endurecido de contenedores. Consulta [`INSTALL.md`](docs/INSTALL.md) y [`PROJECT.md`](docs/PROJECT.md) para conocer el alcance documentado.

## LLM local

CENTAURUS utiliza Ollama para las capacidades locales de lenguaje.

El diseño actual separa dos roles lógicos de LLM:

- **LLM #1 - interpretación:** convierte una petición en lenguaje natural en un Intent validado.
- **LLM #2 - asistencia al analista:** actúa después de que exista el Report determinista y es no autoritativo y fail-soft.

El informe determinista continúa siendo válido aunque la asistencia al analista no esté disponible o agote su timeout.

## Persistencia

Los datos de runtime se mantienen fuera de la imagen de aplicación, en un workspace persistente.

Los artefactos de cada investigación se conservan en el workspace persistente, organizados por su identificador:

```text
workspace/
└── investigations/
    └── <investigation-id>/
        ├── evidences/
        │   ├── raw/
        │   └── normalized/
        ├── findings/
        ├── reports/
        │   ├── report.json
        │   └── report.md
        └── execution/
            └── failures/
```

Consulta [`STORAGE.md`](docs/STORAGE.md) para el modelo autoritativo de persistencia.

## Pruebas

El repositorio incluye la suite automatizada bajo:

```text
tests/
```

En un entorno de desarrollo/pruebas preparado:

```bash
python -m pytest
```

Consulta [`DEVELOPMENT.md`](docs/DEVELOPMENT.md) para las pautas de desarrollo y validación.

## Documentación

Orden de lectura recomendado:

1. [`PROJECT.md`](docs/PROJECT.md) · [English](docs/PROJECT.en.md) - identidad del proyecto, alcance y modalidades de distribución.
2. [`INSTALL.md`](docs/INSTALL.md) · [English](docs/INSTALL.en.md) - despliegue e instalación.
3. [`USER_GUIDE.md`](docs/USER_GUIDE.md) · [English](docs/USER_GUIDE.en.md) - primera sesión, interpretación de resultados y resolución de incidencias.
4. [`ARCHITECTURE.md`](docs/ARCHITECTURE.md) · [English](docs/ARCHITECTURE.en.md) - arquitectura del framework.
5. [`SPECIFICATION.md`](docs/SPECIFICATION.md) · [English](docs/SPECIFICATION.en.md) - especificación funcional y no funcional.
6. [`STORAGE.md`](docs/STORAGE.md) · [English](docs/STORAGE.en.md) - persistencia y trazabilidad.
7. [`STANDARDS.md`](docs/STANDARDS.md) · [English](docs/STANDARDS.en.md) - convenciones y estándares del proyecto.
8. [`DEVELOPMENT.md`](docs/DEVELOPMENT.md) · [English](docs/DEVELOPMENT.en.md) - flujo de desarrollo.

## Release

Release pública actual:

**[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**

La entrega académica del TFM quedó congelada de forma independiente y continúa siendo reproducible desde el commit de entrega documentado en los materiales presentados. Los cambios posteriores del repositorio limitados a documentación pública y licencia no alteran esa fotografía académica congelada.

## Uso responsable

CENTAURUS está orientado a OSINT legítimo, Blue Team, seguridad defensiva, investigación y evaluaciones autorizadas.

El usuario es responsable de garantizar que el uso de fuentes públicas, herramientas de terceros e información recopilada cumple la legislación aplicable, los términos de las fuentes y las políticas de su organización.

## Licencia

CENTAURUS se distribuye bajo la **Apache License, Version 2.0**.

Consulta [`LICENSE`](LICENSE) para el texto completo de la licencia y [`NOTICE.md`](NOTICE.md) para la información de atribución.
