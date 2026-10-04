# Testing strategy

[Español](TESTING.md) | [English](TESTING.en.md)

[Home](../README.en.md) · [Architecture](ARCHITECTURE.en.md) · [Development](DEVELOPMENT.en.md)

## 1. Purpose and preparation

Tests verify contracts and observable behavior. They should allow refactoring that preserves those contracts, avoiding unnecessary dependence on private details. A focused test should have a clear objective and an interpretable failure cause.

Environment preparation, `pytest` installation and commands for the suite, syntax and Git review remain in [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md). This document explains what to check and how to interpret results; it does not claim a recent run or a current passing-test count.

## 2. Levels and limits

| Level | What it demonstrates | What it does not demonstrate alone |
| --- | --- | --- |
| Unit / contractual | Types, invariants, validators, rules, serialization and component contracts. | Actual availability of a source, tool or model. |
| Integration | Collaboration between components and persistence in a controlled environment. | Equivalence across every operating system or deployment mode. |
| Reproducible complete flow | Passage through CLI, Core, adapted acquisition, knowledge, reports and presentation with controlled external boundaries. | A real investigation against external services when they are simulated. |
| Real runtime | Docker, tool, Ollama, permission, resource and platform behavior actually exercised. | Universal compatibility or performance on untested hardware. |

Test doubles should sit at boundaries the test does not intend to validate. Replacing HTTP or an external process enables repeatable scenarios without turning a local test into a claim about the real source. Tests in `tests/test_e2e.py` include replacements for these external dependencies.

## 3. Coverage by responsibility

| Area | Relevant checks | Suite references |
| --- | --- | --- |
| Input and capabilities | Deterministic Target, allowed Intent, catalog and rejection of invalid input. | [request input](../tests/test_request_input.py), [capabilities](../tests/test_capabilities.py) |
| Plugins and normalization | Parameters, representative RAW, acquisition errors and normalized representation. | [plugin manager](../tests/test_plugin_manager.py), [theharvester normalizer](../tests/test_theharvester_normalizer.py) |
| Rules | Match/no-match, types, explicit absence, time and cross-source corroboration. | [rule engine](../tests/test_rule_engine.py), [exposure rules](../tests/test_exposure_rules.py) |
| Core and execution | Sequence, plan validation, partial result, total failure and lifecycle authority. | [core](../tests/test_core.py), [executor](../tests/test_executor.py) |
| Persistence | Separate artifacts, traceability, overwrite rejection and write failures. | [persistence extended](../tests/test_persistence_extended.py), [raw observation store](../tests/test_raw_observation_store.py) |
| LLM | Schema, references, minimized projection, factual rejection and advisory omissions. | [llm](../tests/test_llm.py), [inference profile](../tests/test_inference_profile.py) |
| Presentation and observability | Markdown report, exit codes, progress and logging. | [report markdown](../tests/test_report_markdown.py), [cli app](../tests/test_cli_app.py), [runtime progress](../tests/test_runtime_progress.py) |
| Distribution and host controls | Script, configuration, supply-chain and wrapper contracts. | [linux distribution](../tests/test_linux_distribution.py), [ova runtime broker](../tests/test_ova_runtime_broker.py), [ova poweroff helper](../tests/test_ova_poweroff_helper.py) |

These are representative entry points, not an exhaustive list or a percentage-coverage claim.

## 4. Failure cases that must be distinguished

- A failed task produces `ExecutionFailure`, not fabricated empty evidence.
- A `partial` result may finish with `InvestigationStatus.COMPLETED` and a valid report.
- A structural failure after data acquisition marks the investigation as failed and preserves valid earlier artifacts; global rollback is not expected.
- Zero findings can be a valid result.
- A handled LLM #2 error leaves the already persisted report intact.
- Invalid structure or rejected mandatory factual content invalidates the LLM presentation; individual filtering applies to structurally validated advisory content.
- Progress failures must not change knowledge or exit codes.

Contracts are detailed in [`CORE_RUNTIME.en.md`](CORE_RUNTIME.en.md), [`LLM_ARCHITECTURE.en.md`](LLM_ARCHITECTURE.en.md) and [`STORAGE.en.md`](STORAGE.en.md).

## 5. Real-environment validation

For changes affecting deployment or external dependencies, record the actual environment and check relevant controls: image/model identity, permissions, mounts, networks, executables and persistence. A test inspecting Compose text does not demonstrate that Docker enforces that control at runtime.

OVA/USB acceptance requires import or writing, boot, entrypoint use, investigation and persistence across reboot on the target platform. USB includes real Ethernet networking. Operational procedures remain in their guides; running the Python suite does not establish new physical acceptance.

LLM functions require checks of output compatibility, small and large cases, duration and memory. A suite with a simulated provider does not measure Ollama consumption. GPU evaluation retains the experimental scope of [`GPU_OLLAMA_DOCKER.en.md`](GPU_OLLAMA_DOCKER.en.md).

## 6. Recording and interpreting results

For reviewable validation, retain the commit, environment, dependency versions, commands, results and limitations. Record failed, skipped and unexecuted tests separately; do not present a missing tool as a passing suite.

Select focused tests according to the change and follow integration checks in [`STANDARDS.en.md`](STANDARDS.en.md). Do not integrate with failing tests. When a check cannot be run, record the reason and the scope left unproven.

For documentation, check paths, anchors, ES/EN navigation, technical literals and diagram rendering when diagrams change. These checks do not replace functional validation when software also changes.

Counts and metrics from historical closures describe their commit and platform. They must not be published as results for the current version without an identified new run.

## 7. Related documentation

- [Development](DEVELOPMENT.en.md)
- [Standards](STANDARDS.en.md)
- [Plugin system](PLUGIN_SYSTEM.en.md)
- [Security](SECURITY_ARCHITECTURE.en.md)
