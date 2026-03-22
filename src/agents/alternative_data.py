from src.core.agent import BaseAgent
from src.tools.market.fred import get_economic_indicators, get_insider_transactions


SYSTEM_PROMPT = open("config/prompts/alt_data_agent.md").read()


class AlternativeDataAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Alternative Data",
            system_prompt=SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            tools=[get_economic_indicators, get_insider_transactions],
            max_tokens=1024,
            temperature=0,
        )
