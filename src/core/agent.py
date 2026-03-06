from anthropic import Anthropic
from src.core.message import AgentMessage, AgentResult


class BaseAgent: #This is the base class all agents should inherit from because it manages the tool-use loop
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

    def run(self, message: AgentMessage) -> AgentResult: #This is the core loop that sends a message to the agent and handels the back and forth with the agent when the agent needs to use tools
        messages = [{"role": "user", "content": message.content}]#Format the users message foir the API call

        while True: #Will run until the agent is done
            response = self.client.messages.create(model=self.model, messages=messages, tools=self.tool_schemas, max_tokens=self.max_tokens, system=self.system_prompt) #Sends the message to the agent along with the tools

            if response.stop_reason == "end_turn": #If claude is done thinking
                text = "".join(b.text for b in response.content if b.type == "text")
                return AgentResult(agent_name=self.name, content=text)

            if response.stop_reason == "tool_use": #Agent wants to use a tool so we need to save conversation history
                messages.append({"role": "assistant", "content": response.content})
                
                tool_results = []

                #For each tool use block in response.content
                for block in response.content: #Iterate through the content blocks
                    if block.type == "tool_use": #If the block is a tool use block, look it up in the tool_registry, run it with the arguments passed by the agent, and collect the results
                        tool_name = block.name
                        tool_input = block.input
                        tool = self.tool_registry[tool_name]
                        result = tool(**tool_input)
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": str(result),
                        })
                messages.append({"role": "user", "content": tool_results}) #Send tool results back to the agent as a user message and loops back to the while True loop so the agen can process results