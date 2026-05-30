"""
agent_router.py — Multi-Agent Router with Conversation Memory
--------------------------------------------------------------
KEY FIX: handle_query() now accepts the full message history list.
Each agent.invoke() receives the entire conversation as a messages list,
so agents can see previous turns and maintain context.

Message history format (same as st.session_state["messages"]):
  [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]

The last item is always the new user message.
"""

from agents.receptionist_agent import receptionist_agent
from agents.reasoning_agent import reasoning_agent
from agents.memory_agent import memory_agent


class AgentRouter:
    def __init__(self):
        self.symptom_keywords = {
            "pain", "fever", "dizzy", "headache", "chest", "breathing",
            "vomit", "weakness", "seizure", "nausea", "shortness", "palpitations"
        }
        self.memory_keywords = {
            "allergy", "allergic", "diabetes", "asthma", "disease",
            "history", "bp", "blood pressure"
        }

    def route(self, user_input: str, history: list[dict]) -> dict:
        """
        Route to the correct agent, passing full conversation history.

        Args:
            user_input: The latest user message (plain string).
            history:    Full list of {"role": ..., "content": ...} dicts
                        including the current user message at the end.
        """
        text = user_input.lower()

        if any(k in text for k in self.memory_keywords):
            return self._run("🧬 Medical Memory Agent", memory_agent, history)

        if any(k in text for k in self.symptom_keywords):
            return self._run("🧠 Reasoning Agent", reasoning_agent, history)

        return self._run("🏥 Receptionist Agent", receptionist_agent, history)

    def _run(self, agent_name: str, agent, history: list[dict]) -> dict:
        """
        Convert history list → LangGraph messages tuple format and invoke agent.

        Only the last 10 messages are sent to cap token usage while keeping
        enough context for multi-turn conversations.
        """
        # Cap history to last 10 messages to reduce token usage
        trimmed = history[-10:]

        # Convert {"role": ..., "content": ...} → ("role", "content") tuples
        # which is what LangGraph's create_react_agent expects
        messages = [
            (msg["role"], msg["content"])
            for msg in trimmed
        ]

        try:
            response = agent.invoke({"messages": messages})
            output = response["messages"][-1].content
        except Exception as e:
            output = f"Agent error: {str(e)}"

        return {"agent": agent_name, "output": output}


# Singleton
_router = AgentRouter()


def handle_query(user_input: str, history: list[dict]) -> dict:
    """
    Public API called by app.py.

    Args:
        user_input: Latest message from the user.
        history:    Full conversation history including the current message.
    """
    return _router.route(user_input, history)