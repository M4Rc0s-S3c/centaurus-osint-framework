# Functional Specification

[Español](SPECIFICATION.md) | [English](SPECIFICATION.en.md)

[Home](README.en.md) · [Project](PROJECT.en.md) · [Architecture](ARCHITECTURE.en.md) · [Installation](INSTALL.en.md)

## 1. Purpose

This document defines the public functional behavior of CENTAURUS.

The current implementation uses deterministic planning and keeps the LLM outside tool selection/execution and authoritative finding generation.

## 2. Functional requirements

### FR-01 — Natural-language input

The analyst can start an investigation through the CLI using natural language.

### FR-02 — Structured interpretation

Input is transformed into `StructuredRequest`.

- `TargetFactory` deterministically detects and normalizes the `Target`.
- LLM #1 classifies only an allowed `Intent`.

### FR-03 — Investigation governance

The Core creates `Investigation` and governs its lifecycle.

### FR-04 — Deterministic planning

`Planner` builds `ExecutionPlan` and `ExecutionTask` from `Target`, `Intent` and available capabilities.

The LLM does not select tools.

### FR-05 — Modular execution

`Executor` and `PluginManager` execute plugins through explicit contracts.

### FR-06 — RAW preservation

Each valid execution may produce `RawObservation`, preserved for auditability and reproducibility.

### FR-07 — Normalization and Evidence

RAW output is transformed through tool-specific normalization into `Evidence` without adding analytical conclusions.

### FR-08 — Deterministic analysis

`RuleEngine` evaluates `Rules` and produces `Findings` traceable to their supporting evidence.

### FR-09 — Reporting

`ReportManager` builds and persists the report.

```text
report.json → authoritative
report.md   → deterministic projection
```

### FR-10 — Post-report LLM assistance

LLM #2 may provide synthesis/explanation assistance from the `Report`.

Its output:

- is grounded;
- is ephemeral;
- is non-authoritative;
- does not modify `Evidence`, `Findings` or `Report`;
- fails in fail-soft mode.

Current profile:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

### FR-11 — Partial tool failure

A tool failure does not necessarily invalidate the entire investigation when sufficient valid knowledge exists.

Errors are represented as `ExecutionFailure` and remain outside the Knowledge Pipeline.

### FR-12 — Offline discovery

The CLI provides:

```bash
centaurus capabilities
centaurus capabilities --rules
```

without requiring an investigation to start.

### FR-13 — Interactive progress

Ephemeral progress can be displayed in a TTY.

In non-interactive execution this surface may be suppressed without changing functional behavior.

### FR-14 — Traceable persistence

Artifacts are correlated through `investigation_id` and stored under `/workspace`.

### FR-15 — Appliance entry point

The standard user can start the runtime with:

```bash
centaurus
```

### FR-16 — Controlled shutdown

The appliance is cleanly shut down with:

```bash
centaurus-poweroff
```

### FR-17 — Reproducible distribution

The product can be consumed through:

- Git + Docker Linux;
- VMware OVA;
- bootable USB image.

### FR-18 — Network portability

The appliance uses `centaurus0` as the logical uplink name and avoids dependence on a specific VMware vNIC model.

## 3. Operational coverage

| Target | Coverage |
|---|---|
| DOMAIN | main/complete in the current version |
| IP | limited via RDAP |
| EMAIL | not operational as a direct Target |
| CERTIFICATE | deferred |

## 4. Integrated tools

The current version includes:

- WHOIS;
- RDAP;
- DNSRecon;
- Sublist3r;
- TheHarvester;
- crt.sh.

New tools are added through plugins.

## 5. Non-functional requirements

CENTAURUS should preserve:

- local framework and LLM execution;
- modularity;
- low coupling;
- reproducibility;
- traceability;
- persistence decoupled from the domain;
- least privilege;
- operation without mandatory commercial APIs;
- partial degradation on upstream failures;
- fail-soft degradation of LLM #2;
- automated contract tests;
- separation between product and distribution mode.

## 6. Exclusions

Not in current scope:

- active scanning;
- automated exploitation/pentesting;
- autonomous agents with LLM tool-calling;
- RAG/embeddings as a product requirement;
- mandatory GUI/Web/API;
- high availability or horizontal distribution;
- universal LLM performance guarantees;
- universal compatibility with all hardware.

## 7. Acceptance criteria

A functional investigation must preserve the chain:

```text
RAW
  ↓
Evidence
  ↓
Finding
  ↓
Report
```

with enough traceability to explain the origin of knowledge.

LLM #2 degradation does not invalidate an already built and persisted `Report`.

## 8. Related documentation

- [`PROJECT.en.md`](PROJECT.en.md)
- [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md)
- [`STORAGE.en.md`](STORAGE.en.md)
- [`INSTALL.en.md`](INSTALL.en.md)
