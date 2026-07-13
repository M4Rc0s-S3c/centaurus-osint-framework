# PROJECT.md

# CENTAURUS OSINT Framework

> Framework modular de inteligencia de fuentes abiertas (OSINT) orientado a equipos Blue Team y departamentos de TI de pequeñas y medianas organizaciones.

---

# Información general

| Campo | Valor |
|--------|-------|
| Nombre del proyecto | CENTAURUS OSINT Framework |
| Estado | Plataforma base operativa (v0.2.0) |
| Tipo | Framework OSINT modular |
| Plataforma objetivo | Debian GNU/Linux 13 |
| Arquitectura | Modular basada en plugins |
| Licencia | Pendiente de definir |
| Repositorio | GitHub (privado) |

---

# Objetivo

CENTAURUS OSINT Framework proporciona una plataforma autocontenida para la recopilación, correlación y análisis de información pública sobre activos corporativos mediante técnicas OSINT pasivas.

El framework está diseñado para evolucionar mediante una arquitectura modular basada en **plugins** y un **Rule Engine** determinista, permitiendo incorporar nuevas capacidades sin modificar el núcleo del sistema.

---

# Principios de diseño

El proyecto se basa en los siguientes principios:

- Arquitectura modular.
- Separación entre sistema operativo, plataforma y datos.
- Infrastructure as Code (IaC).
- Funcionamiento offline siempre que sea posible.
- Uso de inteligencia artificial local.
- Portabilidad.
- Escalabilidad.
- Mantenibilidad.
- Extensibilidad mediante plugins.
- Rule Engine desacoplado del Core.
- Persistencia independiente del código fuente.

---

# Tecnologías seleccionadas

| Componente | Tecnología |
|------------|------------|
| Sistema operativo | Debian 13 |
| Contenedores | Docker |
| Orquestación | Docker Compose |
| LLM local | Ollama |
| Modelo inicial | Qwen3:4B Instruct |
| Control de versiones | Git |
| Repositorio remoto | GitHub |
| Autenticación Git | SSH (ED25519) |
| Lenguaje principal | Python *(previsto)* |

---

# Arquitectura de almacenamiento

| Partición | Punto de montaje | Propósito |
|------------|------------------|-----------|
| SYSTEM | `/` | Sistema operativo |
| PLATFORM | `/opt/osint-framework` | Plataforma CENTAURUS |
| WORKSPACE | `/workspace` | Evidencias, informes y datos persistentes |

---

# Hardware de referencia

| Recurso | Valor |
|----------|-------|
| CPU | 8 vCPU |
| Memoria RAM | 8 GB |
| Almacenamiento | 30 GB |

Distribución recomendada:

| Disco | Tamaño | Uso |
|--------|---------|----------------------|
| Disco 1 | 5 GB | Sistema Operativo |
| Disco 2 | 15 GB | Plataforma |
| Disco 3 | 10 GB | Workspace |

---

# Convenciones del proyecto

## Hostname

```text
centaurus
```

## Repositorio remoto

```text
git@github.com:M4Rc0s-S3c/centaurus-osint-framework.git
```

## Repositorio local

```text
/opt/osint-framework/centaurus
```

## Rama principal

```text
main
```

## Método de autenticación

```text
SSH (ED25519)
```

## Proyecto Docker Compose

```text
centaurus
```

## Red Docker

```text
centaurus-network
```

---

# Organización general

```text
/opt/osint-framework
│
├── centaurus/          ← Repositorio Git
├── runtime/            ← Docker, containerd y Ollama
├── models/             ← Modelos LLM
├── cache/              ← Caché persistente
└── lost+found/
```

El código fuente, la documentación, los archivos de configuración y la definición de la infraestructura (Docker Compose) residen exclusivamente dentro del repositorio Git (centaurus).

Los componentes de ejecución (Docker, containerd y Ollama), los modelos de inteligencia artificial y la información temporal permanecen fuera del repositorio para mantener una separación clara entre código y estado de ejecución.
---

# Componentes principales

La arquitectura funcional del framework estará formada por los siguientes componentes:

- CLI
- Planner
- Core
- Plugin Manager
- Executor
- Evidence Manager
- Rule Engine
- Reporting Engine
- LLM Manager

La descripción detallada de cada componente puede consultarse en **ARCHITECTURE.md**.

---

# Documentación

La documentación del proyecto se organiza en documentos independientes, cada uno con una responsabilidad específica.

El índice completo y el orden de lectura recomendado pueden consultarse en **README.md**.

| Documento | Propósito |
|-----------|-----------|
| `PROJECT.md` | Información general e identidad del proyecto. |
| `SPECIFICATION.md` | Especificación funcional del framework. |
| `STANDARDS.md` | Estándares y convenciones oficiales. |
| `ARCHITECTURE.md` | Arquitectura técnica del sistema. |
| `STORAGE.md` | Arquitectura de almacenamiento. |
| `INSTALL.md` | Instalación y preparación del entorno. |
| `DEVELOPMENT.md` | Guía para el desarrollo. |
| `ROADMAP.md` | Planificación y evolución del proyecto. |
| `CHANGELOG.md` | Historial de cambios del proyecto. |

---

# Estado actual

## Infraestructura

- [x] Instalación de Debian.
- [x] Configuración UEFI.
- [x] Arquitectura de almacenamiento.
- [x] Configuración de puntos de montaje.
- [x] Validación de red.
- [x] OpenSSH Server operativo.
- [x] Snapshot de infraestructura.
- [x] Clon de desarrollo.
- [x] Instalación de Git.
- [x] Configuración de GitHub mediante SSH.
- [x] Clonado del repositorio.
- [x] Documentación base completada.
- [x] Instalación de Docker Engine.
- [x] Instalación de Docker Compose.
- [x] Creación del entorno de contenedores.
- [x] Integración de Ollama.
- [x] Infrastructure as Code.
- [x] Runtime de Docker desacoplado del sistema.
- [x] Runtime de containerd desacoplado del sistema.
- [x] Runtime de Ollama desacoplado del repositorio.
- [x] Contenedor `centaurus-ollama` operativo.
- [x] Red Docker `centaurus-network` operativa.
- [x] Arquitectura de runtime validada.


---

# Próximo hito

# Próximo hito

Inicio del desarrollo del Core Framework:

- Gestor de configuración.
- Sistema de logging.
- Gestión del Workspace.
- Motor de plugins.
- API interna.
- Desarrollo del CLI inicial.
- Descarga del modelo Qwen3:4B Instruct.

---

# Referencias

La información funcional del proyecto se desarrolla en:

- **SPECIFICATION.md**
- **ARCHITECTURE.md**
- **STANDARDS.md**

---

# Historial

| Versión | Fecha | Cambios |
|----------|--------|---------|
| 0.4 | Julio 2026 | Actualización del estado del proyecto tras completar la plataforma base. Incorporación de la filosofía Infrastructure as Code, reorganización de la estructura física del proyecto y documentación de la arquitectura de runtime (Docker, containerd y Ollama). |
| 0.3 | Julio 2026 | Reorganización del documento, incorporación de la nueva estructura documental, actualización del estado del proyecto y preparación para la fase de desarrollo. |
| 0.2 | Julio 2026 | Actualización de GitHub, autenticación SSH, estructura del repositorio y estado de la infraestructura. |
| 0.1 | Julio 2026 | Creación del documento. |