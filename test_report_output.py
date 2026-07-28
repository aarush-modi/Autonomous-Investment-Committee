import pytest

from src.reports.generator import ReportGenerator

AGENT_OUTPUTS = {
    "Market Data": """Ticker: NVDA
Price: $142.50
Volume: 312,000,000
Market Cap: $3,490,000,000,000
Day Change: +$3.20 (+2.30%)

Historical data shows NVDA up 180% over the past 12 months.
52-week range: $47.32 - $153.13""",

    "Research Analyst": """Recent 10-K filing (2024-11-01):
Revenue: $60.9B (up 126% YoY)
Data Center revenue: $47.5B (up 217% YoY)
Gross margin: 72.7% (up from 56.9%)
Operating income: $32.97B

Key findings:
- AI/data center is the dominant growth driver
- Gaming revenue relatively flat at $10.3B
- R&D spending increased 45% to $8.7B
- Strong balance sheet with $26B cash""",

    "Quant Analyst": """Returns for NVDA (last 365 days):
  Total Return: 180.25%
  Annualized Return: 180.25%
  Annualized Volatility: 58.30%

Correlation with S&P 500: 0.62 (moderate positive)

Regression vs S&P 500:
  Beta: 2.85
  Alpha (daily): 0.0045
  R-squared: 0.38""",

    "Risk Manager": """Value at Risk (95% confidence):
  Historical VaR: -4.82% daily
  Parametric VaR: -5.10% daily

Sharpe Ratio: 2.45 (Excellent)

Max Drawdown: -28.5%
  Peak: $153.13 (2025-01-06)
  Trough: $109.49 (2025-02-03)
  Recovery needed: 39.85%""",

    "Alternative Data": """Economic Indicators:
  Fed Funds Rate: 4.50% (holding steady)
  CPI (Inflation): 2.8% (trending down)
  GDP Growth: 2.3%
  Consumer Sentiment: 67.8

Insider Transactions for NVDA:
  2025-02-15 | Jensen Huang | Sale | 100,000 shares
  2025-01-20 | Colette Kress | Sale | 50,000 shares
  Note: Insider selling is part of pre-planned 10b5-1 trading plans""",
}

CHAIR_SYNTHESIS = """**Thesis**: NVIDIA is well-positioned as the dominant AI infrastructure provider, with explosive data center revenue growth validating the investment hypothesis.

**Evidence**:
- Revenue grew 126% YoY with data center up 217%, confirming AI demand thesis
- Gross margins expanded to 72.7%, demonstrating pricing power
- Stock up 180% in 12 months with a Sharpe ratio of 2.45 (excellent risk-adjusted returns)
- Macro environment supportive: inflation cooling, rates holding steady

**Risk Assessment**:
- Very high beta (2.85) means amplified downside in market selloffs
- Max drawdown of -28.5% shows significant volatility
- Daily VaR of -4.82% at 95% confidence — substantial daily risk
- Insider selling noted, though via pre-planned trading programs
- Concentration risk: heavy dependence on AI/data center cycle

**Recommendation**: Hold
- Conviction level: Medium
- Reasoning: While fundamentals are exceptional with 126% revenue growth and expanding margins, the stock has already appreciated 180% and trades at elevated multiples. The high beta (2.85) and significant max drawdown (-28.5%) suggest the risk/reward is more balanced at current levels. New positions should wait for a pullback to improve entry price."""


@pytest.fixture
def committee_decision_report():
    gen = ReportGenerator()
    return gen.generate_committee_decision(
        ticker="NVDA",
        hypothesis="Evaluate NVDA as a long position given AI infrastructure demand growth",
        agent_outputs=AGENT_OUTPUTS,
        chair_synthesis=CHAIR_SYNTHESIS,
        recommendation="Hold",
        conviction="Medium",
        reasoning=(
            "While fundamentals are exceptional with 126% revenue growth and expanding margins, "
            "the stock has already appreciated 180% and trades at elevated multiples. The high beta "
            "(2.85) and significant max drawdown (-28.5%) suggest the risk/reward is more balanced "
            "at current levels."
        ),
    )


class TestCommitteeDecisionReport:
    def test_includes_ticker_and_hypothesis(self, committee_decision_report):
        assert "NVDA" in committee_decision_report
        assert "AI infrastructure demand growth" in committee_decision_report

    def test_includes_every_agent_section(self, committee_decision_report):
        for agent_name in AGENT_OUTPUTS:
            assert agent_name in committee_decision_report

    def test_includes_recommendation_and_conviction(self, committee_decision_report):
        assert "Hold" in committee_decision_report
        assert "Medium" in committee_decision_report

    def test_saves_to_disk(self, committee_decision_report, tmp_path):
        gen = ReportGenerator()
        output_path = tmp_path / "reports" / "nvda_test_report.html"

        gen.save(committee_decision_report, str(output_path))

        assert output_path.exists()
        assert output_path.read_text() == committee_decision_report
