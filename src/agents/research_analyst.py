from src.core.agent import BaseAgent
from src.tools.research.sec_edgar import search_sec_filings, get_financial_statements
from src.tools.research.vector_search import search_knowledge_base


SYSTEM_PROMPT = open("config/prompts/research_analyst_agent.md").read()


class ResearchAnalystAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Research Analyst",
            system_prompt=SYSTEM_PROMPT,
            model="claude-haiku-4-5-20251001",
            tools=[search_sec_filings, get_financial_statements, search_knowledge_base],
            max_tokens=2048,
            temperature=0,
        )
