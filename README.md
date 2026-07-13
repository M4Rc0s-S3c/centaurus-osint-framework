# CENTAURUS OSINT Framework

Framework modular de inteligencia de fuentes abiertas (OSINT) diseñado para equipos Blue Team y departamentos de TI, basado en una arquitectura extensible mediante plugins, un motor de reglas determinista y un modelo de lenguaje local para la interpretación de peticiones y la generación de informes.

El objetivo del proyecto es proporcionar una plataforma autocontenida capaz de recopilar, correlacionar y analizar información pública sobre activos corporativos utilizando exclusivamente técnicas OSINT pasivas.

---

# Estado del proyecto

🚧 **En desarrollo (MVP v1.0)**

Actualmente el proyecto se encuentra en la fase de construcción de la infraestructura base y del framework.

---

# Orden de lectura recomendado

La documentación está organizada en documentos independientes. Para obtener una visión progresiva del proyecto, se recomienda el siguiente orden de lectura:

1. **PROJECT.md** — Visión general del proyecto.
2. **SPECIFICATION.md** — Especificación funcional y alcance del framework.
3. **STANDARDS.md** — Estándares y convenciones oficiales.
4. **ARCHITECTURE.md** — Arquitectura técnica del sistema.
5. **STORAGE.md** — Arquitectura de almacenamiento.
6. **INSTALL.md** — Instalación y preparación del entorno.
7. **DEVELOPMENT.md** — Guía para el desarrollo.
8. **ROADMAP.md** — Estado del proyecto y planificación futura.
9. **CHANGELOG.md** — Historial de cambios y evolución del proyecto.

---

# Documentación

La documentación del proyecto se organiza de la siguiente forma:

| Documento | Propósito |
|-----------|-----------|
| **README.md** | Portada del repositorio. Punto de entrada al proyecto y guía de navegación de toda la documentación. |
| **PROJECT.md** | Información general del proyecto: identidad, objetivos, tecnologías empleadas, arquitectura de alto nivel y estado actual. |
| **SPECIFICATION.md** | Especificación funcional del framework: alcance, requisitos, casos de uso, arquitectura conceptual y criterios de aceptación del MVP. |
| **STANDARDS.md** | Estándares y convenciones oficiales del proyecto. Documento normativo que define las reglas de diseño, desarrollo y organización. |
| **ARCHITECTURE.md** | Arquitectura técnica del framework, descripción de los componentes, flujo de ejecución y relaciones entre módulos. |
| **STORAGE.md** | Arquitectura de almacenamiento, organización de discos, particiones, puntos de montaje y persistencia de datos. |
| **INSTALL.md** | Procedimiento completo para desplegar y configurar el entorno desde una instalación limpia hasta dejar la plataforma operativa. |
| **DEVELOPMENT.md** | Guía para el desarrollo del framework: entorno de trabajo, estructura del código, flujo de desarrollo y buenas prácticas. |
| **ROADMAP.md** | Planificación del proyecto, hitos de desarrollo, estado de avance y evolución prevista del framework. |
| **CHANGELOG.md** | Historial de cambios del proyecto, versiones publicadas y evolución funcional siguiendo el estándar *Keep a Changelog*. |

---

# Organización del repositorio

```text
centaurus/
│
├── src/
├── plugins/
├── rules/
├── config/
├── scripts/
├── docs/
├── tests/
│
├── README.md
├── PROJECT.md
├── SPECIFICATION.md
├── STANDARDS.md
├── ARCHITECTURE.md
├── STORAGE.md
├── INSTALL.md
├── DEVELOPMENT.md
├── ROADMAP.md
├── CHANGELOG.md
│
├── docker-compose.yml
└── requirements.txt
```

---

# Objetivos del MVP

El objetivo de la primera versión del framework es proporcionar una plataforma capaz de:

- Interpretar peticiones en lenguaje natural.
- Generar automáticamente un TaskPlan.
- Ejecutar herramientas OSINT de forma modular.
- Normalizar evidencias obtenidas.
- Aplicar reglas deterministas para generar hallazgos.
- Elaborar informes técnicos.
- Exportar informes en formato Markdown y JSON.

---

# Licencia

Pendiente de definir.

---

# Autor

Proyecto desarrollado como parte de un **Trabajo Fin de Máster (TFM)** sobre el diseño e implementación de un framework OSINT modular basado en inteligencia artificial local.