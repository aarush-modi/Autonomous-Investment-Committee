import asyncio
import inspect
from anthropic import AsyncAnthropic, RateLimitError, APIStatusError
from src.core.message import AgentMessage, AgentResult

#This is the base class all agents should inherit from because it manages the tool-use loop
class BaseAgent:
    def __init__(self,name, system_prompt, model, tools, max_tokens, temperature):
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.tools = tools
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.client = AsyncAnthropic()
        self.tool_registry = {t.tool_name: t for t in tools}
        self.tool_schemas = [t.schema for t in tools]
        #Wrap system prompt in a cache_control block so tools+system are reused across turns
        self.system_blocks = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]

    async def _invoke_tool(self, block):
        tool = self.tool_registry[block.name]
        if inspect.iscoroutinefunction(tool):
            result = await tool(**block.input)
        else:
            result = tool(**block.input)
        return {
            "type": "tool_result",
            "tool_use_id": block.id,
            "content": str(result),
        }

    #This is the core loop that sends a message to the agent and handels the back and forth with the agent when the agent needs to use tools
    async def run(self, message: AgentMessage) -> AgentResult:
        #Format the users message foir the API call
        messages = [{"role": "user", "content": message.content}]

        #Will run until the agent is done
        while True:
            #Sends the message to the agent along with the tools, with retry on rate limit
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = await self.client.messages.create(model=self.model, messages=messages, tools=self.tool_schemas, max_tokens=self.max_tokens, system=self.system_blocks)
                    break
                except RateLimitError as e:
                    if attempt == max_attempts - 1:
                        raise
                    retry_after = e.response.headers.get("retry-after") if e.response is not None else None
                    wait = float(retry_after) if retry_after else 30 * (attempt + 1)
                    print(f"  Rate limited, waiting {wait}s...")
                    await asyncio.sleep(wait)
                except APIStatusError as e:
                    #Credit/billing failures shouldn't take down the whole committee — return a
                    #graceful AgentResult so the Chair can synthesize around the missing piece
                    #(and so a sub-agent failing mid-asyncio.gather doesn't cancel its siblings).
                    msg = getattr(e, "message", "") or str(e)
                    if "credit balance" in msg.lower() or "billing" in msg.lower():
                        print(f"\n  [{self.name}] Anthropic API credit balance too low — cannot complete this agent's work.")
                        print(f"  Add credits at https://console.anthropic.com/settings/billing")
                        print(f"  Returning gracefully so partial committee output is preserved.\n")
                        return AgentResult(
                            agent_name=self.name,
                            content=f"[{self.name} could not complete: Anthropic API credit balance too low. Other agents' findings should still inform the recommendation.]",
                        )
                    raise
            #If claude is done thinking
            if response.stop_reason == "end_turn":
                text = "".join(b.text for b in response.content if b.type == "text")
                return AgentResult(agent_name=self.name, content=text)

            #Output was truncated — return what we have instead of looping forever on the same prompt
            if response.stop_reason == "max_tokens":
                text = "".join(b.text for b in response.content if b.type == "text")
                print(f"  [{self.name}] hit max_tokens — returning partial output")
                return AgentResult(agent_name=self.name, content=text or f"[{self.name} hit max_tokens before completing]")

            #Agent wants to use a tool so we need to save conversation history
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                #Run all tool calls from this turn in parallel — the big async win.
                #Sub-agent delegations especially benefit since each can take many seconds.
                tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
                tool_results = list(await asyncio.gather(*(self._invoke_tool(b) for b in tool_use_blocks)))

                #Move the conversation cache breakpoint forward: strip cache_control from
                #prior tool_result blocks so we stay within the 4-breakpoint limit, then
                #mark the latest tool_result so the growing prefix gets cached.
                for prior in messages:
                    if isinstance(prior.get("content"), list):
                        for b in prior["content"]:
                            if isinstance(b, dict) and b.get("type") == "tool_result":
                                b.pop("cache_control", None)
                if tool_results:
                    tool_results[-1]["cache_control"] = {"type": "ephemeral"}
                #Send tool results back to the agent as a user message and loops back to the while True loop so the agen can process results
                messages.append({"role": "user", "content": tool_results})
