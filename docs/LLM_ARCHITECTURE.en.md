# LLM architecture

[Español](LLM_ARCHITECTURE.md) | [English](LLM_ARCHITECTURE.en.md)

[Home](../README.en.md) · [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md) · [`DEVELOPMENT.en.md`](DEVELOPMENT.en.md)

## 1. Two roles, deterministic authority

CENTAURUS uses Ollama for two separate logical roles. They may share a physical service and model, but have independent contracts and profiles. The LLM does not select tools, execute actions or produce authoritative findings.

| Role | Input | Accepted output | Effect of failure |
| --- | --- | --- | --- |
| LLM #1 | Natural-language request | An allowed `Intent` | May prevent an investigation from starting through that flow. |
| LLM #2 | Limited projection of the already persisted `Report` | Validated, ephemeral assistance | A handled LLM error leaves the deterministic report available. |

Operational values and deployment differences are documented in [`CONFIGURATION.en.md`](CONFIGURATION.en.md). Execution management belongs to [`CORE_RUNTIME.en.md`](CORE_RUNTIME.en.md).

## 2. Request interpretation

`RequestInterpreter` first constructs the Target deterministically through `TargetFactory`, then asks the provider to classify the Intent. Both are combined in `StructuredRequest`.

LLM #1 receives the user request. Its contract requires a JSON object with the single key `intent`, whose value must belong to the allowed catalog. Invalid responses are rejected; fields are not guessed and free text is not converted into a plan. The current Intent is `public_exposure_assessment`.

`StructuredRequest` validation checks target type, Intent and normalization. The operational catalog determines which targets can be investigated. The conceptual existence of EMAIL or CERTIFICATE does not make them operational targets.

## 3. What LLM #2 receives

`LLMManager` delegates to a provider that serializes the report using an explicit field allowlist. This projection differs from the persisted JSON.

| Included in the projection | Excluded as a projection field |
| --- | --- |
| `investigation_id` | `analyst_question`, `generated_at`, `target`, `target_type`, `intent` |
| Reference and conclusion of each finding | `Evidence.data` and RAW observations |
| Rule identifier, version, name, category and description | Complete rule conditions |
| `source` and `collected_at` of supporting evidence | Operational failures and logs |

Field exclusion is not anonymization: a conclusion may contain target-specific values. Nor does it remove those data from the persisted report. `report.json` retains rules, supporting evidence and context; the original request may appear in both reports. See [`STORAGE.en.md`](STORAGE.en.md).

## 4. Presentation contract

The structured response contains exactly `executive_summary`, `finding_summaries`, `risk_considerations` and `recommendations`.

References `F-001`, `F-002`, etc. are assigned according to finding order in the report. The executive summary must reference every finding; exactly one summary must exist per finding, with no unknown or duplicate references. Summaries are sorted deterministically before presentation.

Each advisory list allows at most five items. A report without findings cannot have risk considerations or recommendations. JSON structure controls response shape; it does not by itself establish content truth.

## 5. Validation and omissions

| Boundary | Behavior |
| --- | --- |
| Invalid JSON, fields, types or references | Response rejected through `LLMResponseError`. |
| Mandatory factual content that fails grounding | Presentation rejected; a partial factual summary is not accepted. |
| Structurally valid advisory item that fails semantic checks | Individual omission; accepted items may still be presented. |
| Advisory omissions | The renderer reports the number of omitted items without displaying or persisting their text. |

Individual omission applies after structural validation. It does not mean every malformed response can be recovered. Deterministic checks compare text with the allowed context and reject certain incompatible claims; they do not independently verify sources or guarantee every generated statement.

There is no automatic semantic repair or retry mechanism to obtain acceptable output. Assistance does not modify `Evidence`, `Finding` or `Report` and is not persisted as a report.

## 6. Profiles and resources

Interpretation and assistance profiles are separate immutable objects. Sampling parameters are versioned in [`inference_profile.py`](../src/centaurus/llm/inference_profile.py); they are not free analyst settings.

Runtime composition applies the specific timeout, context and optional generation limit to LLM #2. Their values remain in [`CONFIGURATION.en.md`](CONFIGURATION.en.md), without duplication here. They do not automatically apply to LLM #1.

The assistance provider requests `keep_alive=0` to release the model after generation. This request does not guarantee recovery from every memory shortage or prove that the server has finished work when the client times out. Compatibility and resource consumption require real-environment checks.

## 7. Errors and observability

Handled transport, HTTP and validation errors are represented through LLM exceptions. The Core records the incident after persisting the report and continues without assistance. This policy does not make every unexpected exception or process crash recoverable.

Provider telemetry uses duration, HTTP status, cause and counters when available. It does not dump the prompt, report projection or complete response. General logs may contain operational context and must be reviewed before sharing.

Trust boundaries are described in [`SECURITY_ARCHITECTURE.en.md`](SECURITY_ARCHITECTURE.en.md), and functional checks in [`TESTING.en.md`](TESTING.en.md).

## 8. Implementation references

- [`request_interpreter.py`](../src/centaurus/llm/request_interpreter.py)
- [`ollama_intent_provider.py`](../src/centaurus/llm/ollama_intent_provider.py)
- [`serialization.py`](../src/centaurus/llm/serialization.py): LLM #2 projection.
- [`presentation.py`](../src/centaurus/llm/presentation.py): schema, validation and renderer.
- [`ollama_provider.py`](../src/centaurus/llm/ollama_provider.py)
- [`llm_manager.py`](../src/centaurus/llm/llm_manager.py)
