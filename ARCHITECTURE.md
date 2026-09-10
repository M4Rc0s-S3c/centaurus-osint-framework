# Arquitectura de CENTAURUS

[Español](ARCHITECTURE.md) | [English](ARCHITECTURE.en.md)
[Inicio](README.md) · [Proyecto](PROJECT.md) · [Especificación](SPECIFICATION.md) · [Persistencia](STORAGE.md)

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

Perfil actual de LLM #2:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

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

## 14. Documentación relacionada

- [`PROJECT.md`](PROJECT.md)
- [`SPECIFICATION.md`](SPECIFICATION.md)
- [`STORAGE.md`](STORAGE.md)
- [`STANDARDS.md`](STANDARDS.md)
- [`DEVELOPMENT.md`](DEVELOPMENT.md)
