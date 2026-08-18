import json

import httpx
import pytest

from centaurus.llm import OllamaIntentProvider, RequestInterpreter
from centaurus.llm.exceptions import LLMProviderError, LLMResponseError
from centaurus.request import (
    PUBLIC_EXPOSURE_ASSESSMENT,
    StructuredRequest,
    TargetFactory,
)


class FakeIntentProvider:
    def __init__(self, intent=PUBLIC_EXPOSURE_ASSESSMENT):
        self.intent = intent
        self.received = []

    def classify_intent(self, user_input):
        self.received.append(user_input)
        return self.intent


def test_structured_request_accepts_supported_domain_request():
    request = StructuredRequest(
        target="example.com",
        target_type="domain",
        intent=PUBLIC_EXPOSURE_ASSESSMENT,
    )

    assert request.target == "example.com"
    assert request.target_type == "DOMAIN"
    assert request.intent == PUBLIC_EXPOSURE_ASSESSMENT


def test_structured_request_rejects_unknown_intent():
    with pytest.raises(ValueError):
        StructuredRequest(
            target="example.com",
            target_type="DOMAIN",
            intent="invented_intent",
        )


def test_target_factory_detects_and_normalizes_domain():
    target = TargetFactory().create("Investiga la exposición de EXAMPLE.COM.")

    assert target.value == "example.com"
    assert target.type == "DOMAIN"


def test_target_factory_detects_ip():
    target = TargetFactory().create("Analiza 192.0.2.10")

    assert target.value == "192.0.2.10"
    assert target.type == "IP"


def test_target_factory_rejects_email_target_not_operational_in_this_release():
    with pytest.raises(ValueError, match="unable to detect a supported target"):
        TargetFactory().create("Investiga User@Example.COM")


def test_structured_request_rejects_email_target_not_operational_in_this_release():
    with pytest.raises(ValueError, match="unsupported target_type"):
        StructuredRequest(
            target="user@example.com",
            target_type="EMAIL",
            intent=PUBLIC_EXPOSURE_ASSESSMENT,
        )


def test_target_factory_rejects_ambiguous_multiple_targets():
    with pytest.raises(ValueError, match="multiple or ambiguous"):
        TargetFactory().create("Compara example.com y example.net")


def test_request_interpreter_combines_deterministic_target_and_llm_intent():
    provider = FakeIntentProvider()
    interpreter = RequestInterpreter(provider=provider)

    request = interpreter.interpret("Revisa la exposición pública de EXAMPLE.COM")

    assert request == StructuredRequest(
        target="example.com",
        target_type="DOMAIN",
        intent=PUBLIC_EXPOSURE_ASSESSMENT,
    )
    assert provider.received == ["Revisa la exposición pública de EXAMPLE.COM"]


def test_ollama_intent_provider_posts_interpretation_specific_payload():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = request.read()
        return httpx.Response(
            200,
            json={"response": json.dumps({"intent": PUBLIC_EXPOSURE_ASSESSMENT})},
        )

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OllamaIntentProvider(
        base_url="http://ollama",
        model="qwen3:4b-instruct",
        client=client,
    )

    assert provider.classify_intent("Investiga example.com") == PUBLIC_EXPOSURE_ASSESSMENT
    payload = json.loads(captured["body"])
    assert payload["model"] == "qwen3:4b-instruct"
    assert payload["stream"] is False
    assert payload["format"] == "json"
    assert payload["options"]["temperature"] == 0
    assert "public_exposure_assessment" in payload["system"]
    client.close()


def test_ollama_intent_provider_rejects_unsupported_intent():
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(
                200,
                json={"response": json.dumps({"intent": "tool_selection"})},
            )
        )
    )
    provider = OllamaIntentProvider(base_url="http://ollama", client=client)

    with pytest.raises(LLMResponseError):
        provider.classify_intent("Investiga example.com")
    client.close()


def test_ollama_intent_provider_rejects_invalid_json_response():
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(200, json={"response": "not-json"})
        )
    )
    provider = OllamaIntentProvider(base_url="http://ollama", client=client)

    with pytest.raises(LLMResponseError):
        provider.classify_intent("Investiga example.com")
    client.close()


def test_ollama_intent_provider_maps_http_errors():
    client = httpx.Client(
        transport=httpx.MockTransport(
            lambda request: httpx.Response(503, json={"error": "down"})
        )
    )
    provider = OllamaIntentProvider(base_url="http://ollama", client=client)

    with pytest.raises(LLMProviderError):
        provider.classify_intent("Investiga example.com")
    client.close()


def test_cli_to_core_input_flow_creates_completed_investigation():
    from centaurus.cli import CLI
    from centaurus.core import Core
    from centaurus.executor.execution import ExecutionPlan
    from centaurus.investigation import InvestigationStatus

    class FakePlanner:
        def plan(self, investigation):
            return ExecutionPlan(investigation_id=investigation.id)

    class FakeExecutor:
        def execute(self, plan):
            return {"status": "completed", "results": []}

    class FakeReportStore:
        def persist_report(self, investigation_id, report):
            return None

    class FakePresentationLLM:
        def generate(self, report):
            return "presentation"

    core = Core(
        report_store=FakeReportStore(),
        llm_manager=FakePresentationLLM(),
    )
    core._initialized = True
    core._planner = FakePlanner()
    core._executor = FakeExecutor()
    core._rules = ()

    interpreter = RequestInterpreter(provider=FakeIntentProvider())
    cli = CLI(core, request_interpreter=interpreter)

    investigation = cli.submit("Evalúa la exposición pública de Example.COM")

    assert investigation.target == "example.com"
    assert investigation.target_type == "DOMAIN"
    assert investigation.intent == PUBLIC_EXPOSURE_ASSESSMENT
    assert investigation.status is InvestigationStatus.COMPLETED
    assert investigation.report is not None
    assert core.last_llm_output == "presentation"
