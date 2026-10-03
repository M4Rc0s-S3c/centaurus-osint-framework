# Arquitectura de CENTAURUS

[Español](ARCHITECTURE.md) | [English](ARCHITECTURE.en.md)
[Inicio](../README.md) · [Proyecto](PROJECT.md) · [Especificación](SPECIFICATION.md) · [Persistencia](STORAGE.md)

## 1. Propósito

CENTAURUS utiliza una arquitectura modular para separar adquisición OSINT, normalización, razonamiento determinista, persistencia, reporting y asistencia lingüística local.

La arquitectura está diseñada para que la incorporación de nuevas herramientas no obligue a rediseñar el Core ni el modelo de dominio.

## 2. Principios estructurales

- `Investigation` organiza el dominio.
- El **Core** es el custodio del ciclo de vida de `Investigation`.
- Los componentes colaboran mediante contratos públicos explícitos.
- `Executor` delega la ejecución en `PluginManager`.
- Los plugins no producen directamente `Evidence`, `Finding` ni `Report`.
- El dominio no depende de Docker, Ollama, filesystem o herramientas concretas.
- Las decisiones analíticas autoritativas son deterministas.
- Los recursos pesados pueden adquirirse/liberarse bajo demanda.
- Las fronteras de seguridad mantienen autoridad y mínimo privilegio.

Los resultados deterministas, la trazabilidad directa e inversa y la modularidad por contratos son criterios de diseño que atraviesan estas capas. Cada hallazgo debe conservar su regla y sus evidencias de apoyo; la presentación debe respetar esa autoridad. Un cambio de componente debe preservar esas relaciones y los contratos públicos de sus consumidores. El Core coordina el flujo que las mantiene.

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

- `Investigation`
- `Target`
- `Intent`
- `Rule`
- `Evidence`
- `Finding`
- `Report`

| Concepto | Responsabilidad e invariante |
| --- | --- |
| `Investigation` | Agregado con identidad propia; Core coordina su ciclo e integración de conocimiento. Una ejecución nueva crea un caso nuevo. |
| Target / Intent | Identifican el objeto investigado y el propósito permitido. No seleccionan herramientas arbitrarias ni representan hallazgos. |
| `Rule` | Criterio determinista versionado, separado del formato de salida de una herramienta. |
| `Evidence` | Observación normalizada que conserva fuente y tiempo de recogida; no es una conclusión analítica. |
| `Finding` | Conclusión producida por RuleEngine, conservando su regla y evidencias de apoyo. |
| `Report` | Snapshot que consolida hallazgos y contexto del caso; se construye antes de LLM #2 y se persiste mediante stores. |

En la implementación actual, `Investigation` guarda `target`, `target_type` e `intent` como valores; la distinción conceptual no implica tres objetos de dominio anidados. Sus métodos validan la integración de conocimiento, mientras el contrato arquitectónico asigna al Core la coordinación del ciclo.

`RawObservation`, `StructuredRequest`, `ExecutionPlan`, `ExecutionTask` y `ExecutionFailure` son objetos de aplicación u operación. La asistencia LLM y el progreso son superficies de presentación; no crean conocimiento de dominio. Los estados y la ejecución parcial se detallan en [`CORE_RUNTIME.md`](CORE_RUNTIME.md).

### Aplicación/runtime

- `StructuredRequest`
- `RequestInterpreter`
- `TargetFactory`
- `Core`
- `Planner`
- `ExecutionPlan`
- `ExecutionTask`
- `Executor`
- `PluginManager`
- `RawObservation`
- `EvidenceManager`
- `ExecutionFailure`
- `RuntimeProgressReporter`

### Infraestructura/presentación

- plugins concretos y herramientas externas;
- stores/filesystem/JSON;
- Ollama/provider LLM;
- Docker/Compose;
- logging;
- HTTP/subprocess;
- CLI/Rich/Prompt Toolkit.

## 4. Frontera de entrada

```text
Lenguaje natural
  ↓
RequestInterpreter
  ├─ TargetFactory (determinista)
  └─ LLM #1 (clasificación de Intent)
  ↓
StructuredRequest
  ↓
Core crea Investigation
```

El Core no recibe directamente lenguaje natural y no utiliza el LLM para seleccionar herramientas.

## 5. Flujo funcional

```text
Investigation
  ↓
Planner → ExecutionPlan
  ↓
Executor recorre ExecutionTask
  ↓
PluginManager resuelve/invoca Plugin
  ↓
RawObservation
  ↓ persistencia RAW
Normalización específica
  ↓
EvidenceManager → Evidence
  ↓ persistencia Evidence
RuleEngine + Rules → Finding(s)
  ↓ persistencia Finding
ReportManager → Report
  ↓ persistencia Report
report.json + report.md
  ↓
LLM #2
  ↓
presentación efímera/no autoritativa
```

