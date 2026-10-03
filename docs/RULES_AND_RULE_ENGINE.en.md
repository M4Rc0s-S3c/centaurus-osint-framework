# Rules and Rule Engine

[Español](RULES_AND_RULE_ENGINE.md) | [English](RULES_AND_RULE_ENGINE.en.md)

[Home](../README.en.md) · [USER_GUIDE.en.md](USER_GUIDE.en.md) · [ARCHITECTURE.en.md](ARCHITECTURE.en.md)

## 1. Engine purpose

`RuleEngine` evaluates declarative rules against normalized `Evidence` and produces `Finding` objects. The authoritative flow is `Evidence -> Finding -> Report`; the LLM neither defines conditions nor decides which findings are persisted.

Findings describe observations from the queried sources. They do not, by themselves, establish a vulnerability, attribution, risk score or operational recommendation.

### What a deterministic result means

For the same normalized evidence, including collection times, the same rules and evaluation order, and the same implementation, the engine produces the same findings. The criteria can be inspected and evaluated again without asking an LLM to decide the conclusion.

This does not guarantee that a source is accurate or that two live investigations produce identical results: sources, coverage and observations can change. It also does not imply byte-identical reports across investigations, which have their own identifiers and generation times. `report.md` is a deterministic projection of a given `Report`.

### Controlled example: corroboration with RL-014

Suppose normalized Sublist3r evidence contains `api.example.com` and `www.example.com`, while crt.sh evidence contains `api.example.com` and `mail.example.com`. Evaluating `RL-014` alone produces one finding for `api.example.com`, observed in two distinct sources. It retains the rule and both supporting evidences.

The other names do not meet this corroboration criterion. That does not prove that they do not exist or are safe. The example uses controlled data, not live observations of `example.com`. It illustrates how explicit criteria turn observations into a conclusion whose support can be reviewed through [`STORAGE.en.md`](STORAGE.en.md#9-traceability).

## 2. Production catalog

The catalog contains eleven rules, ordered by numeric identifier.

| ID | Version | Observed condition |
| --- | --- | --- |
| `RL-001` | `1.1` | `registrar` is present with value `None`. |
| `RL-002` | `1.1` | `name_servers` is present with value `None`. |
| `RL-003` | `1.1` | `creation_date` or `expiration_date` is present with value `None`; each field is evaluated separately. |
| `RL-004` | `1.1` | `dnssec` equals `signedDelegation` or `unsigned`. |
| `RL-005` | `1.1` | `registrant_name` is present with value `None` or exactly `[REDACTED]`. |
| `RL-006` | `1.1` | Domain created less than 30 days before evidence collection. |
| `RL-007` | `1.0` | `spf_records` equals `[]`. |
| `RL-008` | `1.0` | More than one item in `subdomains`. |
| `RL-009` | `1.0` | More than one item in `emails`. |
| `RL-010` | `1.0` | `dmarc_records` equals `[]` in the direct query to the target domain's `_dmarc` name. |
| `RL-014` | `1.0` | The same subdomain observed in at least two distinct evidence sources. |

`RL-011`, `RL-012` and `RL-013` are not in the production catalog. The identifier sequence does not imply that fourteen rules are available.

Registration rules use normalized WHOIS/RDAP evidence; DNS rules use DNSRecon; public-exposure rules use normalized collections from the relevant sources. Tool availability does not guarantee that a query will produce every field or finding.

## 3. Evaluation semantics

- `missing` requires an existing key with value `None`. An absent key is not equivalent to an observation of absence.
- `redacted` recognizes the explicit marker; it does not infer redaction from any empty string.
- Conditions within a rule are evaluated individually. They are not implicitly joined with AND: `RL-003` can produce separate findings for both dates.
- Temporal conditions use `Evidence.collected_at`, not the computer's current date, preserving the observation's time reference.
- One rule can produce multiple findings for matching conditions and evidence. Finding count is not the number of evaluated rules.

`RL-014` aggregates collections and counts distinct `EvidenceSource` values. Repeated observations from one source do not increase the source count. It produces one finding per corroborated subdomain, with stable item ordering and references to the first supporting evidence from each distinct source.

## 4. Interpreting results

`RL-004` records a recognized DNSSEC state, including `signedDelegation`; it does not necessarily mean DNSSEC is absent.

`RL-010` describes the direct query to the target's `_dmarc` name. It does not establish that every potentially inherited policy is absent or represent a complete DMARC assessment.

An unobserved SPF policy, a recent registration or multiple public addresses also do not prove exploitation or malicious activity. Check each conclusion against its supporting evidence and the execution failures shown separately in the CLI and stored in `execution/failures/`. These failures are not part of `Report`; see [`STORAGE.en.md`](STORAGE.en.md).

No findings does not certify that a target is secure. It can reflect unmet conditions, unobserved data or limited source coverage.

## 5. Inspection and maintenance

In the Core CLI, `centaurus capabilities --rules` lists available rules without starting an investigation. To access Core through Compose, use [`DEPLOYMENT_GIT_DOCKER.en.md`](DEPLOYMENT_GIT_DOCKER.en.md). In the appliance shell, use the capability help described in [`USER_GUIDE.en.md`](USER_GUIDE.en.md); the host wrapper accepts zero arguments.

The catalog and its conditions are maintained in code. Semantic changes should explicitly manage identifiers and versions, include tests with normalized evidence and review their effect on reports. See [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md) and [`STANDARDS.en.md`](STANDARDS.en.md).

## 6. References

- [`rule_engine.py`](../src/centaurus/rules/rule_engine.py)
- [`catalog.py`](../src/centaurus/rules/catalog.py)
- [`registration_rules.py`](../src/centaurus/rules/registration_rules.py)
- [`dns_rules.py`](../src/centaurus/rules/dns_rules.py)
- [`exposure_rules.py`](../src/centaurus/rules/exposure_rules.py)
- [`STORAGE.en.md`](STORAGE.en.md)
