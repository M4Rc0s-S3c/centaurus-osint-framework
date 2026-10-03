# Core and execution lifecycle

[Español](CORE_RUNTIME.md) | [English](CORE_RUNTIME.en.md)

[Home](../README.en.md) · [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md) · [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)

## 1. Authority and input

The Core coordinates components, governs the `Investigation` lifecycle and integrates knowledge. It delegates specialized work through explicit contracts; it does not interpret natural language or contain tool-specific logic.

The CLI uses `RequestInterpreter` to obtain a validated `StructuredRequest`. `Core.submit_request()` creates a new investigation with Target and Intent and runs its lifecycle. The original request may accompany it as `analyst_question`: report context, not an instruction for Planner or RuleEngine.

Every execution creates an independent identity. Repeating a target does not resume or overwrite a previous investigation.

## 2. Domain states and operational result

| `InvestigationStatus` state | Meaning |
| --- | --- |
| `CREATED` | Investigation created. |
| `PLANNED` | Planning entered; the plan is requested and validated. |
| `RUNNING` | Plan validated and execution started. |
| `COMPLETED` | Lifecycle completed; coverage may be reduced. |
| `FAILED` | The lifecycle could not complete. |

`partial` does not belong to that enum. It is an operational result of `Executor`, alongside `completed` and `failed`:

| Executor result | Aggregation condition | Core flow |
| --- | --- | --- |
| `completed` | No task failures. | Continues the pipeline; ends `COMPLETED` if subsequent phases finish. |
| `partial` | Valid observations and task failures coexist. | Keeps failures separate and processes observations; may end `COMPLETED`. |
| `failed` | Failures exist with no valid observations. | Persists failures, marks `FAILED` and does not construct a results report. |

Valid observations do not guarantee that subsequent normalization, rules or persistence will complete. Zero findings is not itself a failure either. CLI presentation and exit codes are explained in [`USER_GUIDE.en.md`](USER_GUIDE.en.md).

## 3. Planning and execution

`Planner` reads the capability catalog for the target type and constructs tasks. Intent has already been validated at the input boundary; the current catalog permits one functional purpose. There is no free LLM tool selection.

`ExecutionPlan` contains `investigation_id`, `tasks` and `metadata`. It is ephemeral; it contains no `objective` field or copies of Target and Intent. Before execution, the Core checks the plan type, investigation identity and that its tasks are `ExecutionTask` instances.

`Executor` processes tasks sequentially and delegates to `PluginManager`. Recoverable plugin failures are recorded and allow later tasks to continue. There is no autonomous replanning. The acquisition contract is documented in [`PLUGIN_SYSTEM.en.md`](PLUGIN_SYSTEM.en.md).

## 4. Pipeline order

| Order | Operation coordinated by the Core |
| --- | --- |
| 1 | Collect the Executor result and persist any `ExecutionFailure`. |
| 2 | If execution is not `failed`, persist valid RAW observations. |
| 3 | Create evidence through `EvidenceManager`, integrate and persist it. |
| 4 | Evaluate rules, integrate findings and persist them. |
| 5 | Construct the report through `ReportManager` and integrate it into the investigation. |
| 6 | Persist `report.json` and `report.md` through `ReportStore`. |
| 7 | Request assistance from `LLMManager` after persistence. |
| 8 | Complete the lifecycle as `COMPLETED`, including when assistance has a handled LLM error. |

The Core retains coordination of these collaborations. Tool-specific normalization belongs at the evidence boundary; `RuleEngine` works on normalized data and `ReportManager` consolidates findings. Execution failures do not enter this knowledge chain.

## 5. Failure-response matrix

| Boundary | Expected result |
| --- | --- |
| Configuration or request rejected before Core | No investigation starts through that flow. |
| Planner or invalid plan after lifecycle start | `FAILED`, error propagated and invalid plan not executed. |
| One task fails | `ExecutionFailure`; other tasks may continue. |
| All tasks in a nonempty plan fail | `FAILED`, persisted failures and no fabricated report. |
| Normalization, rules, report construction or persistence fails | `FAILED`; the exception propagates. Missing downstream knowledge is not fabricated. |
| LLM #2 provider produces a handled LLM error | Warning and no assistance; the persisted report is retained. |
| The progress surface managed by Core fails | Presentation degrades; it gains no authority over knowledge. |

Auxiliary LLM #2 handling catches exceptions under the `LLMError` contract. It does not imply universal recovery from unexpected exceptions, process termination or memory exhaustion. Content rejection rules are described in [`LLM_ARCHITECTURE.en.md`](LLM_ARCHITECTURE.en.md).

## 6. Persistence and recovery limits

There is no global transaction rolling back the entire investigation. A later failure can leave valid RAW, evidence or findings already persisted. These artifacts retain diagnostic and traceability value but do not prove that a final report exists.

An in-memory integrated `Report` must not be confused with completed persistence: integration precedes writing. Stores apply their own local guarantees; for example, `ReportStore` attempts to remove files it just created if writing the JSON/Markdown pair fails. That does not roll back other stores.

Paths, report contents and backup procedures are documented in [`STORAGE.en.md`](STORAGE.en.md).

## 7. Progress and resources

`RuntimeProgressReporter` is an optional, ephemeral surface. Executor communicates task events through a callback; it does not need to know Rich or govern `Investigation`. The Core protects progress publication and may degrade to a null reporter.

Plugins are instantiated per task. HTTP providers close clients they create; an injected client retains its external owner. The assistance model profile and requested release are described in [`LLM_ARCHITECTURE.en.md`](LLM_ARCHITECTURE.en.md). Task concurrency and a permanent Core service are not assumed.

## 8. Implementation references

- [`core.py`](../src/centaurus/core/core.py)
- [`investigation.py`](../src/centaurus/investigation/investigation.py)
- [`investigation_status.py`](../src/centaurus/investigation/investigation_status.py)
- [`planner.py`](../src/centaurus/planner/planner.py)
- [`executor.py`](../src/centaurus/executor/executor.py)
- [`report_store.py`](../src/centaurus/persistence/filesystem/report_store.py)
- [`TESTING.en.md`](TESTING.en.md)
