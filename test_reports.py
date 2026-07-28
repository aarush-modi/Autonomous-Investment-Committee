import pytest

from src.reports.generator import ReportGenerator


@pytest.fixture
def gen():
    return ReportGenerator()


class TestInvestmentMemo:
    def test_generates_memo_with_ticker_and_recommendation(self, gen):
        memo = gen.generate_investment_memo("AAPL", {
            "summary": "Apple shows strong fundamentals with growing services revenue.",
            "market_data": "Price: $185.50, Volume: 50M, Market Cap: $2.8T",
            "fundamentals": "Revenue up 10% YoY, margins expanding.",
            "economic_context": "Fed holding rates steady, inflation cooling.",
            "quant_analysis": "Beta: 1.2, Sharpe: 1.8, annualized return: 25%",
            "risk_assessment": "VaR (95%): -2.1% daily, max drawdown: -15%",
            "recommendation": "Buy",
            "conviction": "High",
            "reasoning": "Strong fundamentals, favorable macro environment, manageable risk profile.",
        })

        assert "AAPL" in memo
        assert "Buy" in memo


class TestRiskReport:
    def test_generates_report_with_ticker_and_var(self, gen):
        risk = gen.generate_risk_report("NVDA", {
            "risk_metrics": "VaR (95%): -3.5% daily, Sharpe: 1.2",
            "drawdown": "Max drawdown: -25% from peak in March 2024",
            "correlation": "Beta vs S&P 500: 1.8, correlation: 0.72",
            "risk_summary": "Elevated volatility but compensated by strong returns.",
        })

        assert "NVDA" in risk
        assert "VaR" in risk


class TestCommitteeDecision:
    def test_generates_decision_with_agent_outputs(self, gen):
        decision = gen.generate_committee_decision(
            ticker="AAPL",
            hypothesis="Evaluate AAPL as a long position",
            agent_outputs={
                "Market Data": "Price: $185.50, up 1.2% today.",
                "Quant Analyst": "Annualized return: 25%, Sharpe: 1.8",
                "Risk Manager": "VaR: -2.1%, max drawdown: -15%",
            },
            chair_synthesis="Strong across all metrics with manageable risk.",
            recommendation="Buy",
            conviction="High",
            reasoning="Consistent growth, strong risk-adjusted returns.",
        )

        assert "AAPL" in decision
        assert "Market Data" in decision
        assert "Quant Analyst" in decision
        assert "3 contributing agents" in decision


class TestSave:
    def test_save_writes_file_and_creates_parent_dirs(self, gen, tmp_path):
        memo = gen.generate_investment_memo("AAPL", {
            "summary": "test", "market_data": "test", "fundamentals": "test",
            "economic_context": "test", "quant_analysis": "test", "risk_assessment": "test",
            "recommendation": "Buy", "conviction": "High", "reasoning": "test",
        })
        output_path = tmp_path / "reports" / "test_memo.md"

        gen.save(memo, str(output_path))

        assert output_path.exists()
        assert output_path.read_text() == memo
