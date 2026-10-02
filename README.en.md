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
- VMware appliance distribution.
- Bootable USB image distribution.
- Git + Docker deployment on Linux.
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

## Quick start — VMware OVA

The prebuilt OVA is the main CENTAURUS distribution. Follow [`DEPLOYMENT_OVA.en.md`](docs/DEPLOYMENT_OVA.en.md) to download and verify it, import it into VMware and open your first session.

For USB, Git + Docker on Linux or local Core on Windows, see [`INSTALL.en.md`](docs/INSTALL.en.md).

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

### VMware appliance

The OVA is the main distribution. Import and first-use procedure: [`DEPLOYMENT_OVA.en.md`](docs/DEPLOYMENT_OVA.en.md).

The prebuilt VMware appliance is available through external storage:

**[Access the CENTAURUS-C4-FINAL.ova download (Google Drive)](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)**

Published artifact identity:

```text
File: CENTAURUS-C4-FINAL.ova
SIZE_BYTES: 11828618752
SHA256: d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868
```

Always verify the SHA-256 after downloading the artifact.

### Bootable USB image

Writing and first-boot procedure: [`DEPLOYMENT_USB.en.md`](docs/DEPLOYMENT_USB.en.md).

The raw USB image is available through external storage:

**[Access the CENTAURUS-USB.img download](https://tinyurl.com/42wumj8b)**

Published artifact identity:

```text
File: CENTAURUS-USB.img
SIZE_BYTES: 31457280000
SHA256: 7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165
```

Always verify the SHA-256 after downloading the artifact.

> OVA and raw USB binaries are external artifacts and are not stored directly in this Git repository.

### Git + Docker

Recommended when the framework is deployed from source on a compatible Linux host.

The repository contains the Core, Docker/Compose definitions, dependency locks, initialization scripts and deployment documentation.

Procedure: [`DEPLOYMENT_GIT_DOCKER.en.md`](docs/DEPLOYMENT_GIT_DOCKER.en.md).

## Windows

Native Windows can be used for development, Core execution and local Ollama workflows.

Windows is not presented as equivalent to the complete Linux + Docker distribution for all integrated OSINT tools or for the hardened container runtime. See [`DEPLOYMENT_WINDOWS.en.md`](docs/DEPLOYMENT_WINDOWS.en.md) and [`PROJECT.en.md`](docs/PROJECT.en.md) for the documented scope.

## Local LLM

CENTAURUS uses Ollama for local language-model capabilities.

The current design separates two logical LLM roles:

- **LLM #1 - interpretation:** converts a natural-language request into a validated Intent.
- **LLM #2 - analyst assistance:** operates after the deterministic Report exists and is non-authoritative and fail-soft.

The deterministic report remains valid even if analyst assistance is unavailable or times out.

## Persistence

Runtime data is kept outside the application image in a persistent workspace.

Each investigation’s artifacts are stored in the persistent workspace, organized by investigation ID:

```text
workspace/
└── investigations/
    └── <investigation-id>/
        ├── evidences/
        │   ├── raw/
        │   └── normalized/
        ├── findings/
        ├── reports/
        │   ├── report.json
        │   └── report.md
        └── execution/
            └── failures/
```

See [`STORAGE.en.md`](docs/STORAGE.en.md) for the authoritative storage model.

## Tests

The repository includes the automated test suite under:

```text
tests/
```

In a prepared development/test environment:

```bash
python -m pytest
```

See [`DEVELOPMENT.en.md`](docs/DEVELOPMENT.en.md) for development and validation guidance.

## Documentation

Recommended reading order:

1. [`PROJECT.en.md`](docs/PROJECT.en.md) · [Español](docs/PROJECT.md) - project identity, scope and distribution modes.
2. [`INSTALL.en.md`](docs/INSTALL.en.md) · [Español](docs/INSTALL.md) - deployment and installation.
3. [`USER_GUIDE.en.md`](docs/USER_GUIDE.en.md) · [Español](docs/USER_GUIDE.md) - first session, result interpretation and troubleshooting.
4. [`ARCHITECTURE.en.md`](docs/ARCHITECTURE.en.md) · [Español](docs/ARCHITECTURE.md) - framework architecture.
5. [`SPECIFICATION.en.md`](docs/SPECIFICATION.en.md) · [Español](docs/SPECIFICATION.md) - functional and non-functional specification.
6. [`STORAGE.en.md`](docs/STORAGE.en.md) · [Español](docs/STORAGE.md) - persistence and traceability.
7. [`STANDARDS.en.md`](docs/STANDARDS.en.md) · [Español](docs/STANDARDS.md) - conventions and project standards.
8. [`DEVELOPMENT.en.md`](docs/DEVELOPMENT.en.md) · [Español](docs/DEVELOPMENT.md) - development workflow.
9. [`CONFIGURATION.en.md`](docs/CONFIGURATION.en.md) · [Español](docs/CONFIGURATION.md) - runtime variables, defaults and deployment differences.
10. [`RULES_AND_RULE_ENGINE.en.md`](docs/RULES_AND_RULE_ENGINE.en.md) · [Español](docs/RULES_AND_RULE_ENGINE.md) - rule catalog and finding interpretation.
11. [`DEPLOYMENT_OVA.en.md`](docs/DEPLOYMENT_OVA.en.md) · [Español](docs/DEPLOYMENT_OVA.md) - OVA import, operation and maintenance.
12. [`DEPLOYMENT_USB.en.md`](docs/DEPLOYMENT_USB.en.md) · [Español](docs/DEPLOYMENT_USB.md) - raw image writing, boot and persistence.
13. [`SECURITY_ARCHITECTURE.en.md`](docs/SECURITY_ARCHITECTURE.en.md) · [Español](docs/SECURITY_ARCHITECTURE.md) - trust boundaries, hardening and failure handling.
14. [`DEPLOYMENT_GIT_DOCKER.en.md`](docs/DEPLOYMENT_GIT_DOCKER.en.md) · [Español](docs/DEPLOYMENT_GIT_DOCKER.md) - deployment from source on Linux.
15. [`DEPLOYMENT_WINDOWS.en.md`](docs/DEPLOYMENT_WINDOWS.en.md) · [Español](docs/DEPLOYMENT_WINDOWS.md) - local Core setup on Windows.
16. [`TROUBLESHOOTING.en.md`](docs/TROUBLESHOOTING.en.md) · [Español](docs/TROUBLESHOOTING.md) - issue diagnosis across deployment modes.
17. [`GPU_OLLAMA_DOCKER.en.md`](docs/GPU_OLLAMA_DOCKER.en.md) · [Español](docs/GPU_OLLAMA_DOCKER.md) - optional experimental acceleration, without project GPU certification.

## Release

Current public release:

**[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**

The academic TFM delivery was frozen separately and remains reproducible from the source-delivery commit documented in the submitted materials. Subsequent repository changes limited to public documentation and licensing do not alter that frozen academic snapshot.

## Responsible use

CENTAURUS is intended for legitimate OSINT, Blue Team, defensive-security, research and authorized assessment workflows.

Users are responsible for ensuring that their use of public sources, third-party tools and collected information complies with applicable law, source terms and organizational policy.

## License

CENTAURUS is licensed under the **Apache License, Version 2.0**.

See [`LICENSE`](LICENSE) for the full license text and [`NOTICE.md`](NOTICE.md) for attribution information.
