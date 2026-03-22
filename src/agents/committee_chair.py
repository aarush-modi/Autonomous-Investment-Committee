from src.core.agent import BaseAgent
from src.core.tool import tool
from src.core.message import AgentMessage

from src.agents.market_data import MarketDataAgent
from src.agents.research_analyst import ResearchAnalystAgent
from src.agents.alternative_data import AlternativeDataAgent
from src.agents.quant_analyst import QuantAnalystAgent
from src.agents.risk_manager import RiskManagerAgent


SYSTEM_PROMPT = open("config/prompts/committee_chair_agent.md").read()

AGENTS = {
    "Market Data": MarketDataAgent,
    "Research Analyst": ResearchAnalystAgent,
    "Alternative Data": AlternativeDataAgent,
    "Quant Analyst": QuantAnalystAgent,
    "Risk Manager": RiskManagerAgent,
}


@tool("Delegates a query to a specialist agent. Agent names: Market Data, Research Analyst, Alternative Data, Quant Analyst, Risk Manager")
def delegate_to_agent(agent_name: str, query: str) -> str:
    if agent_name not in AGENTS:
        return f"Unknown agent: {agent_name}. Available: {', '.join(AGENTS.keys())}"

    agent = AGENTS[agent_name]()
    result = agent.run(AgentMessage(content=query, sender="Committee Chair"))
    return f"[{agent_name}]:\n{result.content}"


class CommitteeChairAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Committee Chair",
            system_prompt=SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            tools=[delegate_to_agent],
            max_tokens=4096,
            temperature=0,
        )
