# Project Standards

[Español](STANDARDS.md) | [English](STANDARDS.en.md)

[Home](README.en.md) · [Architecture](ARCHITECTURE.en.md) · [Development](DEVELOPMENT.en.md)

## 1. Architecture

1. `Investigation` is the central domain unit.
2. The Core governs its lifecycle.
3. Components collaborate through explicit public contracts.
4. Core retains macroscopic orchestration without needing to physically mediate every authorized collaboration.
5. Each component keeps a clear responsibility.
6. The domain does not depend on filesystem, Docker, Ollama, CLI or concrete plugins.
7. Tools are integrated through plugins.
8. Tool-specific logic is not introduced into Core or `RuleEngine`.
9. Heavy resources are acquired/released on demand when appropriate.
10. Security is enforced at the boundaries where risk exists.

## 2. Domain

1. `Investigation` references `Target` and `Intent`.
2. `Rule` belongs to the domain.
3. `RuleEngine` produces `Findings`.
4. `Evidence` represents normalized facts.
5. `Finding` represents a deterministic conclusion.
6. `Report` consolidates knowledge.
7. A `Finding` must be explainable through its `Rule` and supporting `Evidence`.
8. `RawObservation`, `ExecutionPlan`, `ExecutionTask`, `ExecutionFailure` and LLM #2 output are not domain knowledge.

## 3. Knowledge Pipeline

1. RAW is persisted before normalization.
2. Normalization stabilizes representation; it does not interpret.
3. Acquisition failure is not transformed into evidence of absence.
4. `RuleEngine` works on `Evidence`.
5. `Finding` is persisted independently.
6. `Report` is built and persisted before LLM #2.
7. `ExecutionFailure` remains in a separate operational branch.

## 4. Plugins

A new tool must:

- implement the plugin contract;
- return `RawObservation` or a stable contractual failure;
- provide a normalizer when appropriate;
- not directly create `Evidence`, `Finding` or `Report`;
- not couple Core to tool-specific schemas;
- include suitable tests.

## 5. Rules

A new `Rule` must express an objective domain question.

`RuleEngine` is only extended when a real need cannot be represented with existing capabilities.

## 6. LLM

1. LLM #1 classifies `Intent`.
2. `Target` is built deterministically.
3. LLM #1 does not plan tools.
4. LLM #2 runs only after `Report`.
5. LLM #2 output is grounded, ephemeral and non-authoritative.
6. Structured output controls shape, not semantic truth.
7. An LLM #2 timeout/error does not invalidate the deterministic report.

Current LLM #2 profile:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

## 7. Persistence

1. `investigation_id` is the traceability axis.
2. Domain objects do not know physical paths.
3. RAW, Evidence, Finding and Report are materialized as distinct artifacts.
4. RAW is stored under `evidences/raw/`.
5. Normalized Evidence is stored under `evidences/normalized/`.
6. `ExecutionFailure` stays under `execution/failures/`.
7. Historical knowledge is not overwritten during normal operation.
8. LLM #2 output is not persisted.

## 8. Testing

1. Test observable behavior and contracts.
2. Prefer public APIs.
3. Keep tests focused by responsibility.
4. Internal refactors should not break tests that depend only on implementation details.
5. Do not commit with failing tests.
6. Anything depending on real runtime behavior requires real runtime validation.

## 9. Git

Before integration:

```bash
git diff --check
python -m pytest
```

Depending on scope, also review:

- focused suite;
- smoke tests;
- real runtime;
- staged changes;
- clean working tree.

## 10. Documentation

1. Public documentation must describe current behavior.
2. Technical literals are not translated or reinterpreted.
3. Paths, commands, flags, hashes and component names remain exact.
4. Documentation/implementation mismatches must be resolved explicitly.
5. Repository documentation must be useful to users and developers without relying on internal project material.

## 11. Security and responsible use

- do not introduce private credentials into the repository;
- do not log sensitive prompt/report content in telemetry;
- apply least privilege;
- separate administration and operation boundaries;
- use CENTAURUS only in legitimate and authorized contexts.

## 12. License

Contributions and redistributions must comply with [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
