# src/agents/base/agents_orchestrator.py

from pydantic import Field, create_model
from .agent import Agent
from src.tools.send_message import SendMessage
from langchain_core.messages import AIMessage  # <--- IMPORT AIMessage

class AgentsOrchestrator:
    def __init__(self, main_agent: Agent, agents: list[Agent]):
        self.main_agent = main_agent
        self.agents = agents
        self.agent_mapping = {}

        # Set up the communication framework
        self._populate_agent_mapping()

        # --- MOCK non-WhatsApp agents (FIXED) ---
        for agent_name, agent_obj in self.agent_mapping.items():
            if agent_name.lower() != "whatsapp_agent":
                # Create a proper synchronous mock function
                def create_mock_invoke(current_agent):
                    def mock_invoke(*args, **kwargs):
                        # Extract the actual message content
                        messages = kwargs.get("messages", args[0] if args else {"messages": []})
                        human_message_content = messages["messages"][0][1]

                        # Create a mock AI response
                        response_content = f"This is a mock response from {current_agent.name}. I received your message: '{human_message_content}'"

                        # ✅ FIX: Return a proper AIMessage object, not a tuple
                        return {"messages": [AIMessage(content=response_content)]}
                    return mock_invoke

                # Replace the agent's invoke method with our new mock
                agent_obj.invoke = create_mock_invoke(agent_obj)

        self._add_send_message_tool()

    def invoke(self, message, **kwargs):
        messages = {"messages": [("human", message)]}
        response = self.main_agent.invoke(messages, **kwargs)
        return response["messages"][-1].content

    def stream(self, message, **kwargs):
        messages = {"messages": [("human", message)]}
        for chunk in self.main_agent.stream(messages, **kwargs):
            yield chunk

    def _populate_agent_mapping(self):
        for agent in self.agents:
            self.agent_mapping[agent.name] = agent

    def _create_dynamic_send_message_tool(self, agent: "Agent") -> "SendMessage":
        recipients_description = "\n".join(
            f"{sub_agent.name}: {sub_agent.description}"
            for sub_agent in agent.sub_agents
            if sub_agent.description
        )
        DynamicSendMessageInput = create_model(
            f"{agent.name}SendMessageInput",
            recipient=(str, Field(..., description=recipients_description)),
            message=(str, Field(..., description="Message to send to sub-agent.")),
        )
        send_message_tool = SendMessage(args_schema=DynamicSendMessageInput)
        send_message_tool.agent_mapping = self.agent_mapping
        return send_message_tool

    def _add_send_message_tool(self):
        for agent in self.agents:
            if hasattr(agent, "sub_agents") and agent.sub_agents:
                send_message_tool = self._create_dynamic_send_message_tool(agent)
                agent.tools.append(send_message_tool)
                agent.initiat_agent()

    def get_agent(self, name: str) -> "Agent":
        return self.agent_mapping.get(name)