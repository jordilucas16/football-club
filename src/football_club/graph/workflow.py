"""LangGraph workflow definition using the Handoffs pattern.

Follows the official LangChain Handoffs pattern (multiple agent subgraphs):
- Each agent is a `create_agent` subgraph with handoff tools
- `active_agent` state tracks who handles the conversation
- MemorySaver checkpointer persists state between turns
- Hierarchical: domain agents only transfer back to orchestrator
"""

from typing import Any

from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from football_club.agents.analyst import create_analyst_agent
from football_club.agents.medical import create_medical_agent
from football_club.agents.orchestrator import create_orchestrator_agent
from football_club.agents.scout import create_scout_agent
from football_club.state import (
    AGENT_ANALYST,
    AGENT_MEDICAL,
    AGENT_ORCHESTRATOR,
    AGENT_SCOUT,
    AgentState,
)

# All valid agent node names
ALL_AGENTS = [AGENT_ORCHESTRATOR, AGENT_SCOUT, AGENT_ANALYST, AGENT_MEDICAL]


def route_initial(
    state: AgentState,
) -> str:
    """Route START to the currently active agent.

    On first message, defaults to orchestrator. On subsequent turns,
    the checkpointer restores active_agent so the same agent continues.
    """
    active = state.get("active_agent", AGENT_ORCHESTRATOR)
    if active in ALL_AGENTS:
        return str(active)
    return AGENT_ORCHESTRATOR


def route_after_agent(
    state: AgentState,
) -> str:
    """Check if the agent finished or handed off.

    - AIMessage without tool_calls → agent finished responding → END
    - Otherwise → route to the (possibly updated) active_agent
    """
    messages = state.get("messages", [])
    if messages:
        last_msg = messages[-1]
        if isinstance(last_msg, AIMessage) and not getattr(last_msg, "tool_calls", None):
            return "__end__"

    active = state.get("active_agent", AGENT_ORCHESTRATOR)
    if active in ALL_AGENTS:
        return str(active)
    return AGENT_ORCHESTRATOR


def create_workflow() -> CompiledStateGraph[Any, Any, Any, Any]:
    """Create the multi-agent workflow with Handoffs pattern.

    Flow:
        1. User message enters via START
        2. route_initial sends to the active agent (default: orchestrator)
        3. Agent responds directly OR uses a handoff tool to transfer
        4. route_after_agent checks: finished (END) or handed off (next agent)
        5. State persists via MemorySaver checkpointer between turns

    Returns:
        Compiled StateGraph with checkpointer
    """
    # Create all agents
    orchestrator = create_orchestrator_agent()
    scout = create_scout_agent()
    analyst = create_analyst_agent()
    medical = create_medical_agent()

    # Build workflow
    builder = StateGraph(AgentState)

    # Add agent nodes — each invokes its subgraph
    builder.add_node(AGENT_ORCHESTRATOR, orchestrator)
    builder.add_node(AGENT_SCOUT, scout)
    builder.add_node(AGENT_ANALYST, analyst)
    builder.add_node(AGENT_MEDICAL, medical)

    # START → active agent
    builder.add_conditional_edges(START, route_initial, ALL_AGENTS)

    # After each agent → END or handoff
    for agent_name in ALL_AGENTS:
        builder.add_conditional_edges(
            agent_name,
            route_after_agent,
            [*ALL_AGENTS, END],
        )

    return builder.compile(checkpointer=MemorySaver())
