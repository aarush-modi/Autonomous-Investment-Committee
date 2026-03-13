# Autonomous Investment Committee

Multi-agent system that simulates a professional investment board. Specialized AI agents collaborate to ingest market data, analyze investments, and produce structured research reports with Buy/Sell/Hold recommendations.

## Architecture

The system uses the Anthropic Claude API to power specialized agents, each with their own tools and expertise:

- **Committee Chair** — Orchestrates all agents, synthesizes final recommendation
- **Market Data** — Fetches prices, volume, and indices from free APIs
- **Research Analyst** — SEC filings, fundamental analysis, RAG knowledge base search
- **Alternative Data** — Economic indicators, insider transactions
- **Quant Analyst** — Statistical analysis, correlations, regression
- **Risk Manager** — VaR, Sharpe ratio, max drawdown, Black-Scholes

## Project Structure

```
src/
├── core/
│   ├── agent.py          # BaseAgent with Anthropic SDK tool-use loop
│   ├── tool.py           # @tool decorator with auto schema generation
│   ├── message.py        # AgentMessage and AgentResult models
│   └── orchestrator.py   # CommitteeOrchestrator pipeline
├── data/
│   ├── models.py         # Pydantic models (Quote, OHLCV, FinancialStatements, Filing)
│   ├── cache.py          # SQLite-backed cache with TTL
│   └── providers/
│       ├── base.py       # Abstract interfaces for data providers
│       └── yahoo.py      # Yahoo Finance implementation via yfinance
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install anthropic pydantic yfinance
```

## Testing

```bash
source venv/bin/activate

# Test core framework (no API key needed)
python3 test_core.py

# Test data layer (no API key needed, uses free Yahoo Finance)
python3 test_data.py
```

## Tech Stack

- **LLM**: Anthropic Claude API
- **Data**: yfinance, FRED, SEC EDGAR
- **Models**: Pydantic
- **Cache**: SQLite
- **RAG**: ChromaDB + sentence-transformers (planned)
