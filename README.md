# Autonomous Investment Committee

Multi-agent system that simulates a professional investment board. Specialized AI agents collaborate to ingest market data, analyze investments, and produce structured research reports with Buy/Sell/Hold recommendations.

## Usage

```bash
source venv/bin/activate
python3 scripts/run_committee.py --ticker NVDA --hypothesis "Evaluate NVDA as a long position given AI infrastructure demand growth"
```

Output is saved to `data/reports/<ticker>_analysis.html`.

## Architecture

The system uses the Anthropic Claude API to power specialized agents, each with their own tools and expertise. The Committee Chair dynamically decides which agents to consult based on the hypothesis — no hard-coded pipeline.

- **Committee Chair** (Sonnet) — Orchestrates all agents, synthesizes final recommendation
- **Market Data** (Haiku) — Fetches prices, volume, and indices via Yahoo Finance
- **Research Analyst** (Haiku) — SEC filings, financial statements, RAG knowledge base search
- **Alternative Data** (Haiku) — Economic indicators (FRED), insider transactions
- **Quant Analyst** (Haiku) — Returns, correlations, regression analysis
- **Risk Manager** (Haiku) — VaR, Sharpe ratio, max drawdown

Sub-agents run **concurrently** via `asyncio.gather` when the Chair issues multiple delegations in a single turn. The Chair's static prefix (system prompt + tools) and growing conversation history are both **prompt-cached** with a rolling 5-min ephemeral breakpoint, cutting per-call input tokens to ~10% on later iterations.

## Project Structure

```
src/
├── core/
│   ├── agent.py              # Async BaseAgent with Anthropic SDK tool-use loop, prompt caching, parallel tool execution
│   ├── tool.py               # @tool decorator with auto schema generation
│   ├── message.py            # AgentMessage and AgentResult models
│   └── orchestrator.py       # CommitteeOrchestrator (pipeline + Chair mode)
├── data/
│   ├── models.py             # Pydantic models (Quote, OHLCV, FinancialStatements, Filing)
│   ├── cache.py              # SQLite-backed cache with TTL
│   └── providers/
│       ├── base.py           # Abstract interfaces for data providers
│       ├── yahoo.py          # Yahoo Finance implementation via yfinance
│       ├── fred.py           # FRED economic data provider
│       └── edgar.py          # SEC EDGAR filings provider
├── agents/
│   ├── committee_chair.py    # Committee Chair — orchestrates all agents
│   ├── market_data.py        # Market Data agent
│   ├── research_analyst.py   # Research Analyst agent
│   ├── alternative_data.py   # Alternative Data agent
│   ├── quant_analyst.py      # Quant Analyst agent
│   └── risk_manager.py       # Risk Manager agent
├── tools/
│   ├── market/
│   │   ├── yahoo_finance.py  # Stock price and historical data tools
│   │   └── fred.py           # Economic indicator tools
│   ├── research/
│   │   ├── sec_edgar.py      # SEC filing search tools
│   │   └── vector_search.py  # RAG knowledge base search tool
│   └── analysis/
│       ├── statistics.py     # Returns, correlations, regression tools
│       └── risk_metrics.py   # VaR, Sharpe ratio, max drawdown tools
├── rag/
│   ├── embeddings.py         # Sentence-transformers embedding generation
│   ├── chunking.py           # Section-aware document chunking
│   ├── store.py              # ChromaDB vector store wrapper
│   └── ingest.py             # Filing ingestion pipeline
├── reports/
│   ├── generator.py          # Jinja2 report renderer
│   └── templates/
│       ├── investment_memo.md
│       ├── risk_report.md
│       └── committee_decision.html
├── pipeline/
│   ├── hypothesis.py         # Investment hypothesis validation
│   └── runner.py             # Full pipeline: hypothesis → Chair → report
config/
├── settings.py               # Loads .env for API keys and config
├── agents.yaml               # Per-agent config (model, temperature, max_tokens)
└── prompts/                  # System prompts per agent (markdown files)
scripts/
├── run_committee.py          # CLI entry point
└── ingest_filings.py         # Bulk SEC filing ingestion into RAG
```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install anthropic pydantic yfinance fredapi pandas numpy scipy chromadb sentence-transformers edgartools python-dotenv jinja2
```

Create a `.env` file with your API keys:

```
ANTHROPIC_API_KEY=your-key-here
FRED_API_KEY=your-key-here
```

## Ingesting SEC Filings

Before the Research Analyst can search filings, ingest them into the vector store:

```bash
python3 scripts/ingest_filings.py --ticker AAPL --filing-type 10-K --limit 3
```

## Testing

The suite is `pytest`-based. Agent tests mock the Anthropic client (via `conftest.py`), so no API keys or network access are required for the default run:

```bash
source venv/bin/activate
pip install pytest pytest-asyncio

pytest
```

A handful of RAG tests (`test_rag.py`) exercise the real `sentence-transformers` embedding model and a local ChromaDB store; they're marked `integration` and download model weights on first run. Skip them for a fast, fully offline run:

```bash
pytest -m "not integration"
```

## Tech Stack

- **LLM**: Anthropic Claude API (Sonnet for Chair synthesis, Haiku for sub-agents)
- **Concurrency**: `asyncio` + `AsyncAnthropic` for parallel sub-agent execution
- **Token efficiency**: Anthropic prompt caching (ephemeral, rolling conversation breakpoint)
- **Data**: yfinance, FRED, SEC EDGAR (edgartools)
- **Models**: Pydantic
- **Cache**: SQLite
- **RAG**: ChromaDB + sentence-transformers
- **Analysis**: NumPy, SciPy, Pandas
- **Reports**: Jinja2 templates
