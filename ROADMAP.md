# ROADMAP.md

# CENTAURUS OSINT Framework

## Roadmap de Desarrollo

**Versión:** MVP v1.0

**Estado:** Fase de implementación

---

# Objetivo

Este documento define la planificación del desarrollo del proyecto **CENTAURUS OSINT Framework**, organizando las tareas por fases y permitiendo realizar el seguimiento del estado del proyecto.

Cada fase representa un conjunto de hitos necesarios para alcanzar la primera versión funcional (MVP).

---

# Design Freeze

Se considera finalizada la fase de análisis y diseño del proyecto.

Los siguientes elementos quedan congelados para el desarrollo del MVP:

- [x] Objetivos del proyecto.
- [x] Requisitos funcionales.
- [x] Arquitectura general.
- [x] Arquitectura de almacenamiento.
- [x] Arquitectura Docker.
- [x] Arquitectura basada en plugins.
- [x] Rule Engine determinista.
- [x] Flujo de ejecución.
- [x] Workspace.
- [x] Modelo LLM.
- [x] Herramientas OSINT del MVP.
- [x] Estándares del proyecto.
- [x] Organización documental.

A partir de este punto cualquier modificación de diseño deberá justificarse y documentarse.

---

# Fase 0 - Diseño

## Arquitectura

- [x] Definición de objetivos.
- [x] Definición de requisitos.
- [x] Diseño funcional.
- [x] Diseño técnico.
- [x] Diseño del almacenamiento.
- [x] Diseño del Workspace.
- [x] Diseño del Rule Engine.
- [x] Diseño de Docker.
- [x] Selección del LLM.
- [x] Selección de herramientas OSINT.
- [x] Definición de estándares.
- [x] Documentación del proyecto.

**Estado:** ✅ Finalizada

---

# Fase 1 - Infraestructura

## Sistema base

- [x] Instalación de Debian.
- [x] Configuración UEFI.
- [x] Configuración de discos.
- [x] Configuración de puntos de montaje.
- [x] Configuración de `/etc/fstab`.
- [x] Validación del almacenamiento.
- [x] Actualización del sistema.
- [x] Snapshot de infraestructura.
- [x] Clon de desarrollo.

## Red

- [x] Configuración mediante DHCP.
- [x] Validación de conectividad.
- [x] Validación DNS.
- [x] Validación NTP.

## Acceso remoto

- [x] Instalación de OpenSSH Server.
- [x] Configuración del servicio.
- [x] Validación desde Windows.

## Git

- [x] Instalación de Git.
- [x] Creación del repositorio GitHub.
- [x] Configuración SSH (ED25519).
- [x] Clonado del repositorio.

**Estado:** ✅ Finalizada

---

# Fase 2 - Plataforma

## Docker

- [x] Instalación de Docker Engine.
- [x] Instalación de Docker Compose.
- [ ] Creación de la red Docker.
- [ ] Configuración de volúmenes.
- [ ] Primer docker-compose.yml.

## Inteligencia Artificial

- [ ] Instalación de Ollama.
- [ ] Descarga de Qwen3:4B Instruct.
- [ ] Validación del modelo.

**Estado:** ⬜ Pendiente

---

# Fase 3 - Core Framework

## Núcleo

- [ ] Crear estructura del proyecto.
- [ ] Configuración inicial.
- [ ] Core.
- [ ] Config Manager.
- [ ] Logging.
- [ ] Workspace Manager.
- [ ] Plugin Manager.
- [ ] Descubrimiento automático.
- [ ] API interna.

---

# Fase 4 - Herramientas OSINT

## MVP

- [ ] whois_lookup
- [ ] rdap_lookup
- [ ] DNSRecon
- [ ] Sublist3r
- [ ] TheHarvester
- [ ] crtsh_lookup

---

# Fase 5 - Rule Engine

- [ ] Parser.
- [ ] Motor de reglas.
- [ ] Carga dinámica.
- [ ] Correlación.
- [ ] Clasificación.
- [ ] Recomendaciones.

---

# Fase 6 - Inteligencia Artificial

- [ ] Planificación mediante LLM.
- [ ] Interpretación de resultados.
- [ ] Generación de informes.
- [ ] Resumen ejecutivo.

---

# Fase 7 - Reporting

- [ ] Markdown.
- [ ] JSON.
- [ ] Evidencias.
- [ ] Riesgo.
- [ ] Exportación.

---

# Fase 8 - Workspace

- [ ] Evidencias.
- [ ] Informes.
- [ ] Logs.
- [ ] Caché.
- [ ] Limpieza.

---

# Fase 9 - Validación

- [ ] Flujo completo.
- [ ] Casos de uso.
- [ ] Rule Engine.
- [ ] Informes.
- [ ] Rendimiento.

---

# Fase 10 - Release

- [ ] Revisión de OpenSSH.
- [ ] Eliminación de paquetes innecesarios.
- [ ] Optimización.
- [ ] Generación de OVA.
- [ ] Validación desde USB.
- [ ] Revisión documental.

---

# Futuras versiones

## v1.1

- Exportación PDF.
- Nuevas herramientas OSINT.
- Nuevas reglas.
- Nuevos modelos LLM.
- Integración STIX.
- Integración TAXII.

---

# Estado actual

| Fase | Estado |
|-------|--------|
| Design Freeze | ✅ Completado |
| Diseño | ✅ Completado |
| Infraestructura | ✅ Completado |
| Plataforma | 🟡 Próxima fase |
| Core Framework | ⬜ Pendiente |
| Herramientas OSINT | ⬜ Pendiente |
| Rule Engine | ⬜ Pendiente |
| Inteligencia Artificial | ⬜ Pendiente |
| Reporting | ⬜ Pendiente |
| Workspace | ⬜ Pendiente |
| Validación | ⬜ Pendiente |
| Release | ⬜ Pendiente |

---

# Próximo hito

**Inicio de la implementación del framework**

Las siguientes tareas marcarán el comienzo del desarrollo del MVP:

1. Instalación de Docker Engine.
2. Instalación de Docker Compose.
3. Instalación de Ollama.
4. Descarga del modelo Qwen3:4B Instruct.
5. Creación de la estructura inicial del framework.
6. Primer commit de la implementación.

---

# Historial

| Versión | Fecha | Cambios |
|----------|--------|---------|
| 0.3 | Julio 2026 | Aplicación del Design Freeze, reorganización de fases y preparación del inicio de la implementación. |
| 0.2 | Julio 2026 | Actualización de la infraestructura y planificación del MVP. |
| 0.1 | Julio 2026 | Creación del roadmap inicial. |