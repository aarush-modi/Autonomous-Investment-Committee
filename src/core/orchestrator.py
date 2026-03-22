from src.core.agent import BaseAgent
from src.core.message import AgentMessage, AgentResult


class CommitteeOrchestrator:
    def __init__(self, config=None):
        self.config = config or {}
        self.agents = {}
        self.pipeline = []

    def register_agent(self, agent: BaseAgent):
        self.agents[agent.name] = agent

    def set_pipeline(self, agent_names: list[str]):
        self.pipeline = agent_names

    def run(self, query: str) -> dict:
        results = []
        context = {}
        for agent_name in self.pipeline:
            agent = self.agents[agent_name]
            message = AgentMessage(content=query, sender="orchestrator", context=context)
            result = agent.run(message)
            results.append(result)
            context[agent_name] = result.content
        return self._aggregate_results(results)

    def run_with_chair(self, hypothesis: str) -> dict:
        from src.agents.committee_chair import CommitteeChairAgent
        chair = CommitteeChairAgent()
        result = chair.run(AgentMessage(content=hypothesis, sender="user"))
        return {
            "recommendation": result.content,
            "success": result.success,
        }

    def _aggregate_results(self, results: list[AgentResult]) -> dict:
        return {
            "decisions": {r.agent_name: r.content for r in results},
            "success": all(r.success for r in results),
        }
