# Arquitectura de CENTAURUS

**Estado:** FINAL · arquitectura estable y distribución final validada

## 1. Propósito

CENTAURUS es un framework OSINT modular orientado a **Public Exposure Assessment** para equipos Blue Team y departamentos IT de PYMEs. Separa adquisición, normalización, razonamiento determinista, reporting y asistencia lingüística.

## 2. Principios estructurales

- `Investigation` organiza el dominio; la arquitectura no gira alrededor de tools o LLM.
- **Core** es el único custodio de Investigation y autoridad de su lifecycle.
- Core coordina el flujo macroscópico e integra conocimiento, pero **no debe mediar en cada colaboración interna**: son válidas dependencias expresamente definidas por contrato, como `Executor → PluginManager`.
- Están prohibidas dependencias laterales no documentadas, acceso a implementaciones concretas saltándose contratos y transferencia de responsabilidades entre componentes.
- Cada componente mantiene responsabilidad única y contrato público mínimo.
- Plugins no se ejecutan desde Core ni Planner; Executor delega cada `ExecutionTask` en PluginManager.
- El dominio no depende de Docker, Ollama, filesystem, plugins concretos ni interfaz.
- La seguridad combina autoridad clara con controles explícitos en las fronteras relevantes.
- Los componentes estructurales viven bajo el composition root/Core; recursos internos pesados pueden adquirirse/liberarse bajo demanda.

## 3. Capas y conceptos

```text
Analista
  ↓
CLI / RequestInterpreter
  ↓
StructuredRequest
  ↓
Core
  ├─ Planner → ExecutionPlan / ExecutionTask
  ├─ Executor → PluginManager → Plugin
  ├─ EvidenceManager
  ├─ RuleEngine
  ├─ ReportManager
  ├─ LLMManager
  └─ Persistence Layer / Stores

Dominio:
Investigation · Target · Intent · Rule · Evidence · Finding · Report
```

### Dominio

- Investigation
- Target
- Intent
- Rule
- Evidence
- Finding
- Report

### Aplicación / runtime

- StructuredRequest
- RequestInterpreter
- Core
- Planner
- ExecutionPlan
- ExecutionTask
- Executor
- PluginManager
- RawObservation
- EvidenceManager
- ExecutionFailure
- RuntimeProgressReporter/adapters

`RuleEngine` es un servicio de dominio; `ReportManager` materializa el contrato de generación de Report bajo coordinación de Core. Los managers/componentes no se convierten por ello en conocimiento persistido.

### Infraestructura/presentación

- plugins concretos y herramientas externas;
- stores/filesystem/JSON;
- Ollama/provider LLM;
- Docker/Compose;
- logging;
- HTTP/subprocess;
- CLI/Rich/Prompt Toolkit.

## 4. Frontera de entrada

La interfaz puede realizar trabajo de aplicación previo, pero ninguna interfaz crea/modifica Investigation directamente.

```text
Lenguaje natural
  ↓
RequestInterpreter
  ├─ TargetFactory (determinista)
  └─ LLM #1 (Intent permitido)
  ↓
StructuredRequest
  ↓
Core crea Investigation
```

Core no recibe lenguaje natural ni utiliza LLM para planificar herramientas.

## 5. Flujo funcional vigente

```text
Investigation
  ↓
Planner → ExecutionPlan
  ↓
Executor recorre ExecutionTask secuencialmente
  ↓
PluginManager resuelve/invoca Plugin
  ↓
RawObservation
  ↓ persist RAW
Normalización tool-specific
  ↓
EvidenceManager → Evidence
  ↓ persist Evidence
RuleEngine + Rules → Finding(s)
  ↓ persist Finding
ReportManager → Report
  ↓ persist Report (report.json + report.md)
LLM #2
  ↓
presentación efímera/no autoritativa
```

Los fallos de tools se modelan mediante `ExecutionFailure`, se persisten separadamente y no entran en este flujo de conocimiento.

## 6. Frontera de despliegue

La arquitectura de componentes no implica un contenedor por componente. La frontera documentada de despliegue separa:

- `centaurus-core`: framework y ejecución de tools;
- `centaurus-ollama`: servicio LLM local.

Las tools externas con runtimes Python incompatibles se aíslan mediante entornos dedicados de la versión de entrega sin modificar el contrato de plugin.

### Plano host de la appliance

Fuera del dominio/Core existe una frontera operacional mínima:

```text
usuario centaurus
  ├─ `centaurus` → autenticación → broker runtime → shell CENTAURUS
  └─ `centaurus-poweroff` → autenticación → helper poweroff → systemd poweroff
```

Esta frontera no convierte la CLI ni el Core en componentes privilegiados y no concede una capacidad `sudo` general al analista.

## 7. Evolución

La arquitectura conceptual se reabre cuando cambia el dominio, una frontera de autoridad o un contrato público real. Una nueva tool, versión o ruta física no constituye por sí sola evolución del dominio.

## 8. Ajuste operacional OLLAMA-D2

D2 refina únicamente la infraestructura de asistencia posterior al Report. LLM #2 utiliza un provider configurado para Reports grandes con `timeout=300`, `num_ctx=8192` y `num_predict=UNSET`; LLM #1 conserva su perfil previo. `think=false`, `keep_alive=0`, grounding y ausencia de reintentos se mantienen.

La modificación no altera las dependencias de autoridad: Planner sigue seleccionando tools, RuleEngine sigue produciendo Findings y Report continúa siendo el extremo autoritativo/persistido. Un fallo de LLM #2 se degrada como fallo operacional de presentación.

## 9. Materialización de distribución y alcance arquitectónico

El cierre C4-RS2/G4 demuestra que OVA, Git + Docker Linux y USB son modalidades de empaquetado/materialización del mismo producto. La imagen USB conserva las fronteras lógicas SYSTEM/PLATFORM/WORKSPACE sobre un único GPT; esta diferencia física no modifica el modelo de dominio ni el lifecycle de Investigation.

La validación N7 sobre una NIC física real confirma que `centaurus0` es el nombre lógico del uplink y no una dependencia de la vNIC E1000 de VMware. La evidencia física tampoco modifica las dependencias entre Core, Planner, plugins, RuleEngine, Report y LLM.


## Base documental

Constitución Arquitectónica v2.0; ADR v3.2; Modelo Conceptual v3.5; Contrato Core v2.5; Runtime v2.10; Knowledge Pipeline v2.1; Tools-Plugins v2.4; Contrato LLM v2.6; Reporting v1.5; OLLAMA-D2 R2.
