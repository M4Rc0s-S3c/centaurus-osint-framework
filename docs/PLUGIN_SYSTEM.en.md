# Plugin system

[Español](PLUGIN_SYSTEM.md) | [English](PLUGIN_SYSTEM.en.md)

[Home](../README.en.md) · [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md) · [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)

## 1. Scope and responsibilities

Plugins adapt OSINT tools and sources to the framework's acquisition contract. They do not plan investigations, create `Evidence`, apply rules or generate reports. Capability selection remains deterministic and the Core retains control of `Investigation`.

`Planner` creates tasks; `Executor` iterates over them; `PluginManager` loads and invokes the plugin; the plugin returns `RawObservation`. The tool catalog and coverage are described in [`SPECIFICATION.en.md`](SPECIFICATION.en.md).

## 2. Contract and package structure

The implementation must inherit from `BasePlugin` and expose a class named `Plugin` from its package. `PluginManager` checks for `__init__.py` and `plugin.py`, imports `centaurus.plugins.<plugin_id>` and validates the exported class.

| Element | Contract |
| --- | --- |
| `src/centaurus/plugins/<plugin_id>/__init__.py` | Exposes the `Plugin` class, normally by importing it from `plugin.py`. |
| `src/centaurus/plugins/<plugin_id>/plugin.py` | Implements `Plugin(BasePlugin)`. |
| `execute(parameters: dict) -> RawObservation` | Receives task parameters and returns one structured observation. |
| Plugin construction | The manager instantiates the class without arguments for each task execution. |

The manager checks that the output is a `RawObservation` instance. A list, report or `Evidence` is not an accepted substitute. The package structure allows loading, but **does not automatically add the plugin to the plan**.

## 3. Parameters and capability catalog

`ExecutionTask` carries `plugin_id` and `parameters`. The static capability catalog defines the templates used by Planner. Parameter names belong to each tool's contract; there is no universal `target` key.

Existing examples:

| Task | Parameters constructed by the catalog |
| --- | --- |
| WHOIS for a domain | `domain` |
| RDAP for a domain / IP | `domain` / `ip`, according to target type |
| DNSRecon for DMARC | `domain` and `mode="dmarc"` |

The CLI reads the same catalog to display capabilities. That query does not run plugins or demonstrate the availability of dependencies or external sources. Adding a tool requires explicitly updating applicable capabilities; LLM instructions do not discover a new plan.

## 4. RAW, normalization and persistence

`RawObservation` retains `source` (`EvidenceSource`), `data` and `collected_at`. It is an application object preceding domain knowledge. An empty observation must not be fabricated to hide acquisition failure.

The Core coordinates RAW persistence before evidence creation. `EvidenceManager` selects the normalizer by source and constructs `Evidence`, preserving provenance and collection time. A source without a registered normalizer is rejected. Normalizers stabilize representation and vocabulary; conclusions belong to `RuleEngine`.

For a new source, review `EvidenceSource` and normalizer selection in `EvidenceManager`. A new tool does not inherently require new rules: rules are justified by domain questions. See [`RULES_AND_RULE_ENGINE.en.md`](RULES_AND_RULE_ENGINE.en.md) and [`STORAGE.en.md`](STORAGE.en.md).

## 5. Errors and external dependencies

`PluginManager` preserves `PluginExecutionError` and wraps other exceptions while retaining their cause. `Executor` converts failures at this boundary into `ExecutionFailure` and continues with subsequent tasks. Categories are `timeout`, `unavailable`, `upstream_error`, `invalid_output` and `execution_error`.

The failure does not enter normalization or become evidence of absence. A later exception during normalization or persistence is a pipeline failure, handled as described in [`CORE_RUNTIME.en.md`](CORE_RUNTIME.en.md).

External-process tools are invoked with explicit arguments, without `shell=True`, with a timeout and output handling. Their auxiliary files do not replace official persistence. The Docker distribution separates incompatible DNSRecon, Sublist3r and TheHarvester dependencies into their own environments; dependency isolation is not a per-plugin sandbox. Installed plugins are part of the trusted computing base.

## 6. Integration sequence

1. Define the passive, authorized capability added by the source, its parameters and expected errors.
2. Implement the package contract and prepare representative RAW samples without unnecessary sensitive data.
3. Define the source and normalization; preserve original RAW and test missing data, types and real variations.
4. Integrate the required templates into the capability catalog and check their CLI representation.
5. Update the relevant runtime dependencies and locks when needed; avoid mixing incompatible environments.
6. Validate the plugin, normalizer, integration, persistence and complete flow according to [`TESTING.en.md`](TESTING.en.md). When an external tool is required, validate the real runtime too.
7. Update coverage and public documentation, keeping rules independent of tool output formats.

## 7. Implementation references

- [`base_plugin.py`](../src/centaurus/plugins/base_plugin.py): plugin interface.
- [`plugin_manager.py`](../src/centaurus/plugin_manager/plugin_manager.py): validation, loading and invocation.
- [`catalog.py`](../src/centaurus/capabilities/catalog.py): capabilities and task templates.
- [`raw_observation.py`](../src/centaurus/evidence/raw_observation.py): RAW contract.
- [`evidence_manager.py`](../src/centaurus/evidence/evidence_manager.py): normalization selection.
- [`execution_failure.py`](../src/centaurus/executor/execution/execution_failure.py): failure classification.
