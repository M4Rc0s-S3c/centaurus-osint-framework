# Persistence and Traceability

[Español](STORAGE.md) | [English](STORAGE.en.md)

[Home](../README.en.md) · [Architecture](ARCHITECTURE.en.md) · [Specification](SPECIFICATION.en.md)

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

A configured `<workspace>` is used below. `/workspace` is the reference path in the appliance/container; see [`CONFIGURATION.en.md`](CONFIGURATION.en.md) for deployment-specific paths.

```text
<workspace>/
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

The authoritative JSON includes the following content:

| Content | Persisted fields |
| --- | --- |
| Case context | `investigation_id`, `generated_at`, `target`, `target_type`, `intent` |
| Original request | Optional `analyst_question`; recorded by the normal CLI flow |
| Findings | `finding_ref`, conclusion, complete rule snapshot and supporting evidence |
| Supporting evidence within each finding | `source`, `collected_at` and `data` |

The original request also appears in the Markdown report when present. The JSON rule snapshot includes its identity, version, descriptive fields, conditions and conclusion. Evidence supporting a finding is embedded in the report in addition to its separate persistence; evidence without a finding and original RAW are not thereby included in the report. Operational failures remain separate.

The full case directory is therefore the reference for retaining all persisted artifacts. Sharing only the reports still shares context, the original request when recorded and supporting evidence. Review those contents before delivery. The narrower projection sent to LLM #2, described in [`LLM_ARCHITECTURE.en.md`](LLM_ARCHITECTURE.en.md), does not remove data from the persisted files.

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

### Forward traceability: from observation to report

The plugin produces `RawObservation`; its structured output is persisted before normalization. `EvidenceManager` creates normalized `Evidence`, retaining `source` and `collected_at`. Rules evaluate that evidence, and each matching `Finding` retains its rule and supporting evidences. `Report` consolidates the findings within the investigation. Not every observation leads to a finding.

### Reverse traceability: reviewing a conclusion

1. Locate the case by `investigation_id` and open `reports/report.json`.
2. Select the finding by its report-local `finding_ref`. Review its conclusion, rule snapshot, version and conditions, and embedded supporting evidences.
3. Compare those evidences with `evidences/normalized/`, using `source`, `collected_at` and `data` within the same case.
4. Correlate them with observations in `evidences/raw/` using source, collection time and the content transformed by the corresponding normalizer. RAW and normalized content need not be identical.
5. Review `execution/failures/` separately to assess missing coverage. The report does not include those operational failures.

`Evidence` has no direct RAW identifier or file path. RAW and normalized stores allocate sequences independently; matching filename numbers is not a reliable relationship. Source and time alone are not guaranteed unique either: if the retained artifacts do not establish an unambiguous correspondence, record that limit rather than assuming a link.

This is an inspection path through persisted artifacts, not a built-in reverse-navigation command or a cryptographic chain of custody. Preserve the complete case directory and the code/rule version used when an audit must explain both the conclusions and their derivation.

## 10. Workspace in Git + Docker

Git + Docker mode uses a persistent host directory mounted at `/workspace`.

The exact location is documented in [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md).

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

## 13. Export, backup and recovery

These are administrative procedures. The appliance analyst does not need general Docker access or broader filesystem permissions. There is no CLI export or restore command; the administrator works with persisted files and an approved transfer destination.

### Export an investigation

1. Record the investigation ID and wait for its execution to finish. Ask the administrator to locate `<workspace>/investigations/<investigation-id>/` in the deployment workspace.
2. Copy the whole case directory to a separate destination to preserve evidence, findings, reports and operational failures together. For a report-only delivery, copy both `reports/report.json` and `reports/report.md`, explaining that the report includes supporting evidence but does not replace the complete case directory or include operational failures.
3. Compare the copied files with the source using SHA-256, retain the case ID and deployment identity, and review the contents before sharing. LLM assistance is not included in persisted reports.

### Back up the workspace

1. Finish active investigations, exit Core sessions and prevent new sessions during the copy. Verify the actual workspace mount; on OVA/USB the administrator can use `findmnt /workspace`.
2. Copy the complete workspace, including `investigations/` and any logs needed, to independent storage. Preserve directory layout, numeric ownership and permissions with a suitable backup tool. Keep the backup outside the live workspace and outside the same USB medium.
3. Record the appliance hash or source commit, the source path, backup time and file hashes. Check readability and available destination space. A workspace backup preserves results; it does not back up the operating system, Docker images or Ollama model.
4. For a full OVA recovery point, shut down the VM cleanly and copy its complete directory with all three virtual disks using the host's backup procedure. A snapshot on the same storage is not an independent backup. For USB, retain the original verified distribution image separately from the workspace backup.

### Recover and verify

1. Preserve the current workspace before making changes. Prepare a separate compatible instance using the identified distribution; keep it inactive during recovery.
2. Restore the workspace backup to that instance's data volume, preserving numeric ownership and permissions. Do not overlay cases with identical IDs or replace SYSTEM/PLATFORM content with workspace data.
3. Before normal use, verify the mount, compare restored file hashes against the backup and open selected `report.json` and `report.md` files. The administrator must also confirm that the normal runtime user can access the restored data.
4. Retain the original and backup until recovery is accepted. Existing files do not prove every investigation completed; check each case's reports and operational failures. No migration between incompatible storage formats is provided by this procedure.

This procedure is operational guidance; it does not claim a new OVA/USB recovery test. Validate the chosen backup tool and transfer method in your environment before relying on them.

## 14. Related documentation

- [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md)
- [`SPECIFICATION.en.md`](SPECIFICATION.en.md)
- [`INSTALL.en.md`](INSTALL.en.md)
