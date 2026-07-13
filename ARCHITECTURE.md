# ARCHITECTURE.md

# Arquitectura técnica del Framework OSINT
# Información del proyecto

| Campo | Valor |
|--------|-------|
| Nombre | CENTAURUS OSINT Framework |
| Repositorio | centaurus-osint-framework |
| Plataforma | Debian 13 |
| Arquitectura | Modular |
| Contenedorización | Docker |
| LLM local | Ollama |
| Modelo inicial | Qwen3:4B Instruct |

## Objetivo

Definir la arquitectura técnica de referencia para el desarrollo del
framework OSINT local orientado a equipos Blue Team.

## Decisiones tecnológicas adoptadas

  Componente                Tecnología seleccionada
  ------------------------- -------------------------
  Sistema operativo         Debian mínimo
  Contenedorización         Docker + Docker Compose
  Lenguaje                  Python 3
  LLM local                 Ollama
  Modelo LLM                Qwen3:4B Instruct
  Interfaz CLI              Typer
  Presentación en consola   Rich
  Entrada interactiva       Prompt Toolkit
  Comunicación HTTP         httpx
  Modelado de datos         Pydantic
  Calidad de código         Ruff
  Pruebas                   Pytest

## Principios de diseño

-   Ejecución completamente local.
-   Sin dependencias de servicios cloud.
-   Sin APIs comerciales obligatorias.
-   Arquitectura modular basada en plugins.
-   Análisis OSINT exclusivamente pasivo.
-   Separación entre recopilación de evidencias, correlación y
    generación del informe.
-   Un único LLM para planificación y generación de informes.

## Arquitectura lógica

``` text
Analista
    │
    ▼
CLI (Typer + Rich + Prompt Toolkit)
    │
    ▼
LLM Local (Ollama + Qwen3:4B Instruct)
    │
    ▼
TaskPlan
    │
    ▼
Core Framework
    │
 ┌──┼───────────────┐
 ▼  ▼               ▼
Plugin Manager  Executor  Evidence Manager
                   │
                   ▼
             Herramientas OSINT
                   │
                   ▼
        Normalización de evidencias
                   │
                   ▼
              Rule Engine
                   │
                   ▼
               Hallazgos
                   │
                   ▼
LLM Local (Ollama + Qwen3:4B Instruct)
                   │
        ┌──────────┴──────────┐
        ▼                     ▼
 CLI (Rich)          Informes Markdown / JSON
```

## Componentes

### LLM local

Responsabilidades: - Interpretar la petición. - Generar el TaskPlan. -
Redactar el informe final.

El modelo no ejecuta herramientas ni determina el riesgo.

### Core Framework

Coordina toda la ejecución mediante: - Plugin Manager - Executor -
Evidence Manager - Rule Engine

### Herramientas del MVP

-   whois_lookup
-   rdap_lookup
-   DNSRecon
-   Sublist3r
-   TheHarvester
-   crtsh_lookup

## Workspace

``` text
workspace/
├── reports/
├── evidence/
├── logs/
├── cache/
└── tmp/
```

El directorio será configurable y se montará como volumen Docker
persistente.

## Flujo de ejecución

1.  El analista realiza una petición desde la CLI.
2.  El LLM interpreta la petición.
3.  Se genera un TaskPlan.
4.  El Core ejecuta las herramientas.
5.  Las evidencias se normalizan y almacenan.
6.  El Rule Engine genera los hallazgos.
7.  El LLM redacta el informe.
8.  El informe se presenta en la CLI y se almacena en Markdown y JSON.

## Decisiones congeladas del MVP

-   Un único LLM local (Ollama + Qwen3:4B Instruct).
-   Framework completamente dockerizado.
-   Análisis OSINT pasivo.
-   Arquitectura basada en plugins.
-   Rule Engine determinista.
-   CLI como única interfaz de usuario.
-   Informes en Markdown y JSON.
-   Workspace configurable e independiente del Core.
