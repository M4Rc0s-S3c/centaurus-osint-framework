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

A continuación, seguir el procedimiento documentado en [`INSTALL.md`](INSTALL.md).

El bootstrap de release está disponible mediante:

```bash
./scripts/bootstrap_linux_release.sh
```

> Los prerrequisitos exactos, la preparación del entorno y los pasos de validación se definen en `INSTALL.md`. Debe utilizarse ese documento como procedimiento de despliegue, no este README como runbook completo.

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

Puede utilizarse una OVA preconstruida cuando se prefiera una appliance virtual autocontenida.

### Imagen USB arrancable

Puede materializarse una imagen raw arrancable sobre un dispositivo de almacenamiento adecuado para ejecución portable.

> La OVA y la imagen raw USB son artefactos de release y no se almacenan directamente en este repositorio Git.

## Windows

Windows nativo puede utilizarse para desarrollo, ejecución del Core y flujos locales con Ollama.

No se presenta Windows como equivalente a la distribución completa Linux + Docker para todas las herramientas OSINT integradas ni para el runtime endurecido de contenedores. Consulta [`INSTALL.md`](INSTALL.md) y [`PROJECT.md`](PROJECT.md) para conocer el alcance documentado.

## LLM local

CENTAURUS utiliza Ollama para las capacidades locales de lenguaje.

El diseño actual separa dos roles lógicos de LLM:

- **LLM #1 - interpretación:** convierte una petición en lenguaje natural en un Intent validado.
- **LLM #2 - asistencia al analista:** actúa después de que exista el Report determinista y es no autoritativo y fail-soft.

El informe determinista continúa siendo válido aunque la asistencia al analista no esté disponible o agote su timeout.

## Persistencia

Los datos de runtime se mantienen fuera de la imagen de aplicación, en un workspace persistente.

Entre los datos persistidos se incluyen normalmente:

```text
workspace/
├── reports/
├── evidence/
├── logs/
├── cache/
└── tmp/
```

Consulta [`STORAGE.md`](STORAGE.md) para el modelo autoritativo de persistencia.

## Pruebas

El repositorio incluye la suite automatizada bajo:

```text
tests/
```

En un entorno de desarrollo/pruebas preparado:

```bash
python -m pytest
```

Consulta [`DEVELOPMENT.md`](DEVELOPMENT.md) para las pautas de desarrollo y validación.

## Documentación

Orden de lectura recomendado:

1. [`PROJECT.md`](PROJECT.md) - identidad del proyecto, alcance y modalidades de distribución.
2. [`INSTALL.md`](INSTALL.md) - despliegue e instalación.
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) - arquitectura del framework.
4. [`SPECIFICATION.md`](SPECIFICATION.md) - especificación funcional y no funcional.
5. [`STORAGE.md`](STORAGE.md) - persistencia y trazabilidad.
6. [`STANDARDS.md`](STANDARDS.md) - convenciones y estándares del proyecto.
7. [`DEVELOPMENT.md`](DEVELOPMENT.md) - flujo de desarrollo.

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
