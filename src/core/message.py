#Pydantic library creates data classes with auto validation so it does type enforcement for you
from pydantic import BaseModel 

#What gets sent to an agent
class AgentMessage(BaseModel): 
    content: str
    sender: str
    context: dict = {}
    
#What the agent returns after running
class AgentResult(BaseModel): 
    agent_name: str
    content: str
    tool_calls: list =  []
    success: bool = True
