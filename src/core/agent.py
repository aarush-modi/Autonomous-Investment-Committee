import time
from anthropic import Anthropic, RateLimitError
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
        self.client = Anthropic()
        self.tool_registry = {t.tool_name: t for t in tools}
        self.tool_schemas = [t.schema for t in tools]
        #Wrap system prompt in a cache_control block so tools+system are reused across turns
        self.system_blocks = [{"type": "text", "text": system_prompt, "cache_control": {"type": "ephemeral"}}]

    #This is the core loop that sends a message to the agent and handels the back and forth with the agent when the agent needs to use tools
    def run(self, message: AgentMessage) -> AgentResult: 
        #Format the users message foir the API call
        messages = [{"role": "user", "content": message.content}]

        #Will run until the agent is done
        while True: 
            #Sends the message to the agent along with the tools, with retry on rate limit
            max_attempts = 3
            for attempt in range(max_attempts):
                try:
                    response = self.client.messages.create(model=self.model, messages=messages, tools=self.tool_schemas, max_tokens=self.max_tokens, system=self.system_blocks)
                    #TEMP: cache verification — remove after confirming cache_read > 0 on later iterations
                    u = response.usage
                    print(f"  [{self.name}] usage: input={u.input_tokens} output={u.output_tokens} cache_read={getattr(u, 'cache_read_input_tokens', 0) or 0} cache_creation={getattr(u, 'cache_creation_input_tokens', 0) or 0}")
                    break
                except RateLimitError as e:
                    if attempt == max_attempts - 1:
                        raise
                    retry_after = e.response.headers.get("retry-after") if e.response is not None else None
                    wait = float(retry_after) if retry_after else 30 * (attempt + 1)
                    print(f"  Rate limited, waiting {wait}s...")
                    time.sleep(wait)
            #If claude is done thinking
            if response.stop_reason == "end_turn": 
                text = "".join(b.text for b in response.content if b.type == "text")
                return AgentResult(agent_name=self.name, content=text)

            #Agent wants to use a tool so we need to save conversation history
            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})

                tool_results = []

                #For each tool use block in response.content
                #Iterate through the content blocks
                for block in response.content:
                    #If the block is a tool use block, look it up in the tool_registry, run it with the arguments passed by the agent, and collect the results
                    if block.type == "tool_use":
                        tool_name = block.name
                        tool_input = block.input
                        tool = self.tool_registry[tool_name]
                        result = tool(**tool_input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
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