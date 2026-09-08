# CENTAURUS OSINT Framework

[Español](README.md) | [English](README.en.md)

CENTAURUS is a modular, local-first OSINT framework designed for Blue Team, security analysis and IT environments.

It provides a reproducible workflow for collecting public information, normalizing evidence, applying deterministic analysis rules and generating traceable investigation reports, while keeping operational decisions outside the language model.

## Key features

- Modular plugin architecture.
- Passive OSINT collection.
- Deterministic `Evidence -> Findings -> Report` pipeline.
- Local LLM integration through Ollama.
- Separation between authoritative deterministic reporting and non-authoritative LLM assistance.
- Persistent workspace for investigations, evidence, findings, reports and logs.
- Git + Docker deployment on Linux.
- VMware appliance distribution.
- Bootable USB image distribution.
- Local-first execution model.
- Apache License 2.0.

## Included OSINT capabilities

The current framework integrates six OSINT tools/capabilities:

- WHOIS lookup
- RDAP lookup
- DNSRecon
- Sublist3r
- TheHarvester
- crt.sh lookup

The architecture is designed so additional tools can be incorporated through the plugin model without redesigning the Core.

## Architecture at a glance

```text
Analyst
   |
   v
CLI / natural-language request
   |
   v
LLM #1 - Intent interpretation
   |
   v
TargetFactory
   |
   v
Planner
   |
   v
Core execution
   |
   +--> Plugins / OSINT sources
   |        |
   |        v
   |   Raw observations
   |        |
   |        v
   |   Normalization
   |        |
   v        v
EvidenceManager
   |
   v
Evidence
   |
   v
RuleEngine
   |
   v
Findings
   |
   v
Deterministic Report
   |
   +--> report.json   (authoritative)
   +--> report.md     (deterministic projection)
   |
   v
LLM #2 - Analyst assistance
          grounded, ephemeral,
          non-authoritative, fail-soft
```

The language model does not execute OSINT tools autonomously and does not generate authoritative findings. Operational execution and technical conclusions remain traceable through deterministic components.

## Quick start - Git + Docker

### Requirements

A Linux host with:

- Git
- Python 3
- Docker Engine
- Docker Compose
- Docker access for the deployment user

Clone the repository:

```bash
git clone https://github.com/M4Rc0s-S3c/centaurus-osint-framework.git
cd centaurus-osint-framework
```

For the current public release:

```bash
git checkout v1.0.0
```

Then follow the deployment procedure documented in [`INSTALL.md`](INSTALL.md).

The release bootstrap is provided through:

```bash
./scripts/bootstrap_linux_release.sh
```

> The exact prerequisites, environment preparation and validation steps are defined in `INSTALL.md`. Follow that document rather than treating this README as the complete deployment runbook.

## Appliance credentials

The distributed OVA/USB appliance uses the following default credentials:

### Standard user

```text
Username: centaurus
Password: centaurus
```

### Root

```text
Username: root
Password: root
```

Change the default credentials after first use when the environment will remain deployed.

## Distribution modes

CENTAURUS is designed around several distribution modes.

### Git + Docker

Recommended when the framework is deployed from source on a compatible Linux host.

The repository contains the Core, Docker/Compose definitions, dependency locks, initialization scripts and deployment documentation.

### VMware appliance

A prebuilt OVA can be used when a self-contained virtual appliance is preferred.

### Bootable USB image

A raw bootable image can be materialized onto suitable removable storage for portable execution.

> OVA and raw USB images are release artifacts and are not stored directly in this Git repository.

## Windows

Native Windows can be used for development, Core execution and local Ollama workflows.

Windows is not presented as equivalent to the complete Linux + Docker distribution for all integrated OSINT tools or for the hardened container runtime. See [`INSTALL.md`](INSTALL.md) and [`PROJECT.md`](PROJECT.md) for the documented scope.

## Local LLM

CENTAURUS uses Ollama for local language-model capabilities.

The current design separates two logical LLM roles:

- **LLM #1 - interpretation:** converts a natural-language request into a validated Intent.
- **LLM #2 - analyst assistance:** operates after the deterministic Report exists and is non-authoritative and fail-soft.

The deterministic report remains valid even if analyst assistance is unavailable or times out.

## Persistence

Runtime data is kept outside the application image in a persistent workspace.

Typical persisted data includes:

```text
workspace/
├── reports/
├── evidence/
├── logs/
├── cache/
└── tmp/
```

See [`STORAGE.md`](STORAGE.md) for the authoritative storage model.

## Tests

The repository includes the automated test suite under:

```text
tests/
```

In a prepared development/test environment:

```bash
python -m pytest
```

See [`DEVELOPMENT.md`](DEVELOPMENT.md) for development and validation guidance.

## Documentation

Recommended reading order:

1. [`PROJECT.md`](PROJECT.md) - project identity, scope and distribution modes.
2. [`INSTALL.md`](INSTALL.md) - deployment and installation.
3. [`ARCHITECTURE.md`](ARCHITECTURE.md) - framework architecture.
4. [`SPECIFICATION.md`](SPECIFICATION.md) - functional and non-functional specification.
5. [`STORAGE.md`](STORAGE.md) - persistence and traceability.
6. [`STANDARDS.md`](STANDARDS.md) - conventions and project standards.
7. [`DEVELOPMENT.md`](DEVELOPMENT.md) - development workflow.

## Release

Current public release:

**[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**

The academic TFM delivery was frozen separately and remains reproducible from the source-delivery commit documented in the submitted materials. Subsequent repository changes limited to public documentation and licensing do not alter that frozen academic snapshot.

## Responsible use

CENTAURUS is intended for legitimate OSINT, Blue Team, defensive-security, research and authorized assessment workflows.

Users are responsible for ensuring that their use of public sources, third-party tools and collected information complies with applicable law, source terms and organizational policy.

## License

CENTAURUS is licensed under the **Apache License, Version 2.0**.

See [`LICENSE`](LICENSE) for the full license text and [`NOTICE`](NOTICE) for attribution information.
