# Project Overview

[Español](PROJECT.md) | [English](PROJECT.en.md)

[Home](README.en.md) · [Architecture](ARCHITECTURE.en.md) · [Installation](INSTALL.en.md) · [Specification](SPECIFICATION.en.md)

## 1. Identity

**CENTAURUS OSINT Framework** is a modular, local-first OSINT framework for Blue Team, security analysis and IT environments.

Its goal is to provide a reproducible platform for passive public-exposure assessments while preserving traceability from sources to evidence, findings and reports.

Current public release: **[v1.0.0](https://github.com/M4Rc0s-S3c/centaurus-osint-framework/releases/tag/v1.0.0)**.

## 2. Purpose

CENTAURUS can:

- interpret an investigation request expressed in natural language;
- build a structured `Investigation`;
- deterministically select the capabilities that must run;
- execute OSINT tools through plugins;
- preserve original observations and normalized evidence;
- produce `Findings` through deterministic `Rules`;
- consolidate knowledge into a persistent `Report`;
- present results through CLI and bounded local LLM assistance.

## 3. Intended users

The project is primarily intended for:

- Blue Team environments;
- SME IT departments;
- security analysts;
- authorized defensive research and public-exposure assessments.

CENTAURUS is not a replacement for a SIEM, a pentesting platform or an active scanner.

## 4. Functional coverage

### DOMAIN

Main coverage through:

- WHOIS;
- RDAP;
- DNSRecon;
- Sublist3r;
- TheHarvester;
- crt.sh.

### IP

Limited coverage through RDAP.

### EMAIL and CERTIFICATE

Kept as evolution concepts. They are not currently part of complete operational coverage as direct investigation `Target` types.

## 5. Architecture

CENTAURUS explicitly separates:

- input interface and interpretation;
- Core orchestration;
- planning;
- execution;
- plugins/tools;
- normalization;
- persistence;
- `RuleEngine`;
- reporting;
- LLM assistance;
- Docker/Ollama infrastructure.

The **Core** owns the `Investigation` lifecycle.

`Planner` determines the capabilities to execute from `Target` and `Intent`. The language model does not select tools and does not generate `Findings`.

See [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md).

## 6. Artificial intelligence: two logical roles

CENTAURUS uses a local LLM service through Ollama with two different responsibilities.

### LLM #1 — interpretation

- participates in `RequestInterpreter`;
- classifies an allowed `Intent`;
- does not detect or normalize the `Target`;
- does not select tools;
- does not execute actions.

`Target` construction is deterministic.

### LLM #2 — analyst assistance

- runs only after a deterministic `Report` exists;
- works on a controlled report projection;
- generates synthesis/explanation support;
- is ephemeral;
- is non-authoritative;
- works in fail-soft mode.

An LLM #2 failure does not invalidate `Evidence`, `Findings` or `Report`.

## 7. Main technologies

| Area | Technology |
|---|---|
| Target OS | Debian GNU/Linux 13 |
| Framework | Python 3.12 |
| Containerization | Docker + Docker Compose |
| CLI | Typer + Rich + Prompt Toolkit |
| HTTP | httpx |
| Local LLM | Ollama |
| Model | `qwen3:4b` |
| Persistence | Filesystem + JSON |
| Logging | stdlib `logging` + `RotatingFileHandler` |
| Testing | pytest |

Current LLM #2 operational profile:

```text
timeout=300
num_ctx=8192
num_predict=UNSET
think=false
keep_alive=0
```

## 8. Distribution modes

### Git + Docker

Reproducible deployment from the public repository on a compatible Linux host.

See [`INSTALL.en.md`](INSTALL.en.md).

### VMware appliance

The prebuilt OVA is distributed through external storage:

**[CENTAURUS-C4-FINAL.ova — Google Drive](https://drive.google.com/drive/folders/1Anvan2lh-KQzQMDvvv_nTqSjfdSnTpdT?usp=sharing)**

```text
SIZE_BYTES=11828618752
SHA256=d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868
```

### Bootable USB image

The raw USB image has been validated and is pending external publication:

```text
File=CENTAURUS-USB.img
SIZE_BYTES=31457280000
SHA256=7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165
PUBLICATION_STATUS=PENDING
```

OVA/USB binaries are not stored directly in this Git repository. Verify artifact integrity using the published SHA-256.

## 9. Appliance credentials

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

Change default credentials after first access when the environment will remain deployed.

## 10. Appliance operation

The standard user starts CENTAURUS with:

```bash
centaurus
```

Controlled shutdown is performed outside the shell with:

```bash
centaurus-poweroff
```

The architecture avoids granting generic Docker administration to the operational user.

## 11. Responsible use

CENTAURUS is intended for legitimate OSINT, defensive security, research and authorized assessments.

Users are responsible for complying with applicable law, source terms and organizational policy.

## 12. Related documentation

- [`README.en.md`](README.en.md)
- [`INSTALL.en.md`](INSTALL.en.md)
- [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md)
- [`SPECIFICATION.en.md`](SPECIFICATION.en.md)
- [`STORAGE.en.md`](STORAGE.en.md)
- [`STANDARDS.en.md`](STANDARDS.en.md)
- [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)

## 13. License

CENTAURUS is distributed under the **Apache License 2.0**.

See [`LICENSE`](LICENSE) and [`NOTICE.md`](NOTICE.md).
