"""Shared fixtures for the test suite.

Agents talk to the Anthropic API through `src.core.agent.BaseAgent`, which
constructs an `AsyncAnthropic()` client in `__init__`. None of these tests
should require a real ANTHROPIC_API_KEY or make network calls, so we patch
that client with `FakeAnthropicClient`, which plays back a scripted sequence
of responses shaped like the real SDK's `messages.create` return value.
"""
import os

# src/tools/market/fred.py constructs a module-level FredProvider() on import, which
# raises if FRED_API_KEY is unset. Agents that pull in that module (Alternative Data,
# Committee Chair) would fail to even import under test otherwise. The tests never make
# real FRED calls, so a placeholder key is enough to satisfy the constructor.
os.environ.setdefault("FRED_API_KEY", "test-fred-key")

import httpx
import pytest
from types import SimpleNamespace
from anthropic import RateLimitError


def text_block(text: str) -> SimpleNamespace:
    return SimpleNamespace(type="text", text=text)


def tool_use_block(tool_name: str, tool_input: dict, tool_id: str = "toolu_test") -> SimpleNamespace:
    return SimpleNamespace(type="tool_use", name=tool_name, input=tool_input, id=tool_id)


def end_turn_response(text: str) -> SimpleNamespace:
    return SimpleNamespace(stop_reason="end_turn", content=[text_block(text)])


def tool_use_response(tool_name: str, tool_input: dict, tool_id: str = "toolu_test") -> SimpleNamespace:
    return SimpleNamespace(stop_reason="tool_use", content=[tool_use_block(tool_name, tool_input, tool_id)])


def max_tokens_response(text: str) -> SimpleNamespace:
    return SimpleNamespace(stop_reason="max_tokens", content=[text_block(text)])


def make_rate_limit_error(retry_after: str = "0") -> RateLimitError:
    request = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    response = httpx.Response(429, headers={"retry-after": retry_after}, request=request)
    return RateLimitError("rate limited", response=response, body=None)


class FakeAnthropicClient:
    """Drop-in stand-in for `anthropic.AsyncAnthropic` that plays back canned responses."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []
        self.messages = SimpleNamespace(create=self._create)

    async def _create(self, **kwargs):
        self.calls.append(kwargs)
        item = self._responses.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


@pytest.fixture(autouse=True)
def isolated_cache(monkeypatch, tmp_path):
    """Give every test its own empty response cache, so tests never read or write the
    real data/cache.db and a previously cached response can't mask a mocked provider."""
    from src.data import cache
    monkeypatch.setattr(cache, "_cache", cache.Cache(str(tmp_path / "cache.db")))


@pytest.fixture
def install_fake_anthropic(monkeypatch):
    """Patch BaseAgent's Anthropic client factory. Returns a function that takes a
    list of responses (or exceptions to raise) and installs a FakeAnthropicClient
    that plays them back in order; the client itself is returned for call inspection.
    """
    def _install(responses):
        client = FakeAnthropicClient(responses)
        monkeypatch.setattr("src.core.agent.AsyncAnthropic", lambda: client)
        return client

    return _install
