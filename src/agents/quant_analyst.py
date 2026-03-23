from src.core.agent import BaseAgent
from src.tools.analysis.statistics import calculate_returns, calculate_correlations, run_regression


SYSTEM_PROMPT = open("config/prompts/quant_analyst_agent.md").read()


class QuantAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Quant Analyst",
            system_prompt=SYSTEM_PROMPT,
            model="claude-haiku-4-5-20251001",
            tools=[calculate_returns, calculate_correlations, run_regression],
            max_tokens=1024,
            temperature=0,
        )
