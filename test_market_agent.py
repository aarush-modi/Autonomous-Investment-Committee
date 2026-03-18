from dotenv import load_dotenv
load_dotenv()

from src.agents.market_data import MarketDataAgent
from src.core.message import AgentMessage

agent = MarketDataAgent()

# Test 1: Get a stock quote
print("--- Test: Stock Quote ---")
result = agent.run(AgentMessage(content="What's AAPL trading at?", sender="user"))
print(result.content)
assert result.success
assert result.agent_name == "Market Data"
print("✓ Stock quote works\n")

# Test 2: Get historical data
print("--- Test: Historical Data ---")
result = agent.run(AgentMessage(content="Get me NVDA historical data from 2025-01-01 to 2025-01-31", sender="user"))
print(result.content)
assert result.success
print("✓ Historical data works\n")

# Test 3: Get market indices
print("--- Test: Market Indices ---")
result = agent.run(AgentMessage(content="How are the major indices doing today?", sender="user"))
print(result.content)
assert result.success
print("✓ Market indices works")
