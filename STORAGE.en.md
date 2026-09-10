# Persistence and Traceability

[Español](STORAGE.md) | [English](STORAGE.en.md)

[Home](README.en.md) · [Architecture](ARCHITECTURE.en.md) · [Specification](SPECIFICATION.en.md)

## 1. Principle

Persistence belongs to infrastructure and is coordinated by the Core.

Domain objects do not know about filesystem, JSON or physical paths.

`investigation_id` is the logical correlation axis for investigation artifacts.

## 2. Persisted artifacts

### Knowledge Pipeline

- `RawObservation` — original observation;
- `Evidence` — normalized fact;
- `Finding` — deterministic conclusion;
- `Report` — authoritative snapshot.

### Operational branch

- `ExecutionFailure` — execution failure.

LLM #2 output and interactive progress are not persisted as knowledge.

## 3. Stores

```text
Persistence Layer
├── RawObservationStore
├── EvidenceStore
├── FindingStore
├── ReportStore
└── ExecutionFailureStore
```

Stores persist already-produced artifacts. They do not normalize, apply `Rules` or govern the `Investigation` lifecycle.

## 4. Physical layout

```text
/workspace/
└── investigations/
    └── <investigation-id>/
        ├── evidences/
        │   ├── raw/
        │   └── normalized/
        ├── findings/
        ├── reports/
        └── execution/
            └── failures/
```

### RAW

RAW is materialized in:

```text
evidences/raw/
```

### Evidence

Normalized Evidence is materialized in:

```text
evidences/normalized/
```

### Findings

Findings are stored in:

```text
findings/
```

### Reports

Reports are stored in:

```text
reports/
```

### Operational failures

Failures are stored in:

```text
execution/failures/
```

## 5. RAW naming convention

Reference naming:

```text
<investigation-id>_<sequence>-<source>.json
```

The sequence belongs to the investigation.

RAW is cumulative and is not overwritten.

## 6. Report

`ReportStore` materializes the report as:

```text
report.json
report.md
```

- `report.json` is authoritative.
- `report.md` is a deterministic projection of the same report.

`Report` does not incorporate `ExecutionFailure` as knowledge.

## 7. ExecutionFailure

`ExecutionFailure`:

- is not `RawObservation`;
- is not `Evidence`;
- is not `Finding`;
- does not enter `RuleEngine`;
- does not alter the meaning of an already-built Report.

## 8. Immutability and accumulation

- RAW is not overwritten.
- Historical Evidence is not destructively replaced.
- Findings are cumulative.
- Report is a snapshot.
- Operational failures retain their evidence.

CENTAURUS does not apply one global rollback transaction across all stores of an investigation.

If a later phase fails, earlier valid persisted artifacts remain available.

```text
previously persisted artifacts → preserved
current phase                  → fails
downstream artifacts not made  → remain absent
```

Persisted does not necessarily mean completed investigation.

## 9. Traceability

```text
investigation_id
  ├─ evidences/raw/             → RawObservation
  ├─ evidences/normalized/      → Evidence
  ├─ findings/                  → Finding → Rule + Evidence(s)
  ├─ reports/                   → Report → Finding(s)
  └─ execution/failures/        → ExecutionFailure
```

Conceptual explanation chain:

```text
Report
  ↓
Finding
  ↓
Rule + Evidence
  ↓
source / collected_at
  ↓
correlatable original RAW
```

## 10. Workspace in Git + Docker

Git + Docker mode uses a persistent host directory mounted at `/workspace`.

The exact location is documented in [`INSTALL.en.md`](INSTALL.en.md).

Investigation data is not part of the Docker image or Git repository.

## 11. Data excluded from the repository

Do not version:

- investigations;
- generated evidence;
- real reports;
- runtime logs;
- Ollama models;
- secrets;
- local credentials;
- deployment `.env` files.

## 12. Technology

The implementation uses **Filesystem + JSON**.

Direct access to persisted artifacts is part of the operating model; a separate historical API is not mandatory.

## 13. Related documentation

- [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md)
- [`SPECIFICATION.en.md`](SPECIFICATION.en.md)
- [`INSTALL.en.md`](INSTALL.en.md)
