from dotenv import load_dotenv
load_dotenv()

from src.pipeline.hypothesis import InvestmentHypothesis
from src.core.orchestrator import CommitteeOrchestrator
from src.reports.generator import ReportGenerator


def run_committee(ticker: str, thesis: str, output_path: str):
    hypothesis = InvestmentHypothesis(ticker=ticker, thesis=thesis)

    print(f"Running investment committee for {hypothesis.ticker}...")
    print(f"Thesis: {hypothesis.thesis}\n")

    orch = CommitteeOrchestrator()
    result = orch.run_with_chair(hypothesis.thesis)

    if not result["success"]:
        print("Committee session failed.")
        return

    print("\nGenerating report...")
    gen = ReportGenerator()
    report = gen.generate_investment_memo(hypothesis.ticker, {
        "summary": result["recommendation"],
        "market_data": "",
        "fundamentals": "",
        "economic_context": "",
        "quant_analysis": "",
        "risk_assessment": "",
        "recommendation": "",
        "conviction": "",
        "reasoning": result["recommendation"],
    })

    gen.save(report, output_path)
    print(f"Report saved to {output_path}")
