# CENTAURUS Architecture

[Español](ARCHITECTURE.md) | [English](ARCHITECTURE.en.md)

[Home](README.en.md) · [Project](PROJECT.en.md) · [Specification](SPECIFICATION.en.md) · [Storage](STORAGE.en.md)

## 1. Purpose

CENTAURUS uses a modular architecture to separate OSINT acquisition, normalization, deterministic reasoning, persistence, reporting and local language-model assistance.

The architecture is designed so that new tools can be added without redesigning the Core or the domain model.

## 2. Structural principles

- `Investigation` organizes the domain.
- The **Core** owns the `Investigation` lifecycle.
- Components collaborate through explicit public contracts.
- `Executor` delegates execution to `PluginManager`.
- Plugins do not directly produce `Evidence`, `Finding` or `Report`.
- The domain does not depend on Docker, Ollama, filesystem or concrete tools.
- Authoritative analytical decisions are deterministic.
- Heavy resources can be acquired/released on demand.
- Security boundaries preserve authority and least privilege.

## 3. Layers and concepts

```text
Analyst
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

Domain:
Investigation · Target · Intent · Rule · Evidence · Finding · Report
```

### Domain

- `Investigation`
- `Target`
- `Intent`
- `Rule`
- `Evidence`
- `Finding`
- `Report`

### Application/runtime

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

### Infrastructure/presentation

- concrete plugins and external tools;
- stores/filesystem/JSON;
- Ollama/LLM provider;
- Docker/Compose;
- logging;
- HTTP/subprocess;
- CLI/Rich/Prompt Toolkit.

## 4. Input boundary

```text
Natural language
  ↓
RequestInterpreter
  ├─ TargetFactory (deterministic)
  └─ LLM #1 (Intent classification)
  ↓
StructuredRequest
  ↓
Core creates Investigation
```

The Core does not receive natural language directly and does not use the LLM to select tools.

## 5. Functional flow

```text
Investigation
  ↓
Planner → ExecutionPlan
  ↓
Executor iterates over ExecutionTask
  ↓
PluginManager resolves/invokes Plugin
  ↓
RawObservation
  ↓ persist RAW
Tool-specific normalization
  ↓
EvidenceManager → Evidence
  ↓ persist Evidence
RuleEngine + Rules → Finding(s)
  ↓ persist Finding
ReportManager → Report
  ↓ persist Report
report.json + report.md
  ↓
LLM #2
  ↓
ephemeral/non-authoritative presentation
```

Tool failures are represented through `ExecutionFailure` and remain outside the Knowledge Pipeline.

## 6. Plugins and tools

A tool is integrated through the corresponding plugin contract.

Main responsibilities:

```text
Plugin
  ↓
RawObservation
  ↓
Tool-specific normalizer
  ↓
EvidenceManager
  ↓
Evidence
```

A plugin must not introduce domain logic into the Core or `RuleEngine`.

## 7. RuleEngine and Findings

`RuleEngine` is the authoritative producer of `Findings`.

A `Rule`:

- operates on `Evidence`;
- expresses a verifiable condition;
- preserves traceability to the evidence supporting the finding.

The LLM does not produce `Findings`.

## 8. Reporting

`ReportManager` generates the `Report` from already consolidated knowledge.

```text
report.json → authoritative representation
report.md   → deterministic projection
```

LLM #2 runs after report persistence.

## 9. LLM roles

### LLM #1

- input interpretation;
- `Intent` classification;
- fail-closed when output is invalid.

### LLM #2

- assistance after `Report`;
- grounded on a controlled projection;
- non-authoritative;
- ephemeral;
- fail-soft.

Current LLM #2 profile:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

## 10. Deployment boundary

The software architecture does not imply one container per component.

The Docker mode primarily separates:

```text
centaurus-core
centaurus-ollama
```

`centaurus-core` runs the framework and integrated tools.

`centaurus-ollama` provides the local LLM service on an internal network without requiring exposure to the host.

## 11. Appliance

Outside the domain/Core, the appliance exposes a minimal operational boundary:

```text
centaurus user
  ├─ centaurus          → CENTAURUS runtime
  └─ centaurus-poweroff → controlled shutdown
```

This boundary does not grant generic Docker administration or a root shell to the operational user.

## 12. Distribution

OVA, Git + Docker Linux and USB image are different ways to materialize the same product and do not redefine the domain model.

The appliance uses `centaurus0` as the stable logical network uplink name.

## 13. Architectural evolution

The architecture should be revisited when any of the following changes:

- the domain;
- an authority boundary;
- a public contract;
- responsibility ownership.

Adding a tool, a rule or a packaging mode does not by itself imply an architectural change.

## 14. Related documentation

- [`PROJECT.en.md`](PROJECT.en.md)
- [`SPECIFICATION.en.md`](SPECIFICATION.en.md)
- [`STORAGE.en.md`](STORAGE.en.md)
- [`STANDARDS.en.md`](STANDARDS.en.md)
- [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)
