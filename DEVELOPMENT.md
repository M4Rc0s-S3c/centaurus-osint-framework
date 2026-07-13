# DEVELOPMENT.md

# CENTAURUS OSINT Framework
## Guía de Desarrollo

> **Estado:** Documento de referencia para el desarrollo del MVP v1.0

---

# 1. Objetivo

Este documento establece las directrices para el desarrollo de **CENTAURUS OSINT Framework**.

Su finalidad es garantizar que todos los componentes se implementen siguiendo una arquitectura homogénea, modular, mantenible y fácilmente extensible.

---

# 2. Filosofía del desarrollo

Durante el desarrollo deberán respetarse las siguientes decisiones de diseño:

- El Core nunca contendrá lógica específica de herramientas.
- Todas las herramientas serán plugins independientes.
- El Core únicamente orquestará la ejecución.
- El LLM nunca ejecutará herramientas directamente.
- El Rule Engine será el único responsable de generar hallazgos.
- El LLM únicamente interpretará peticiones y redactará informes.
- Todo el sistema deberá poder ejecutarse completamente en local.
- Todo componente deberá ser fácilmente sustituible.

---

# 3. Entorno de desarrollo

## Sistema operativo

- Debian GNU/Linux 13

## Lenguaje principal

- Python 3

## Control de versiones

- Git

## Repositorio remoto

```
git@github.com:M4Rc0s-S3c/centaurus-osint-framework.git
```

## Repositorio local

```
/opt/osint-framework/centaurus
```

## Rama principal

```
main
```

## Autenticación

- SSH
- Claves ED25519

No se utilizará autenticación HTTPS.

---

# 4. Tecnologías

| Componente | Tecnología |
|------------|------------|
| Contenedores | Docker |
| Orquestación | Docker Compose |
| LLM | Ollama |
| Modelo inicial | Qwen3:4B Instruct |

---

# 5. Librerías previstas

| Librería | Uso |
|-----------|--------------------------------|
| Typer | CLI |
| Rich | Interfaz de consola |
| Prompt Toolkit | Entrada interactiva |
| httpx | Comunicación HTTP |
| Pydantic | Modelos de datos |
| Pytest | Testing |
| Ruff | Calidad del código |

---

# 6. Organización del proyecto

```
centaurus/
│
├── src/
│   ├── core/
│   ├── planner/
│   ├── executor/
│   ├── evidence/
│   ├── reporting/
│   ├── cli/
│   └── llm/
│
├── plugins/
│
├── rules/
│
├── docker/
│
├── config/
│
├── scripts/
│
├── docs/
│
├── tests/
│
├── README.md
├── PROJECT.md
├── ARCHITECTURE.md
├── STORAGE.md
├── INSTALL.md
├── DEVELOPMENT.md
├── ROADMAP.md
├── docker-compose.yml
└── requirements.txt
```

> Los datos persistentes (workspace, modelos, informes, evidencias y logs) no forman parte del repositorio Git y residen fuera del árbol del código.

---

# 7. Flujo de trabajo con Git

Actualizar el repositorio:

```bash
git pull
```

Consultar estado:

```bash
git status
```

Añadir cambios:

```bash
git add .
```

Crear commit:

```bash
git commit -m "Descripción del cambio"
```

Enviar cambios:

```bash
git push
```

---

# 8. Convenciones de desarrollo

## Core

El Core nunca contendrá código específico de herramientas.

---

## Plugins

Cada herramienta deberá implementarse como un plugin independiente.

Cada plugin será responsable de:

- recibir parámetros
- ejecutar la herramienta
- normalizar resultados
- devolver evidencias al Core

---

## Rules

Las reglas estarán completamente desacopladas del código.

Su función será:

- analizar evidencias
- detectar hallazgos
- asignar severidad
- generar recomendaciones

Nunca deberán contener lógica propia de ejecución de herramientas.

---

# 9. Flujo de desarrollo

## Fase 1

- Crear estructura del proyecto.
- Configurar Docker.
- Configurar CLI.

## Fase 2

- Implementar Core.
- Plugin Manager.
- Executor.

## Fase 3

- Implementar herramientas OSINT.

## Fase 4

- Evidence Manager.

## Fase 5

- Rule Engine.

## Fase 6

- Integración con Ollama.

## Fase 7

- Generación de informes.

## Fase 8

- Validación y pruebas.

---

# 10. Calidad del código

Antes de aceptar cualquier cambio deberán ejecutarse:

- Ruff
- Pytest

El código deberá mantenerse:

- tipado
- documentado
- modular
- desacoplado

---

# 11. Docker

Todos los componentes deberán diseñarse pensando en su ejecución mediante Docker.

Los datos persistentes se almacenarán fuera de los contenedores.

---

# 12. Persistencia

Toda la información generada deberá almacenarse dentro del Workspace.

Nunca deberán utilizarse rutas absolutas codificadas en el código fuente.

---

# 13. Objetivo del MVP

Al finalizar el desarrollo el framework deberá ser capaz de:

- Interpretar peticiones en lenguaje natural.
- Generar un TaskPlan.
- Ejecutar herramientas OSINT.
- Normalizar evidencias.
- Aplicar Rules.
- Generar hallazgos.
- Elaborar informes técnicos.
- Mostrar resultados en la CLI.
- Exportar informes en Markdown y JSON.

---

# Historial

| Versión | Fecha | Cambios |
|----------|--------|---------|
| 0.2 | Julio 2026 | Actualizada la arquitectura de desarrollo, Git, GitHub SSH, estructura del repositorio y motor de Rules. |
| 0.1 | Julio 2026 | Documento inicial. |