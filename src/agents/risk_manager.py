from src.core.agent import BaseAgent
from src.tools.analysis.risk_metrics import calculate_var, calculate_sharpe_ratio, calculate_max_drawdown


SYSTEM_PROMPT = open("config/prompts/risk_manager_agent.md").read()


class RiskManagerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Risk Manager",
            system_prompt=SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            tools=[calculate_var, calculate_sharpe_ratio, calculate_max_drawdown],
            max_tokens=1024,
            temperature=0,
        )
