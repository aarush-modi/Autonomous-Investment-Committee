from datetime import datetime

from src.agents.market_data import MarketDataAgent
from src.core.message import AgentMessage
from src.data.models import Quote
from conftest import end_turn_response, tool_use_response


class TestMarketDataAgent:
    async def test_answers_directly_without_tools(self, install_fake_anthropic):
        install_fake_anthropic([end_turn_response("AAPL is trading around $185.")])
        agent = MarketDataAgent()

        result = await agent.run(AgentMessage(content="What's AAPL trading at?", sender="user"))

        assert result.success
        assert result.agent_name == "Market Data"
        assert "AAPL" in result.content

    async def test_uses_get_stock_price_tool(self, install_fake_anthropic, monkeypatch):
        fake_quote = Quote(
            ticker="AAPL", price=185.50, volume=50_000_000, market_cap=2.8e12,
            day_change=1.25, day_change_percent=0.68, timestamp=datetime.now(),
        )
        monkeypatch.setattr(
            "src.tools.market.yahoo_finance.provider.get_quote",
            lambda ticker: fake_quote,
        )
        install_fake_anthropic([
            tool_use_response("get_stock_price", {"ticker": "AAPL"}),
            end_turn_response("AAPL is at $185.50."),
        ])
        agent = MarketDataAgent()

        result = await agent.run(AgentMessage(content="What's AAPL trading at?", sender="user"))

        assert result.success
        assert result.content == "AAPL is at $185.50."
