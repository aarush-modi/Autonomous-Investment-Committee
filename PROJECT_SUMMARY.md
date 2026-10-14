# Autonomous Investment Committee — Project Summary (at public release, August 2026)

> Purpose of this document: source material for generating a résumé/portfolio section.
> Audience: AI engineer internship / new-grad applications. Author is a student; this is a
> self-directed personal project, designed, built, and shipped solo over ~6 months.
> Everything in the "Shipped" sections below is implemented and verifiable in the repo.
> Items marked [PLANNED] were scheduled for the launch window but should be confirmed
> before claiming them.

## One-line description

A multi-agent AI system built on the Anthropic Claude API that simulates a professional
investment committee: six specialized LLM agents collaborate — orchestrated dynamically by
an LLM "Chair," not a hard-coded pipeline — to ingest live market data, analyze SEC filings
via RAG, compute quantitative risk metrics, and produce structured investment memos with
Buy/Sell/Hold recommendations, end-to-end from a single CLI command.

## Multi-agent orchestration (the core AI engineering work)

- **LLM-driven dynamic orchestration.** A Committee Chair agent (Claude Sonnet 5) receives
  an investment hypothesis and decides at runtime which specialist agents to consult, in
  what order, and with what queries — delegation is exposed to the model as a
  `delegate_to_agent` tool, so the execution graph is chosen by the model's reasoning
  rather than hard-coded. The Chair synthesizes all sub-agent findings into a final
  recommendation with a conviction level.
- **Five specialist sub-agents** (Claude Haiku 4.5, chosen for cost/latency): Market Data
  (prices, volume, indices via Yahoo Finance), Research Analyst (SEC filings, financial
  statements, RAG knowledge-base search), Alternative Data (FRED economic indicators,
  insider transactions), Quant Analyst (returns, correlations, regression), and Risk
  Manager (VaR, Sharpe ratio, max drawdown, Black-Scholes option pricing).
- **Tiered model architecture** — an expensive, high-reasoning model for synthesis and
  orchestration; cheap fast models for tool-heavy specialist work — keeping a full
  committee run under ~$1 of API spend.

## Multi-agent communication

- **Typed message passing.** Agents communicate through Pydantic models (`AgentMessage`,
  `AgentResult`) rather than raw strings, giving validated, structured inter-agent
  contracts.
- **Context accumulation.** Each specialist's result is fed back into the Chair's
  conversation as a tool result, so later delegations are informed by earlier findings —
  the Chair can follow up with a specialist based on what another specialist reported.

## Agent framework (built from scratch on the raw Anthropic SDK — no LangChain)

- **`BaseAgent`**: an async tool-use loop implementing the full Claude agentic pattern —
  send messages, branch on `stop_reason`, execute requested tools, feed results back,
  repeat until the model completes. All six agents inherit from it.
- **`@tool` decorator** that auto-generates Anthropic tool JSON schemas from Python type
  annotations and docstrings, so adding a new agent capability is one decorated function.
- **Parallel execution.** Converted the framework to `asyncio` + `AsyncAnthropic`; when
  the Chair issues multiple delegations in one turn, sub-agents run concurrently via
  `asyncio.gather` (the Chair is prompted to batch independent delegations), and each
  agent's own tool calls within a turn also execute in parallel.
- **Prompt-cache engineering.** System prompts and tool schemas are wrapped in
  `cache_control` breakpoints, and a rolling ephemeral breakpoint is moved forward along
  the growing conversation each turn (managed within the API's 4-breakpoint limit) —
  cutting per-call input token cost to roughly 10% on later loop iterations.
- **Resilience.** Rate-limit handling honors the API's `retry-after` header with
  exponential backoff; billing/credit failures in one sub-agent return a graceful
  degraded result instead of an exception, so a failure mid-`asyncio.gather` doesn't
  cancel sibling agents and the Chair can synthesize around the missing input.

## Retrieval-augmented generation (RAG)

- ChromaDB vector store with metadata filtering (ticker, filing type, date) and free
  local embeddings via sentence-transformers (no embedding API cost).
- **Section-aware chunking** for SEC filings: 10-K/10-Q documents are split on their Item
  sections (with a recursive fallback), so retrieved chunks align with the document's
  semantic structure instead of arbitrary windows.
- Bulk ingestion pipeline pulling filings from SEC EDGAR (edgartools) into the store; the
  Research Analyst queries it through a `search_knowledge_base` tool.

## Automation & data engineering

- **End-to-end automated pipeline**: one CLI command takes a ticker and a natural-language
  hypothesis and produces a multi-section markdown/HTML investment memo (thesis, market
  data, fundamentals, risk metrics, economic context, recommendation) rendered through
  Jinja2 templates with data citations.
- **Abstract data-provider interfaces** (`MarketDataProvider`, `EconomicDataProvider`,
  `FilingsProvider`) with free-tier implementations (Yahoo Finance, FRED, SEC EDGAR), so
  premium sources can be swapped in without touching agent code.
- SQLite-backed API response cache with per-data-type TTLs to respect rate limits and cut
  latency on repeated runs.
- Quantitative tooling in NumPy/SciPy/pandas: historical & parametric VaR, Sharpe, max
  drawdown, OLS regression, correlation matrices, Black-Scholes.

## Engineering & release quality [PLANNED — confirm each before claiming]

- Packaged as a pip-installable project (`pyproject.toml`, pinned dependencies, MIT
  license), released publicly on GitHub August 2026.
- pytest suite that runs fully offline — the Anthropic client is mocked (including
  tool_use responses) and data providers use recorded fixtures — wired into GitHub
  Actions CI on every push.
- First-run hardening: startup API-key validation with actionable errors, graceful
  handling of an empty vector store, per-run token/cost reporting.
- Public docs: architecture diagram, committed sample analysis reports, quickstart
  verified from a fresh clone, and a financial disclaimer.
- [STRETCH — only if completed] Backtesting engine for entry/exit strategies with
  transaction costs and look-ahead-bias protection, integrated as a Quant Analyst tool.

## Scale/impact numbers safe to cite

- 6 collaborating LLM agents; ~40 Python modules across framework, agents, tools, RAG,
  data, and reporting layers; ~15 model-callable tools.
- ~90% input-token cost reduction on later agent-loop iterations via prompt caching.
- Concurrent sub-agent execution (up to 5 agents in parallel) vs. the original
  sequential design.
- Full committee analysis of a ticker for well under $1 in API cost, on entirely
  free-tier data sources.

## Notes for the résumé generator

- Target roles: AI engineer / LLM application engineer (student, internship or new-grad).
- Emphasize: multi-agent orchestration, multi-agent communication, agentic tool-use loops
  built directly on the Anthropic SDK, async/parallel agent execution, RAG, prompt-cache
  cost engineering, and end-to-end automation.
- Do not overstate: this is a research/educational tool, not a live trading system; it
  produces research memos, not trades. Avoid implying production traffic or users.
- Honest framing that lands well: "designed and shipped solo," "built the agent framework
  from scratch on the raw SDK rather than an orchestration library."
