# SPECIFICATION.md

# CENTAURUS OSINT Framework
## Especificación Funcional y Técnica

> **Estado:** Documento de referencia del proyecto (MVP v1.0)

Este documento define la especificación funcional del **CENTAURUS OSINT Framework**. Su objetivo es consolidar las decisiones funcionales adoptadas para el MVP y servir como referencia para el desarrollo, la validación y la memoria del Trabajo Fin de Máster (TFM).

---

# 1. Objetivo del proyecto

Desarrollar una plataforma OSINT portable, modular y autocontenida orientada a equipos Blue Team y departamentos de TI de pequeñas y medianas organizaciones.

La solución deberá permitir identificar, recopilar, correlacionar y analizar información pública sobre activos corporativos mediante técnicas OSINT pasivas, integrando un modelo de lenguaje local para interpretar las peticiones del analista y elaborar informes técnicos.

---

# 2. Alcance del MVP

El producto deberá proporcionar las siguientes capacidades:

- Análisis OSINT exclusivamente pasivo.
- Ejecución completamente local.
- Arquitectura modular basada en plugins.
- Framework desplegable mediante Docker.
- Interfaz CLI conversacional.
- Motor de reglas determinista.
- Generación automática de informes.
- Exportación de resultados en Markdown y JSON.
- Sin dependencia obligatoria de APIs comerciales.
- Sin análisis activo (Nmap u otras herramientas de enumeración activa quedan fuera del MVP).

---

# 3. Usuarios objetivo

El framework está dirigido a:

- Equipos Blue Team.
- Departamentos de TI.
- Consultores de ciberseguridad.
- Analistas OSINT.
- Investigadores de seguridad.

---

# 4. Casos de uso principales

El sistema deberá permitir:

- Analizar dominios corporativos.
- Obtener información WHOIS y RDAP.
- Enumerar registros DNS públicos.
- Descubrir subdominios.
- Localizar certificados públicos.
- Identificar direcciones de correo asociadas.
- Correlacionar evidencias.
- Generar hallazgos mediante reglas.
- Elaborar informes técnicos.

---

# 5. Arquitectura funcional

El flujo funcional del sistema será:

```text
Analista
      │
      ▼
CLI Conversacional
      │
      ▼
LLM Local (Qwen3)
      │
      ▼
TaskPlan
      │
      ▼
Core
      │
      ▼
Plugin Manager
      │
      ▼
Executor
      │
      ▼
Plugins OSINT
      │
      ▼
Evidence Manager
      │
      ▼
Rule Engine
      │
      ▼
Hallazgos
      │
      ▼
LLM Local
      │
      ▼
Informe
```

---

# 6. Papel del LLM

El modelo local realizará únicamente dos funciones:

1. Interpretación de las peticiones del usuario.
2. Redacción del informe final.

El modelo **no** tomará decisiones técnicas.

No determinará:

- Riesgos.
- Severidad.
- Recomendaciones.
- Hallazgos.

Estas funciones corresponderán exclusivamente al Rule Engine.

---

# 7. Rule Engine

El Rule Engine constituye el núcleo de análisis del framework.

Será responsable de:

- Correlacionar evidencias.
- Detectar hallazgos.
- Asignar severidad.
- Generar recomendaciones.
- Clasificar resultados.

Todas las reglas serán deterministas y completamente independientes del LLM.

---

# 8. Herramientas OSINT previstas para el MVP

| Herramienta | Función |
|-------------|---------|
| whois_lookup | Información WHOIS |
| rdap_lookup | Información RDAP |
| DNSRecon | Enumeración DNS |
| Sublist3r | Descubrimiento de subdominios |
| TheHarvester | Correos y activos relacionados |
| crtsh_lookup | Certificate Transparency |

La incorporación de nuevas herramientas no requerirá modificaciones en el Core.

---

# 9. Requisitos funcionales

El sistema deberá ser capaz de:

- Interpretar peticiones en lenguaje natural.
- Generar un TaskPlan.
- Ejecutar plugins.
- Normalizar evidencias.
- Aplicar reglas.
- Generar hallazgos.
- Elaborar informes técnicos.
- Exportar resultados.

---

# 10. Requisitos no funcionales

El sistema deberá cumplir:

- Arquitectura modular.
- Portabilidad.
- Escalabilidad.
- Reproducibilidad.
- Funcionamiento offline.
- Desacoplamiento entre componentes.
- Persistencia independiente.
- Mantenibilidad.
- Extensibilidad mediante plugins.

---

# 11. Restricciones

Durante el MVP no se contempla:

- Escaneo activo.
- Vulnerability Assessment.
- Integración SIEM.
- APIs comerciales obligatorias.
- Dependencia de servicios cloud.
- Ejecución distribuida.

---

# 12. Informes

El framework generará informes en:

- Markdown (.md)
- JSON (.json)

Los informes deberán incluir:

- Resumen ejecutivo.
- Evidencias.
- Hallazgos.
- Recomendaciones.
- Metadatos de ejecución.

---

# 13. Criterios de aceptación del MVP

El MVP se considerará completado cuando sea capaz de:

- Interpretar una petición en lenguaje natural.
- Generar automáticamente un TaskPlan.
- Ejecutar las herramientas OSINT previstas.
- Normalizar todas las evidencias.
- Aplicar reglas deterministas.
- Generar hallazgos.
- Elaborar un informe técnico.
- Mostrar el resultado en la CLI.
- Exportar el informe en Markdown y JSON.

---

# 14. Exclusiones del MVP

Quedan fuera del alcance inicial:

- Interfaz gráfica.
- Multiusuario.
- Alta disponibilidad.
- Balanceo de carga.
- Procesamiento distribuido.
- Gestión centralizada de credenciales.
- Automatización CI/CD.

---

# 15. Relación con la documentación

Este documento define **qué es el producto**.

Los aspectos técnicos se desarrollan en el resto de la documentación:

| Documento | Contenido |
|-----------|-----------|
| PROJECT.md | Identidad del proyecto |
| STANDARDS.md | Estándares y convenciones |
| ARCHITECTURE.md | Arquitectura técnica |
| STORAGE.md | Arquitectura de almacenamiento |
| INSTALL.md | Instalación del entorno |
| DEVELOPMENT.md | Guía de desarrollo |
| ROADMAP.md | Planificación del proyecto |

---

# Historial

| Versión | Fecha | Cambios |
|----------|--------|---------|
| 2.0 | Julio 2026 | Reestructuración completa como especificación funcional del proyecto. |
| 1.0 | Julio 2026 | Documento inicial. |