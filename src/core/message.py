from pydantic import BaseModel #Pydantic library creates data classes with auto validation so it does type enforcement for you

class AgentMessage(BaseModel): #What gets sent to an agent
    content: str
    sender: str
    context: dict = {}
    

class AgentResult(BaseModel): #What the agent returns after running
    agent_name: str
    content: str
    tool_calls: list =  []
    success: bool = True
