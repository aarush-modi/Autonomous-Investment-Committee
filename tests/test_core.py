import pytest

from src.core.tool import tool
from src.core.message import AgentMessage, AgentResult
from src.core.agent import BaseAgent
from conftest import end_turn_response, tool_use_response, max_tokens_response, make_rate_limit_error


@tool("Adds two numbers")
def add(a: int, b: int) -> int:
    return a + b


class TestToolDecorator:
    def test_sets_tool_name(self):
        assert add.tool_name == "add"

    def test_builds_schema_name_and_description(self):
        assert add.schema["name"] == "add"
        assert add.schema["description"] == "Adds two numbers"

    def test_builds_schema_parameter_types(self):
        properties = add.schema["input_schema"]["properties"]
        assert properties["a"]["type"] == "integer"
        assert properties["b"]["type"] == "integer"

    def test_schema_marks_params_required(self):
        assert add.schema["input_schema"]["required"] == ["a", "b"]

    def test_decorated_function_still_callable(self):
        assert add(2, 3) == 5


class TestAgentMessage:
    def test_defaults_to_empty_context(self):
        msg = AgentMessage(content="hello", sender="test")
        assert msg.context == {}

    def test_accepts_explicit_context(self):
        msg = AgentMessage(content="hello", sender="test", context={"key": "value"})
        assert msg.context == {"key": "value"}


class TestAgentResult:
    def test_defaults(self):
        result = AgentResult(agent_name="test", content="done")
        assert result.success is True
        assert result.tool_calls == []


@tool("Echoes the input back")
def echo(value: str) -> str:
    return f"echoed:{value}"


def make_agent():
    return BaseAgent(
        name="Test Agent",
        system_prompt="You are a test agent.",
        model="claude-haiku-4-5-20251001",
        tools=[echo],
        max_tokens=256,
        temperature=0,
    )


class TestBaseAgentRun:
    async def test_returns_text_on_end_turn(self, install_fake_anthropic):
        install_fake_anthropic([end_turn_response("all done")])
        agent = make_agent()

        result = await agent.run(AgentMessage(content="hi", sender="user"))

        assert result.success
        assert result.agent_name == "Test Agent"
        assert result.content == "all done"

    async def test_invokes_tool_then_returns_final_text(self, install_fake_anthropic):
        client = install_fake_anthropic([
            tool_use_response("echo", {"value": "ping"}),
            end_turn_response("tool said echoed:ping"),
        ])
        agent = make_agent()

        result = await agent.run(AgentMessage(content="use the tool", sender="user"))

        assert result.success
        assert result.content == "tool said echoed:ping"
        # Second call should carry the tool result back to the model
        second_call_messages = client.calls[1]["messages"]
        tool_result_content = second_call_messages[-1]["content"]
        assert tool_result_content[0]["content"] == "echoed:ping"

    async def test_max_tokens_returns_partial_output(self, install_fake_anthropic):
        install_fake_anthropic([max_tokens_response("partial thought...")])
        agent = make_agent()

        result = await agent.run(AgentMessage(content="hi", sender="user"))

        assert result.success
        assert result.content == "partial thought..."

    async def test_credit_balance_error_returns_graceful_result(self, install_fake_anthropic, monkeypatch):
        import httpx
        from anthropic import APIStatusError

        request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
        response = httpx.Response(400, request=request)
        error = APIStatusError("Your credit balance is too low", response=response, body=None)
        install_fake_anthropic([error])
        agent = make_agent()

        result = await agent.run(AgentMessage(content="hi", sender="user"))

        assert result.success is True
        assert "credit balance too low" in result.content
        assert result.agent_name == "Test Agent"

    async def test_retries_after_rate_limit_then_succeeds(self, install_fake_anthropic, monkeypatch):
        async def no_op_sleep(_seconds):
            return None
        monkeypatch.setattr("src.core.agent.asyncio.sleep", no_op_sleep)

        install_fake_anthropic([make_rate_limit_error(retry_after="0"), end_turn_response("recovered")])
        agent = make_agent()

        result = await agent.run(AgentMessage(content="hi", sender="user"))

        assert result.success
        assert result.content == "recovered"

    async def test_raises_after_exhausting_rate_limit_retries(self, install_fake_anthropic, monkeypatch):
        async def no_op_sleep(_seconds):
            return None
        monkeypatch.setattr("src.core.agent.asyncio.sleep", no_op_sleep)

        from anthropic import RateLimitError

        install_fake_anthropic([make_rate_limit_error(), make_rate_limit_error(), make_rate_limit_error()])
        agent = make_agent()

        with pytest.raises(RateLimitError):
            await agent.run(AgentMessage(content="hi", sender="user"))
