from src.core.agent import BaseAgent
from src.tools.market.yahoo_finance import get_stock_price, get_historical_ohlcv, get_market_indices


SYSTEM_PROMPT = open("config/prompts/market_data_agent.md").read()


class MarketDataAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Market Data",
            system_prompt=SYSTEM_PROMPT,
            model="claude-sonnet-4-20250514",
            tools=[get_stock_price, get_historical_ohlcv, get_market_indices],
            max_tokens=1024,
            temperature=0,
        )
