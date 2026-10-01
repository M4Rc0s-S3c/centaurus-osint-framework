# CENTAURUS · User Guide

[Español](USER_GUIDE.md) | [English](USER_GUIDE.en.md)

[Home](../README.en.md) · [Installation](INSTALL.en.md) · [Storage](STORAGE.en.md)

**Document version:** 1.0

**Audience:** users and analysts getting started with CENTAURUS.

**Scope:** operating the application, interpreting results and accessing reports. Installation is covered in the deployment documentation.

## 1. What you can do with CENTAURUS

CENTAURUS lets you investigate a domain's public exposure or query the information available for an IP address. It collects observations from different sources, normalizes the data and applies explicit rules to produce traceable conclusions.

The main result is a deterministic report. Language-model assistance can help you understand it, but the report's conclusions come from the framework's rules.

| Investigation target | Coverage in the documented version |
|---|---|
| Domain (`DOMAIN`) | Plan with 7 tasks across 6 tools |
| IP address (`IP`) | Limited lookup through RDAP |
| Email address (`EMAIL`) | Direct investigation unavailable |
| Certificate (`CERTIFICATE`) | Direct investigation deferred |

Certificate Transparency lookup is part of domain analysis. This does not mean that you can start a separate certificate investigation. Domain coverage does not amount to an exhaustive security audit either.

## 2. Identify where you are typing

The distribution distinguishes the system terminal from the application shell. The same `centaurus` name can refer to different entry points depending on the environment.

| Context | How to recognize it | What to enter |
|---|---|---|
| OVA/USB appliance Linux terminal | System prompt, before entering the application | `centaurus`, with no arguments |
| CENTAURUS shell | `centaurus>` prompt | Meta-commands such as `/help` or a natural-language request |
| Development or runtime environment with the package installed | Terminal prepared to use the package CLI | Commands such as `centaurus --help` or `centaurus capabilities` |

On the appliance, the first route is the normal entry point. Do not append `capabilities`, `shell` or `investigate` to the host command: that wrapper accepts zero arguments.

For Git + Docker on Linux, use the execution context specified by the deployment; do not assume that the host has the appliance wrapper. See [Installation and Deployment](INSTALL.en.md).

## 3. Your first appliance session

### 3.1 Sign in

Log in to Linux as the operational user `centaurus`. From that user's terminal, run:

```bash
centaurus
```

Enter the user's password when prompted. Access requires an interactive terminal and requests fresh authentication for every session.

When `centaurus>` appears, you are inside the application. The following examples show only what you should type, without the prompt.

### 3.2 View help and capabilities

```text
/help
```

To view target types, tools and the rule catalog:

```text
/capabilities --rules
```

You can also view each part separately:

| Input | Result |
|---|---|
| `/capabilities` | Distribution capabilities |
| `/rules` | Productive rule catalog |
| `/capabilities --rules` | Both views |
| `/help` | Shell help |
| `/exit` or `/quit` | End the session |

These queries display static information: they do not run tools or create an investigation. The verified catalog contains 11 rules. Being able to view capabilities does not prove that external sources or the LLM service are available.

### 3.3 Write your request

Write a clear request with a single target within the scope of your work. Example wording:

```text
Investigate the public exposure of example.com
```

`example.com` illustrates the format; replace it with the domain you are investigating. This example does not include real results or guarantee any particular number of findings.

The application interprets the request, validates the target and purpose, and passes the request to the Core. The framework determines the tool plan from its capabilities; it cannot be freely selected through instructions to the language model.

Each executed request opens a new investigation, even if you repeat the same domain. Repeating a request does not resume or update the previous case.

### 3.4 Wait for the result

An interactive terminal shows the current activity, elapsed time, task position in the plan, and tool or mode in use. Completion and degradation indicators help you follow progress.

There is no overall percentage or estimated time remaining. Duration depends on the sources queried and available resources. After collection tasks finish, result generation or presentation may continue; a visible pause alone does not prove that the application is stuck.

## 4. How to read the result

Start with the target and status, then review source failures and findings. Keep the investigation ID if you intend to access its artifacts or report an issue.

| Visible field | How to interpret it |
|---|---|
| `Investigation` | Case identifier |
| `Target` | Type and value of the target investigated |
| `Intent` | Supported purpose; the verified catalog uses `public_exposure_assessment` |
| `Status` | Status displayed for the execution |
| `Evidence` | Number of normalized evidence items |
| `Findings` | Number of conclusions produced by rules |
| `Rule` / `Conclusion` | Rule and conclusion for each finding |
| `Tool execution failures` | Failed sources or tasks and their diagnostics |
| `LLM analyst assistance — ephemeral` | Generative explanation, when available |

### Evidence, findings and reports

An **evidence item** represents normalized data obtained from a source. A **finding** represents what can be concluded by applying a rule to one or more evidence items. The **report** consolidates the case's findings.

