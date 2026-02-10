"""State management for the multi-agent system (Handoffs pattern)."""

from typing import Annotated, NotRequired, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import add_messages

# Agent name constants
AGENT_SCOUT = "scout"
AGENT_ANALYST = "analyst"
AGENT_MEDICAL = "medical"
AGENT_ORCHESTRATOR = "orchestrator"


class AgentState(TypedDict):
    """State shared across all agents in the workflow.

    Uses the Handoffs pattern: `active_agent` persists across turns
    via checkpointer, so the same agent continues handling follow-ups.
    """

    # Conversation messages (auto-merged by add_messages)
    messages: Annotated[list[BaseMessage], add_messages]

    # Currently active agent — persists across turns via checkpointer
    active_agent: NotRequired[str]

    # Final response text
    final_answer: str
