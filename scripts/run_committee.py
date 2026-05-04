import argparse
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.pipeline.runner import run_committee


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Autonomous Investment Committee")
    parser.add_argument("--ticker", required=True, help="Stock ticker (e.g. AAPL, NVDA)")
    parser.add_argument("--hypothesis", required=True, help="Investment hypothesis to evaluate")
    parser.add_argument("--output", default=None, help="Output path for the report (default: data/reports/<ticker>_analysis.md)")
    args = parser.parse_args()

    output = args.output or f"data/reports/{args.ticker.lower()}_analysis.md"
    asyncio.run(run_committee(args.ticker, args.hypothesis, output))
