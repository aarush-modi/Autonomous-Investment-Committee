import pytest

from src.core.message import AgentMessage, AgentResult
from src.core.orchestrator import CommitteeOrchestrator
from src.agents import committee_chair
from src.agents.committee_chair import CommitteeChairAgent, delegate_to_agent
from conftest import end_turn_response


@pytest.fixture(autouse=True)
def clear_agent_outputs():
    # `committee_chair.agent_outputs` is a module-level dict shared across delegations
    # within a single committee run; reset it so tests don't leak state into each other.
    committee_chair.agent_outputs.clear()
    yield
    committee_chair.agent_outputs.clear()


class FakeSubAgent:
    def __init__(self, content="canned sub-agent output"):
        self._content = content

    async def run(self, message: AgentMessage) -> AgentResult:
        return AgentResult(agent_name="Market Data", content=self._content)


class TestDelegateToAgent:
    async def test_unknown_agent_returns_error_without_dispatching(self):
        result = await delegate_to_agent(agent_name="Nonexistent", query="anything")

        assert "Unknown agent" in result
        assert "Nonexistent" in result

    async def test_known_agent_dispatches_and_records_output(self, monkeypatch):
        monkeypatch.setitem(committee_chair.AGENTS, "Market Data", lambda: FakeSubAgent("AAPL is at $185"))

        result = await delegate_to_agent(agent_name="Market Data", query="What's AAPL trading at?")

        assert "[Market Data]" in result
        assert "AAPL is at $185" in result
        assert committee_chair.agent_outputs["Market Data"] == "AAPL is at $185"


class TestCommitteeChairAgent:
    async def test_answers_directly_without_delegation(self, install_fake_anthropic):
        install_fake_anthropic([end_turn_response("Recommendation: Hold AAPL.")])
        chair = CommitteeChairAgent()

        result = await chair.run(AgentMessage(content="Evaluate AAPL", sender="user"))

        assert result.success
        assert result.agent_name == "Committee Chair"
        assert "Hold" in result.content


class FakeChairAgent:
    def __init__(self, content="Hold AAPL — mixed signals.", outputs=None, success=True):
        self._content = content
        self._outputs = outputs or {"Market Data": "AAPL at $185"}
        self._success = success

    async def run(self, message: AgentMessage) -> AgentResult:
        return AgentResult(agent_name="Committee Chair", content=self._content, success=self._success)

    def get_agent_outputs(self) -> dict:
        return dict(self._outputs)


class TestCommitteeOrchestratorWithChair:
    async def test_wires_recommendation_and_agent_outputs(self, monkeypatch):
        monkeypatch.setattr(committee_chair, "CommitteeChairAgent", lambda: FakeChairAgent())
        orch = CommitteeOrchestrator()

        result = await orch.run_with_chair("Evaluate AAPL as a long position")

        assert result["success"] is True
        assert result["recommendation"] == "Hold AAPL — mixed signals."
        assert result["agent_outputs"] == {"Market Data": "AAPL at $185"}

    async def test_propagates_failure(self, monkeypatch):
        monkeypatch.setattr(
            committee_chair, "CommitteeChairAgent",
            lambda: FakeChairAgent(content="could not complete", success=False),
        )
        orch = CommitteeOrchestrator()

        result = await orch.run_with_chair("Evaluate AAPL")

        assert result["success"] is False


class FakePipelineAgent:
    def __init__(self, name, content):
        self.name = name
        self._content = content

    async def run(self, message: AgentMessage) -> AgentResult:
        return AgentResult(agent_name=self.name, content=self._content)


class TestCommitteeOrchestratorPipeline:
    async def test_runs_agents_in_order_and_aggregates(self):
        orch = CommitteeOrchestrator()
        orch.register_agent(FakePipelineAgent("Market Data", "price info"))
        orch.register_agent(FakePipelineAgent("Risk Manager", "risk info"))
        orch.set_pipeline(["Market Data", "Risk Manager"])

        result = await orch.run("Evaluate AAPL")

        assert result["success"] is True
        assert result["decisions"] == {"Market Data": "price info", "Risk Manager": "risk info"}
