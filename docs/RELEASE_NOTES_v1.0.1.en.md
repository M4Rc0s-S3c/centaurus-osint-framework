# CENTAURUS v1.0.1 — Documentation release

[Español](RELEASE_NOTES_v1.0.1.md) | [English](RELEASE_NOTES_v1.0.1.en.md)

[Home](../README.en.md) · [Project](PROJECT.en.md)

## Scope

This release consolidates public documentation and repository cleanup. Application source, tests, dependency locks, `pyproject.toml`, deployment scripts and Docker configuration are unchanged from `v1.0.0`. It adds no runtime features and makes no new hardware-validation claim.

## Changes

- Spanish and English guides organized by purpose, with consistent navigation and presentation.
- Expanded deployment, configuration, troubleshooting and backup instructions.
- Technical references for plugins, LLM architecture, Core runtime and testing.
- Clearer explanations of deterministic results, forward/reverse traceability, modularity and persisted report content.
- DHCP identified as the appliance default, with administrative static IPv4 instructions.
- Repository housekeeping, attribution clarification and removal of unused placeholders.

## Version identities

| Item | Identity |
| --- | --- |
| Repository release/tag | `v1.0.1`, documentation only |
| Python package | `0.4.0-dev`, normalized to `0.4.0.dev0` |
| Existing appliance artifacts | Previously distributed OVA/USB; unchanged |
| Core build bundle filename | `centaurus-core-build_v1.0.zip`; unchanged internal name |

`centaurus --version` reports the package version, not the repository release tag. Existing installations do not require a software upgrade for these documentation changes. The `v1.0.0` tag and academic delivery remain unchanged.

## OVA and USB downloads

Reuse the existing artifacts through [OVA deployment](DEPLOYMENT_OVA.en.md) and [USB deployment](DEPLOYMENT_USB.en.md). No replacement appliance is issued. Preserve their original identities:

| Artifact | Size in bytes | SHA-256 |
| --- | --- | --- |
| `CENTAURUS-C4-FINAL.ova` | `11828618752` | `d8ed4bbbce29d604be59464594a06c1c06b62a4a8840f7cb4140a086ce679868` |
| `CENTAURUS-USB.img` | `31457280000` | `7bb1f954d478b1bf405ee5b74d8a55370aedb5901355e151ca6cdaa918cd0165` |

GitHub's automatic Source code ZIP/TAR archives contain the repository at this tag, not the OVA or USB image. Linux bootstrap requires a Git checkout; the source ZIP is not a substitute for that checkout.

## Verification and limits

Runtime inputs were compared with `v1.0.0`. The deterministic Core build bundle is byte-identical, with SHA-256 `f580177c286afc71a2e3ab423d5ba5316d277112601af92e550d21ac92247463`. Relative links, anchors and ES/EN consistency were checked.

This does not constitute a new Docker build, full Python test-suite run, Windows installation, OVA import, USB boot, static-IP appliance test or GPU validation. Previous validation claims retain their original scope; GPU guidance remains experimental.
