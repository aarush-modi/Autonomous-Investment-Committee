from dotenv import load_dotenv
load_dotenv()

from src.core.message import AgentMessage

# --- Test Quant Analyst (no FRED key needed) ---
print("--- Test: Quant Analyst ---")
from src.agents.quant_analyst import QuantAnalystAgent
quant = QuantAnalystAgent()
result = quant.run(AgentMessage(content="Calculate AAPL returns over the last 180 days and its correlation with MSFT", sender="user"))
print(result.content)
assert result.success
print("✓ Quant Analyst works\n")

# --- Test Risk Manager (no FRED key needed) ---
print("--- Test: Risk Manager ---")
from src.agents.risk_manager import RiskManagerAgent
risk = RiskManagerAgent()
result = risk.run(AgentMessage(content="What's the risk profile for NVDA? Calculate VaR, Sharpe ratio, and max drawdown over the last year", sender="user"))
print(result.content)
assert result.success
print("✓ Risk Manager works\n")

# --- Test Alternative Data (needs FRED_API_KEY) ---
print("--- Test: Alternative Data ---")
from src.agents.alternative_data import AlternativeDataAgent
alt = AlternativeDataAgent()
result = alt.run(AgentMessage(content="What's the current inflation and unemployment rate? Also check insider transactions for AAPL", sender="user"))
print(result.content)
assert result.success
print("✓ Alternative Data works")
