# Autonomous Investment Committee

Multi-agent system that simulates a professional investment board. Specialized AI agents collaborate to ingest market data, analyze investments, and produce structured research reports with Buy/Sell/Hold recommendations.

## Architecture

The system uses the Anthropic Claude API to power specialized agents, each with their own tools and expertise:

- **Committee Chair** — Orchestrates all agents, synthesizes final recommendation
- **Market Data** — Fetches prices, volume, and indices from free APIs
- **Research Analyst** — SEC filings, fundamental analysis, RAG knowledge base search
- **Alternative Data** — Economic indicators, insider transactions
- **Quant Analyst** — Statistical analysis, correlations, regression
- **Risk Manager** — VaR, Sharpe ratio, max drawdown

## Project Structure

```
src/
├── core/
│   ├── agent.py              # BaseAgent with Anthropic SDK tool-use loop
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
│       └── committee_decision.md
config/
└── prompts/                  # System prompts per agent (markdown files)
scripts/
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

## Testing

```bash
source venv/bin/activate

# Test core framework (no API key needed)
python3 test_core.py

# Test data layer (no API key needed, uses free Yahoo Finance)
python3 test_data.py

# Test RAG system (no API key needed, runs locally)
python3 test_rag.py

# Test report generation (no API key needed)
python3 test_reports.py

# Test Market Data agent (needs ANTHROPIC_API_KEY)
python3 test_market_agent.py

# Test Quant, Risk, and Alt Data agents (needs ANTHROPIC_API_KEY + FRED_API_KEY)
python3 test_agents.py

# Test full Committee Chair orchestration (needs ANTHROPIC_API_KEY + FRED_API_KEY)
python3 test_chair.py
```

## Ingesting SEC Filings

```bash
python3 scripts/ingest_filings.py --ticker AAPL --filing-type 10-K --limit 3
```

## Tech Stack

- **LLM**: Anthropic Claude API
- **Data**: yfinance, FRED, SEC EDGAR (edgartools)
- **Models**: Pydantic
- **Cache**: SQLite
- **RAG**: ChromaDB + sentence-transformers
- **Analysis**: NumPy, SciPy, Pandas
- **Reports**: Jinja2 templates
