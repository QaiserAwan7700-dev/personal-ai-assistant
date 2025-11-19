from typing import List
from langgraph.prebuilt import create_react_agent
# ✅ Updated: get_llm_by_provider is no longer needed; we pass model & provider directly
# from src.utils import get_llm_by_provider

class Agent:
    def __init__(
        self,
        name: str,
        description: str,
        system_prompt: str,
        tools: List,  # tools can now include tool instances, no type hint issue
        sub_agents: List['Agent'],
        model: str,  # model name only, e.g., "gpt-4o"
        temperature: float,
        memory=None  # memory storage optional
    ):
        self.name = name
        self.description = description
        self.system_prompt = system_prompt
        self.tools = tools
        self.sub_agents = sub_agents
        self.model = model
        self.temperature = temperature
        self.agent = None
        self.memory = memory

    def invoke(self, *args, **kwargs):
        if not self.agent:
            self.initiat_agent()
        print(f"--- Calling {self.name} ---")
        response = self.agent.invoke(*args, **kwargs)
        return response

    def stream(self, *args, **kwargs):
        if not self.agent:
            self.initiat_agent()
        print(f"--- Calling {self.name} ---")
        for chunk in self.agent.stream(*args, **kwargs):
            yield chunk

    def initiat_agent(self):
        # Only pass model string; tools can be empty list if no tools yet
        self.agent = create_react_agent(
            model=self.model,               # required: model string e.g., "openai/gpt-4o-mini"
            tools=self.tools or [],         # required: list of tools (empty list if none)
            checkpointer=self.memory if self.memory else False
        )
