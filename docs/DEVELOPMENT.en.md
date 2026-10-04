# Development Guide

[Español](DEVELOPMENT.md) | [English](DEVELOPMENT.en.md)

[Home](../README.en.md) · [Architecture](ARCHITECTURE.en.md) · [Standards](STANDARDS.en.md)

<details>
<summary>On this page</summary>

- [1. Workflow](#1-workflow)
- [2. Principles](#2-principles)
- [3. Dependencies and collaborations](#3-dependencies-and-collaborations)
- [4. Adding a plugin](#4-adding-a-plugin)
- [5. Adding a Rule](#5-adding-a-rule)
- [6. LLM](#6-llm)
- [7. Persistence](#7-persistence)
- [8. Development environment](#8-development-environment)
- [9. Tests](#9-tests)
- [10. Git review](#10-git-review)
- [11. Commit convention](#11-commit-convention)
- [12. What not to do](#12-what-not-to-do)
- [13. Contributions](#13-contributions)
- [14. Related documentation](#14-related-documentation)

</details>

## 1. Workflow

1. Need
2. Analysis
3. Design
4. Implementation
5. Tests
6. Review
7. Commit

A new component should not be added without a defined responsibility and contract.

## 2. Principles

- design before implementation;
- YAGNI / KISS / SRP;
- minimal public contracts;
- low coupling;
- high cohesion;
- tool-neutral Core;
- infrastructure-independent domain;
- operational configuration separated from analytical semantics;
- incremental evolution based on demonstrated need.

## 3. Dependencies and collaborations

A direct dependency between components is valid when it belongs to the architecture contract.

Examples:

| Component | Collaborates with |
| --- | --- |
| `Core` | `Planner`, `Executor`, `EvidenceManager`, `RuleEngine`, `ReportManager` |
| `Executor` | `PluginManager` |
| `PluginManager` | `BasePlugin` |

Not allowed:

- ad hoc lateral dependencies;
- bypassing public contracts to access concrete implementations;
- modifying `Investigation` outside the Core;
- accidental inversion of ownership.

## 4. Adding a plugin

A new tool must:

1. implement the `BasePlugin` contract;
2. produce `RawObservation` or a stable contractual failure;
3. provide a normalizer when required;
4. not directly create `Evidence`, `Finding` or `Report`;
5. not introduce tool-specific logic into Core or `RuleEngine`;
6. document the RAW → Evidence mapping;
7. include focused tests;
8. include integration/runtime validation when depending on an external tool.

Package structure, capability registration, normalization and the integration sequence are detailed in [`PLUGIN_SYSTEM.en.md`](PLUGIN_SYSTEM.en.md).

## 5. Adding a Rule

A new `Rule` should start from an objective domain question.

`RuleEngine` should only be extended when a real rule cannot be represented with existing capabilities.

## 6. LLM

LLM-related changes must preserve:

- LLM #1 / LLM #2 separation;
- deterministic `Target`;
- no LLM tool-calling;
- LLM #2 grounding;
- non-authoritative LLM #2 output;
- no persistence of analyst assistance;
- fail-soft behavior after `Report`.

Operational parameters should only change when there is a demonstrated need.

## 7. Persistence

- do not introduce physical paths into domain objects;
- persist RAW before normalization;
- keep `Evidence`, `Finding` and `Report` separate;
- keep `ExecutionFailure` outside the Knowledge Pipeline;
- do not overwrite historical knowledge.

See [`STORAGE.en.md`](STORAGE.en.md).

## 8. Development environment

The project requires Python 3.12 or later according to the versioned configuration.

Local example:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-core.lock
python -m pip install --no-deps -e .
python -m pip install pytest
python -m pip check
```

On Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-core.lock
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
.\.venv\Scripts\python.exe -m pip install pytest
.\.venv\Scripts\python.exe -m pip check
```

`pytest` is a development dependency and is not included in `requirements-core.lock` or the installed package dependencies. Install it only in the development environment. No test-dependency lock is provided; record `python -m pip freeze` with validation results when reproducibility is required.

## 9. Tests

Test levels, selection criteria and limits of simulated dependencies are explained in [`TESTING.en.md`](TESTING.en.md).

Run the suite:

```bash
python -m pytest
```

On Windows, keep using the virtual-environment interpreter without requiring activation:

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m compileall -q src tests
```

For Python changes on Linux, also check syntax:

```bash
python -m compileall -q src tests
```

Before committing:

```bash
git diff --check
```

Do not stage/commit while tests are failing.

## 10. Git review

Recommended flow (on Windows, replace `python` with `.\.venv\Scripts\python.exe`):

```bash
git status
git diff
git diff --check
python -m pytest

git add <paths>
git diff --cached
git status

git commit -m "<type>: <description>"
git push
```

After push:

```bash
git status
```

The working tree should be clean.

## 11. Commit convention

Use compact, descriptive commit messages.

Examples:

```text
feat: add new OSINT capability
fix: handle upstream timeout
test: add plugin integration coverage
docs: update deployment guide
refactor: simplify evidence mapping
```

## 12. What not to do

- add global business logic without defined responsibility;
- couple `RuleEngine` to tool-specific RAW;
- introduce free-form settings for analytical semantics;
- allow the LLM to select/execute tools;
- convert operational errors into knowledge;
- reopen architecture only for aesthetics;
- version workspaces, models, logs, secrets or generated artifacts.

## 13. Contributions

Before proposing a change:

1. keep scope limited;
2. preserve contractual compatibility;
3. add/update tests;
4. update affected public documentation;
5. review licenses of new dependencies;
6. comply with [`LICENSE`](../LICENSE) and [`NOTICE.md`](../NOTICE.md).

## 14. Related documentation

- [Architecture](ARCHITECTURE.en.md)
- [Standards](STANDARDS.en.md)
- [Specification](SPECIFICATION.en.md)
- [Installation](INSTALL.en.md)
