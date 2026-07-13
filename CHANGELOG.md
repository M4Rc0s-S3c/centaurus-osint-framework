# CHANGELOG.md

# Historial de Cambios

Todos los cambios relevantes del proyecto **CENTAURUS OSINT Framework** se documentan en este archivo.

Este documento sigue las recomendaciones del estándar **Keep a Changelog** y utiliza un esquema de versionado basado en **Semantic Versioning (SemVer)**.

---

# Versionado

El proyecto utiliza el siguiente esquema de versionado:

```text
MAJOR.MINOR.PATCH
```

Ejemplo:

```text
1.0.0
```

Donde:

- **MAJOR**: cambios incompatibles con versiones anteriores.
- **MINOR**: incorporación de nuevas funcionalidades compatibles.
- **PATCH**: correcciones de errores y mejoras menores sin cambios funcionales.

---

# Tipos de cambios

Las modificaciones se clasifican utilizando las siguientes categorías:

- **Added** → Nuevas funcionalidades.
- **Changed** → Cambios en funcionalidades existentes.
- **Deprecated** → Funcionalidades en proceso de eliminación.
- **Removed** → Funcionalidades eliminadas.
- **Fixed** → Corrección de errores.
- **Security** → Mejoras relacionadas con la seguridad.

---

# [0.2.0] - En desarrollo

## Added

### Plataforma

- Instalación de Docker Engine desde el repositorio oficial de Docker.
- Instalación de Docker Compose Plugin.
- Validación del servicio Docker.
- Validación del motor Docker mediante contenedor de prueba.


## Planned

### Plataforma

- Creación del proyecto Docker Compose.
- Instalación de Ollama.
- Descarga del modelo Qwen3:4B Instruct.


### Framework

- Creación de la estructura inicial del proyecto.
- Implementación del Core.
- Configuración inicial del Workspace.
- Primer prototipo de la CLI.

---

# [0.1.0] - Julio 2026

## Added

### Infraestructura

- Instalación base de Debian 13.
- Configuración del firmware UEFI.
- Arquitectura de almacenamiento con discos independientes para:
  - Sistema (`/`)
  - Plataforma (`/opt/osint-framework`)
  - Workspace (`/workspace`)
- Configuración persistente mediante `/etc/fstab`.
- Validación de los puntos de montaje.
- Actualización completa del sistema (`apt update` y `apt upgrade`).
- Configuración de red mediante DHCP.
- Validación de conectividad.
- Validación de resolución DNS.
- Validación de sincronización horaria (NTP).
- Instalación y configuración de OpenSSH Server.
- Verificación del acceso remoto desde Windows.
- Creación del snapshot **"01 - Infraestructura Base"**.
- Creación del clon de desarrollo en VMware.
- Creación del snapshot **"02 - Desarrollo preparado (Design Freeze)"**.



### Control de versiones

- Instalación de Git.
- Creación del repositorio privado en GitHub.
- Configuración de autenticación SSH mediante claves ED25519.
- Clonado del repositorio en:

```text
/opt/osint-framework/centaurus
```

### Documentación

Se establece la estructura documental oficial del proyecto:

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

### Arquitectura

- Definición de la arquitectura modular basada en plugins.
- Definición del Rule Engine determinista.
- Definición del flujo de ejecución del framework.
- Definición del Workspace persistente.
- Definición de la arquitectura Docker.
- Definición de la organización del repositorio.
- Definición de la estructura documental.

### Inteligencia Artificial

- Selección de Ollama como motor LLM local.
- Selección del modelo Qwen3:4B Instruct para el MVP.

### Diseño

- Finalización del diseño funcional del framework.
- Aplicación del **Design Freeze** para el MVP v1.0.
- Congelación de la arquitectura, estándares y especificaciones funcionales.

---

# Referencias

- Semantic Versioning: https://semver.org/
- Keep a Changelog: https://keepachangelog.com/