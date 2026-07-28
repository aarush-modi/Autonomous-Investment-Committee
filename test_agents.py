from src.core.message import AgentMessage
from src.agents.quant_analyst import QuantAnalystAgent
from src.agents.risk_manager import RiskManagerAgent
from src.agents.alternative_data import AlternativeDataAgent
from conftest import end_turn_response


class TestQuantAnalystAgent:
    async def test_returns_result(self, install_fake_anthropic):
        install_fake_anthropic([end_turn_response("AAPL and MSFT are moderately correlated at 0.55.")])
        agent = QuantAnalystAgent()

        result = await agent.run(AgentMessage(
            content="Calculate AAPL returns over the last 180 days and its correlation with MSFT",
            sender="user",
        ))

        assert result.success
        assert result.agent_name == "Quant Analyst"
        assert "correlated" in result.content


class TestRiskManagerAgent:
    async def test_returns_result(self, install_fake_anthropic):
        install_fake_anthropic([end_turn_response("NVDA has a Sharpe ratio of 2.1 and max drawdown of -28%.")])
        agent = RiskManagerAgent()

        result = await agent.run(AgentMessage(
            content="What's the risk profile for NVDA? Calculate VaR, Sharpe ratio, and max drawdown over the last year",
            sender="user",
        ))

        assert result.success
        assert result.agent_name == "Risk Manager"
        assert "Sharpe" in result.content


class TestAlternativeDataAgent:
    async def test_returns_result(self, install_fake_anthropic):
        install_fake_anthropic([end_turn_response("Inflation is 2.8% and unemployment is 4.1%.")])
        agent = AlternativeDataAgent()

        result = await agent.run(AgentMessage(
            content="What's the current inflation and unemployment rate? Also check insider transactions for AAPL",
            sender="user",
        ))

        assert result.success
        assert result.agent_name == "Alternative Data"
        assert "Inflation" in result.content
