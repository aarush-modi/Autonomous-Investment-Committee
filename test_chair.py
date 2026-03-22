from dotenv import load_dotenv
load_dotenv()

from src.core.orchestrator import CommitteeOrchestrator

# Run the full committee with the Chair agent
orch = CommitteeOrchestrator()
result = orch.run_with_chair("Evaluate AAPL as a long position given strong iPhone sales and services growth")

print(result["recommendation"])
assert result["success"]
print("\n✓ Committee Chair orchestration works")
