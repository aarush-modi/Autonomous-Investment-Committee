from src.core.tool import tool
from src.core.message import AgentMessage, AgentResult

# Test the @tool decorator
@tool("Adds two numbers")
def add(a: int, b: int) -> int:
    return a + b

assert add.tool_name == "add"
assert add.schema["name"] == "add"
assert add.schema["input_schema"]["properties"]["a"]["type"] == "integer"
assert add.schema["input_schema"]["properties"]["b"]["type"] == "integer"
assert add.schema["description"] == "Adds two numbers"
assert add(2, 3) == 5
print("✓ @tool decorator works")

# Test message models
msg = AgentMessage(content="hello", sender="test")
assert msg.context == {}

msg_with_ctx = AgentMessage(content="hello", sender="test", context={"key": "value"})
assert msg_with_ctx.context == {"key": "value"}

result = AgentResult(agent_name="test", content="done")
assert result.success is True
assert result.tool_calls == []

print("✓ Message models work")
