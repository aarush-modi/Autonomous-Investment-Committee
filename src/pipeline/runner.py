import re

from dotenv import load_dotenv
load_dotenv()

from src.pipeline.hypothesis import InvestmentHypothesis
from src.core.orchestrator import CommitteeOrchestrator
from src.reports.generator import ReportGenerator


def _parse_decision(text: str) -> dict:
    recommendation = "N/A"
    conviction = "N/A"
    reasoning = ""

    # Search for the last occurrence of Buy/Sell/Hold to get the Chair's final call
    rec_match = re.search(r"\*\*Recommendation\*\*[:\s]*(Buy|Sell|Hold)", text, re.IGNORECASE)
    if not rec_match:
        # findall returns all matches — take the last one (the final decision)
        all_recs = re.findall(r"\b(Buy|Sell|Hold)\b", text, re.IGNORECASE)
        if all_recs:
            recommendation = all_recs[-1].capitalize()
    else:
        recommendation = rec_match.group(1).capitalize()

    conv_match = re.search(r"\*\*Conviction[^:]*\*\*[:\s]*(High|Medium|Low)", text, re.IGNORECASE)
    if not conv_match:
        all_convs = re.findall(r"Conviction[:\s]*(High|Medium|Low)", text, re.IGNORECASE)
        if all_convs:
            conviction = all_convs[-1].capitalize()
    else:
        conviction = conv_match.group(1).capitalize()

    reason_match = re.search(r"\*\*Reasoning\*\*[:\s]*(.*?)(?:\n\n|\Z)", text, re.DOTALL | re.IGNORECASE)
    if not reason_match:
        reason_match = re.search(r"Reasoning[:\s]*(.*?)(?:\n\n|\Z)", text, re.DOTALL | re.IGNORECASE)
    if reason_match:
        reasoning = reason_match.group(1).strip()

    return {
        "recommendation": recommendation,
        "conviction": conviction,
        "reasoning": reasoning,
    }


async def run_committee(ticker: str, thesis: str, output_path: str):
    hypothesis = InvestmentHypothesis(ticker=ticker, thesis=thesis)

    print(f"Running investment committee for {hypothesis.ticker}...")
    print(f"Thesis: {hypothesis.thesis}\n")

    orch = CommitteeOrchestrator()
    result = await orch.run_with_chair(hypothesis.thesis)

    if not result["success"]:
        print("Committee session failed.")
        return

    print("\nGenerating report...")
    gen = ReportGenerator()
    agent_outputs = result.get("agent_outputs", {})
    decision = _parse_decision(result["recommendation"])

    # Use .html extension for output
    if output_path.endswith(".md"):
        output_path = output_path.rsplit(".md", 1)[0] + ".html"

    report = gen.generate_committee_decision(
        ticker=hypothesis.ticker,
        hypothesis=hypothesis.thesis,
        agent_outputs=agent_outputs,
        chair_synthesis=result["recommendation"],
        recommendation=decision["recommendation"],
        conviction=decision["conviction"],
        reasoning=decision["reasoning"],
    )

    gen.save(report, output_path)
    print(f"Report saved to {output_path}")
