# STANDARDS.md
Este documento tiene carácter normativo. En caso de discrepancia con otros documentos del proyecto, prevalecerá el contenido de STANDARDS.md, salvo que una nueva versión aprobada lo sustituya explícitamente.
# Estándares del Proyecto - CENTAURUS OSINT Framework

> **Estado:** Diseño congelado (MVP v1.0)

---

# Objetivo

Este documento define las convenciones, estándares y normas oficiales del proyecto **CENTAURUS OSINT Framework**.

Su finalidad es garantizar que la arquitectura, el desarrollo y la organización del proyecto permanezcan homogéneos durante todo el ciclo de vida del framework.

---

# Identidad

| Elemento | Valor |
|----------|-------|
| Nombre oficial | CENTAURUS OSINT Framework |
| Repositorio Git | centaurus-osint-framework |
| Hostname | centaurus |

---

# Sistema

| Parámetro | Valor |
|-----------|-------|
| Distribución | Debian GNU/Linux 13 |
| Firmware | UEFI |
| Entorno de desarrollo | VMware |
| Despliegue previsto | OVA y USB |

---

# Almacenamiento

| Punto de montaje | Finalidad |
|------------------|-----------|
| `/` | Sistema operativo |
| `/opt/osint-framework` | Plataforma |
| `/workspace` | Datos persistentes |

---

# Docker

# Contenedores

Todos los servicios desplegados mediante Docker deberán cumplir las siguientes normas:

- utilizar Docker Compose;
- pertenecer al proyecto `centaurus`;
- utilizar la red `centaurus-network`;
- emplear nombres de contenedor explícitos;
- utilizar volúmenes persistentes para los datos.

## Proyecto Compose

```text
centaurus
```

## Contenedores previstos

```text
centaurus-core
centaurus-ollama
```

## Red

```text
centaurus-network
```

---

# Plataforma

```text
/opt/osint-framework/
├── centaurus/
├── runtime/
│   ├── docker/
│   └── containerd/
├── models/
├── cache/
├── plugins/
├── rules/
├── config/
├── scripts/
├── docs/
└── docker-compose.yml
```

---

# Workspace

```text
/workspace/
├── reports/
├── evidence/
├── logs/
├── cache/
└── tmp/
```

---

# Runtime de la plataforma

Todo el estado de ejecución deberá almacenarse fuera del repositorio Git.

El directorio `/opt/osint-framework/runtime` será la ubicación oficial para los componentes de ejecución de la plataforma.

Entre ellos:

- Docker
- containerd
- futuros servicios auxiliares

Los modelos de inteligencia artificial se almacenarán en `/opt/osint-framework/models`.
---

# Infrastructure as Code

La infraestructura de la plataforma forma parte del proyecto y se gestionará mediante archivos versionados.

Queda prohibida cualquier configuración manual que no pueda reproducirse a partir del repositorio.

Toda modificación sobre Docker, Docker Compose o cualquier otro componente de la plataforma deberá reflejarse mediante cambios en los archivos de configuración correspondientes.

Objetivos:

- reproducibilidad;
- trazabilidad;
- automatización;
- facilidad de despliegue.

---

# Inteligencia Artificial

| Elemento | Valor |
|----------|-------|
| Motor | Ollama |
| Modelo inicial | Qwen3:4B Instruct |
| Ejecución | Local |

---

# Git

| Elemento | Valor |
|----------|-------|
| Rama principal | `main` |
| Protocolo | SSH |
| Tipo de clave | ED25519 |

---

# Convenciones de desarrollo

- Python 3.
- Arquitectura basada en plugins.
- Rule Engine determinista.
- Un único LLM para planificación e informes.
- El Core no contendrá lógica específica de herramientas.
- No existirán rutas codificadas dentro del Core.
- Todo componente deberá ser modular y reutilizable.
- Todo desarrollo deberá documentarse.

---

# Informes

Formatos soportados:

- Markdown
- JSON

Formato recomendado para los nombres de fichero:

```text
YYYYMMDD_HHMM_objetivo.md
YYYYMMDD_HHMM_objetivo.json
```

---

# Evidencias

Las evidencias deberán almacenarse en formato JSON normalizado para facilitar su trazabilidad y reutilización.

---

# Configuración

Toda la configuración del framework residirá en:

```text
/opt/osint-framework/config/
```

No existirán rutas absolutas codificadas dentro del Core.

---

# Documentación

La documentación oficial del proyecto estará compuesta por los siguientes documentos:

- README.md
- PROJECT.md
- SPECIFICATION.md
- STANDARDS.md
- ARCHITECTURE.md
- STORAGE.md
- INSTALL.md
- DEVELOPMENT.md
- ROADMAP.md
- CHANGELOG.md

Cada documento tendrá una responsabilidad específica y deberá mantenerse sincronizado con el resto de la documentación del proyecto.

---

# Estabilidad documental

Los documentos principales del proyecto se consideran congelados una vez aprobados.

Las modificaciones deberán limitarse exclusivamente a:

- corrección de errores;
- incorporación de funcionalidades implementadas;
- actualización del estado del proyecto.

No deberán realizarse reestructuraciones completas de documentos ya estabilizados salvo decisión expresa del proyecto.

---

# Versionado

El proyecto sigue el estándar **Semantic Versioning (SemVer)**.

Formato:

```text
MAJOR.MINOR.PATCH
```

Donde:

- **MAJOR**: cambios incompatibles con versiones anteriores o publicación de una nueva versión estable.
- **MINOR**: incorporación de nuevas funcionalidades compatibles.
- **PATCH**: correcciones de errores y mejoras menores sin cambios funcionales.

Durante el desarrollo del MVP se utilizará la siguiente correspondencia entre versiones y fases del proyecto:

| Versión | Hito del proyecto |
|----------|-------------------|
| **0.1.0** | Diseño, infraestructura y preparación del entorno |
| **0.2.0** | Plataforma (Docker Engine, Docker Compose y Ollama) |
| **0.3.0** | Core funcional y estructura inicial del framework |
| **0.4.0** | Implementación de las herramientas OSINT del MVP |
| **0.5.0** | Desarrollo del Rule Engine |
| **0.6.0** | Integración completa del LLM |
| **0.7.0** | Reporting, gestión de evidencias y validación |
| **1.0.0** | Publicación del MVP |

La correspondencia entre versiones y fases podrá evolucionar en futuras versiones del proyecto, manteniendo siempre la compatibilidad con Semantic Versioning.

---

# Design Freeze

El diseño funcional y técnico correspondiente al **MVP v1.0** queda congelado.

Cualquier modificación que afecte a la arquitectura, las especificaciones funcionales o los estándares del proyecto deberá justificarse, documentarse y reflejarse en la documentación correspondiente antes de su implementación.

# Snapshots

Antes de cualquier cambio que afecte a la infraestructura de la plataforma se recomienda generar un snapshot de la máquina virtual.

Especialmente antes de:

- modificaciones de Docker;
- cambios en containerd;
- modificaciones del almacenamiento;
- actualizaciones mayores del sistema.

Los snapshots forman parte del procedimiento habitual de desarrollo y no sustituyen al control de versiones del repositorio.