import json

import httpx
import pytest

from centaurus.core.core import Core
from centaurus.investigation import Investigation
from centaurus.llm import LLMManager, OllamaProvider
from centaurus.llm.serialization import serialize_report
from centaurus.llm.exceptions import LLMProviderError, LLMResponseError
from centaurus.report import Report


class FakeProvider:
    def __init__(self, response="Generated presentation"):
        self.response = response
        self.received = []

    def generate(self, report):
        self.received.append(report)
        return self.response


def make_report():
    return Report(investigation_id="inv-1", findings=())


def test_llm_manager_accepts_report_and_returns_provider_text():
    provider = FakeProvider()
    manager = LLMManager(provider=provider)
    report = make_report()

    assert manager.generate(report) == "Generated presentation"
    assert provider.received == [report]


def test_report_serialization_is_structured_and_non_mutating():
    report = make_report()
    serialized = serialize_report(report)

    payload = json.loads(serialized)
    assert payload == {"investigation_id": "inv-1", "findings": []}
    assert report.findings == ()


def test_llm_manager_rejects_non_report():
    manager = LLMManager(provider=FakeProvider())
    with pytest.raises(TypeError):
        manager.generate("report")  # type: ignore[arg-type]


def test_ollama_provider_posts_expected_payload():
    captured = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["json"] = request.read()
        return httpx.Response(200, json={"response": "Clear presentation"})

    client = httpx.Client(transport=httpx.MockTransport(handler))
    provider = OllamaProvider(
        base_url="http://ollama",
        model="qwen3:4b-instruct",
        client=client,
    )

    assert provider.generate(make_report()) == "Clear presentation"
    payload = json.loads(captured["json"])
    assert payload["model"] == "qwen3:4b-instruct"
    assert payload["stream"] is False
    assert payload["system"]
    assert json.loads(payload["prompt"])["investigation_id"] == "inv-1"
    client.close()


def test_ollama_provider_rejects_empty_response():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"response": " "}))
    )
    provider = OllamaProvider(base_url="http://ollama", client=client)
    with pytest.raises(LLMResponseError):
        provider.generate(make_report())
    client.close()


def test_ollama_provider_maps_http_errors():
    client = httpx.Client(
        transport=httpx.MockTransport(lambda request: httpx.Response(503, json={"error": "down"}))
    )
    provider = OllamaProvider(base_url="http://ollama", client=client)
    with pytest.raises(LLMProviderError):
        provider.generate(make_report())
    client.close()


def test_core_integrates_report_with_llm_manager():
    from centaurus.executor.execution import ExecutionPlan

    class FakePlanner:
        def plan(self, investigation):
            return ExecutionPlan(investigation_id=investigation.id)

    class FakeExecutor:
        def execute(self, plan):
            return {"status": "completed", "results": []}

    provider = FakeProvider("linguistic report")
    core = Core(llm_manager=LLMManager(provider=provider))
    core._initialized = True
    core._planner = FakePlanner()
    core._executor = FakeExecutor()
    core._rules = ()

    investigation = Investigation(objective="example.com")
    result = core.run_investigation(investigation)

    assert result == {"status": "completed", "results": []}
    assert provider.received == [investigation.report]
    assert core.last_llm_output == "linguistic report"


def test_core_keeps_completed_domain_state_when_llm_provider_fails():
    from centaurus.executor.execution import ExecutionPlan
    from centaurus.llm.exceptions import LLMProviderError

    class FakePlanner:
        def plan(self, investigation):
            return ExecutionPlan(investigation_id=investigation.id)

    class FakeExecutor:
        def execute(self, plan):
            return {"status": "completed", "results": []}

    class FailingProvider:
        def generate(self, report):
            raise LLMProviderError("Ollama unavailable")

    core = Core(llm_manager=LLMManager(provider=FailingProvider()))
    core._initialized = True
    core._planner = FakePlanner()
    core._executor = FakeExecutor()
    core._rules = ()

    investigation = Investigation(objective="example.com")
    core.run_investigation(investigation)

    assert investigation.report is not None
    assert core.last_llm_output is None