Los fallos de herramientas se representan mediante `ExecutionFailure` y permanecen fuera del Knowledge Pipeline.

## 6. Plugins y herramientas

Una herramienta se integra mediante el contrato de plugin correspondiente.

Responsabilidades principales:

```text
Plugin
  ↓
RawObservation
  ↓
Normalizador específico
  ↓
EvidenceManager
  ↓
Evidence
```

El plugin no debe introducir lógica de dominio en el Core ni en `RuleEngine`.

## 7. RuleEngine y Findings

`RuleEngine` es el productor autoritativo de `Findings`.

Una `Rule`:

- opera sobre `Evidence`;
- expresa una condición verificable;
- mantiene trazabilidad hacia las evidencias que soportan el hallazgo.

El LLM no produce `Findings`.

## 8. Reporting

`ReportManager` genera el `Report` a partir del conocimiento ya consolidado.

```text
report.json → representación autoritativa
report.md   → proyección determinista
```

LLM #2 se ejecuta después de la persistencia del informe.

## 9. Roles LLM

### LLM #1

- interpretación de entrada;
- clasificación de `Intent`;
- fail-closed si la salida no es válida.

### LLM #2

- asistencia posterior al `Report`;
- grounded sobre una proyección controlada;
- no autoritativo;
- efímero;
- fail-soft.

Los parámetros operacionales, sus valores por defecto y las diferencias entre ejecución nativa y Docker se documentan en [`CONFIGURATION.md`](CONFIGURATION.md).

## 10. Frontera de despliegue

La arquitectura de software no implica un contenedor por componente.

La modalidad Docker separa principalmente:

```text
centaurus-core
centaurus-ollama
```

`centaurus-core` ejecuta el framework y las herramientas integradas.

`centaurus-ollama` proporciona el servicio LLM local en una red interna sin necesidad de exponer el servicio al host.

## 11. Appliance

Fuera del dominio/Core existe una frontera operacional mínima:

```text
usuario centaurus
  ├─ centaurus          → runtime CENTAURUS
  └─ centaurus-poweroff → apagado controlado
```

Esta frontera no concede administración Docker genérica ni shell root al usuario operativo.

## 12. Distribución

OVA, Git + Docker Linux e imagen USB son formas distintas de materializar el mismo producto y no redefinen el modelo de dominio.

La interfaz lógica de red de la appliance utiliza `centaurus0` como nombre estable del uplink.

## 13. Evolución arquitectónica

La arquitectura debe revisarse cuando cambie:

- el dominio;
- una frontera de autoridad;
- un contrato público;
- el ownership de una responsabilidad.

Añadir una herramienta, una regla o una nueva modalidad de empaquetado no implica por sí mismo un cambio arquitectónico.

### Modularidad en la práctica

| Cambio | Componentes principales implicados | Contrato que debe preservarse |
| --- | --- | --- |
| Sustituir o añadir una herramienta | Plugin, dependencias, catálogo de capacidades y normalizador cuando corresponda | `RawObservation`, fuente y tiempo de recogida; `Evidence` normalizada compatible. |
| Añadir un criterio analítico | Catálogo de reglas y pruebas; motor si se necesita un operador nuevo | Identidad/versión explícitas de la regla, semántica de evaluación y evidencias de apoyo en cada `Finding`. |
| Añadir un formato de informe | Renderizado y persistencia del informe | Significado de `Report`, sin conclusiones analíticas adicionales desde la presentación. |
| Sustituir un backend de persistencia | Implementaciones de stores y conexión en el runtime | Interfaces de los stores, correlación del caso, conservación de artefactos y comportamiento ante fallos. |

La modularidad localiza el impacto del cambio; no significa que todo cambio quepa en un fichero o pueda aplicarse sin trabajo de integración. Consulta [`PLUGIN_SYSTEM.md`](PLUGIN_SYSTEM.md) para integrar herramientas y [`RULES_AND_RULE_ENGINE.md`](RULES_AND_RULE_ENGINE.md) para los criterios analíticos.

El catálogo de reglas actual reside en código. Cargarlo desde YAML, JSON, un registry o una base de datos es una posible evolución, no una opción de configuración implementada. Ese cambio requeriría un cargador y validación, preservando `Rule`/`Condition`, las versiones y el snapshot de la regla conservado en los hallazgos.

## 14. Documentación relacionada

- [`PROJECT.md`](PROJECT.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`STORAGE.md`](STORAGE.md)
- [`STANDARDS.md`](STANDARDS.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)
- [`CORE_RUNTIME.md`](CORE_RUNTIME.md)
- [`PLUGIN_SYSTEM.md`](PLUGIN_SYSTEM.md)
- [`LLM_ARCHITECTURE.md`](LLM_ARCHITECTURE.md)