For example, one source may observe a subdomain. If another source corroborates it and the corresponding rule's criteria are met, the framework can produce a corroboration conclusion. That conclusion does not by itself demonstrate that the subdomain is vulnerable.

The number of findings is not an overall risk score. A result with zero findings does not certify that the target has no exposure or problems either: it must be interpreted alongside the available coverage and evidence.

### Partial execution

`PARTIAL — completed with reduced tool coverage` indicates reduced coverage due to operational failures. If a valid report was produced, it remains useful within that coverage.

Review which source failed before drawing conclusions. A source failing to respond does not prove that the data you were looking for does not exist. An operational failure is recorded separately and does not become a finding.

### Failed investigation

If `FAILED` is displayed and the application indicates that no final report was produced, do not treat the case as completed. Observations, evidence or findings persisted before the failure may remain available; they support review and diagnostics but do not replace the missing final report.

## 5. Which results to keep and where to find them

| Artifact | Purpose |
|---|---|
| `report.json` | Authoritative structured representation of the report |
| `report.md` | Deterministic human-readable projection of the same report |
| Normalized evidence | Review the data supporting the analysis |
| RAW observations | Consult the preserved original responses |
| Execution failures | Explain missing coverage |
| LLM assistance text | Ephemeral reading aid; not part of the persisted report |

Report paths, relative to the configured workspace, are:

```text
investigations/<investigation-id>/reports/report.json
investigations/<investigation-id>/reports/report.md
```

In the container runtime, the usual location is `/workspace`. The host path backing that volume depends on the deployment: it should not be confused with a directory necessarily accessible to the appliance user.

This version's CLI does not provide a history browser or a command to open or export previous reports. To retrieve the files, use the workspace access provided by your installation or ask the environment administrator for a copy of the case directory. See the [storage model](STORAGE.en.md) for the other paths.

When handing over a result, include the report's identifier, target and relevant coverage limitations. Do not present a screenshot of the LLM explanation as a substitute for the report.

## 6. The role of LLM assistance

The model is involved at two different stages:

| Stage | Role | Effect of a failure |
|---|---|---|
| Request interpretation, LLM #1 | Help obtain a request with a supported purpose | May prevent the investigation from starting through the natural-language route |
| Subsequent assistance, LLM #2 | Explain the report already produced and persisted | The explanation may be unavailable while the deterministic report is preserved |

If you see `LLM analyst assistance unavailable; the deterministic Report remains the authoritative persisted result.`, consult the report. This message does not mean that you should automatically repeat the entire investigation.

The model's recommendations are advisory. To support a decision, return to the finding, rule and evidence. If the generative explanation disagrees with the report, the deterministic report takes precedence.

## 7. Common issues

| Situation | Check or next step |
|---|---|
| The host entry point rejects `centaurus capabilities` | On the appliance, run only `centaurus`; inside, use `/capabilities` |
| Appliance access fails before `centaurus>` appears | Review the message and report it to the environment administrator; services may require attention |
| `Invalid request` appears | Check the target and write a simple request using a supported target type |
| An LLM error appears during interpretation | Keep the message; ask for Ollama availability and configuration to be checked before retrying |
| A tool fails and the result is partial | Read the failure table and document the reduced coverage |
| No findings are produced | Review evidence and coverage; zero findings does not mean no risk |
| LLM assistance is unavailable after the report | Use the persisted report; the additional explanation may have failed |
| You cannot find a previous investigation from the shell | The CLI has no historical query feature; use the workspace access defined by the deployment |

When reporting an issue, include the deployment mode, the stage where it occurred, the exact message and the case identifier if one was generated. Include only the data needed for diagnosis.

## 8. End the session and shut down the appliance

To leave the application:

```text
/exit
```

`/quit` is also supported. You will return to the Linux terminal; leaving the application does not shut down the appliance or delete its persisted reports.

To shut down the documented OVA/USB appliance, run the following from the Linux terminal:

```bash
centaurus-poweroff
```

The command requires an interactive terminal, accepts zero arguments and requests the operational user's password again. There is no `/poweroff` command inside the CENTAURUS shell.

## 9. Package CLI reference

This section applies to an environment where the package is executed directly, such as development or the prepared container context. It does not apply to the appliance host wrapper.

```bash
centaurus --help
centaurus --version
centaurus capabilities
centaurus capabilities --rules
centaurus rules
centaurus shell
python -m centaurus --help
```

The `investigate` subcommand receives the natural-language request as an argument. View its help with `centaurus investigate --help` in that execution context.

| Exit code for a direct investigation | Meaning |
|---|---|
| `0` | Usable result; includes partial execution with a valid report |
| `1` | Internal error or invalid configuration |
| `2` | Invalid request |
| `3` | Operational failure preventing completion of a usable result |

Do not use these codes to infer the outcome of every request made within an interactive session: the shell lets you continue after a failed request, and normal shell exit returns `0`.
