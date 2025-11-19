# src/tools/send_message.py

from typing import Optional, Type, Dict
from langchain_core.callbacks import CallbackManagerForToolRun
from pydantic import BaseModel
from langchain.tools import BaseTool
from src.agents.base import Agent

class SendMessage(BaseTool):
    name: str = "SendMessage"
    description: str = "Use this to send a message to one of your sub-agents"
    args_schema: Type[BaseModel]
    agent_mapping: Dict[str, "Agent"] = None

    def _run(self, recipient: str, message: str, run_manager: Optional[CallbackManagerForToolRun] = None) -> str:
        """
        Executes the tool.
        """
        print(f"--- TOOL SendMessage CALLED ---")
        print(f"Recipient: {recipient}")
        print(f"Message: {message}")

        agent = self.agent_mapping.get(recipient)

        if not agent:
            print(f"Agent '{recipient}' not found. Returning mock response.")
            return f"Message sent to mock agent '{recipient}'. The message was: '{message}'."

        print(f"Found agent '{recipient}'. Invoking...")
        try:
            # Get the config that was "smuggled" onto this tool instance by the agent
            config = getattr(self, 'config', None)

            # Pass the config to the sub-agent's invoke call
            response = agent.invoke({"messages": [("human", message)]}, config=config)
            content = response["messages"][-1].content
            print(f"Agent '{recipient}' responded with: {content}")
            return f"Successfully relayed message to {recipient}. Response: {content}"
        except Exception as e:
            print(f"Error invoking agent '{recipient}': {e}")
            return f"Error while sending message to {recipient}: {str(e)}"

    def run(self, args):
        return self._run(recipient=args["recipient"], message=args["message"])