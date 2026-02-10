"""Handoff tools for agent-to-agent transfers.

Follows the official LangChain Handoffs pattern with hierarchical constraint:
- Orchestrator can transfer to any domain agent (scout, analyst, medical)
- Domain agents can ONLY transfer back to orchestrator
- Domain agents NEVER transfer directly to each other
"""

from langchain.messages import AIMessage, ToolMessage
from langchain.tools import ToolRuntime, tool
from langgraph.types import Command

from football_club.state import (
    AGENT_ANALYST,
    AGENT_MEDICAL,
    AGENT_ORCHESTRATOR,
    AGENT_SCOUT,
)


def _build_handoff_command(
    runtime: ToolRuntime,
    target_agent: str,
    transfer_message: str,
) -> Command:  # type: ignore[type-arg]
    """Build a Command for transferring to another agent.

    Extracts the last AIMessage (containing the tool call) and pairs it
    with a ToolMessage acknowledgement, following LangChain docs pattern.
    """
    last_ai_message = next(
        msg for msg in reversed(runtime.state["messages"]) if isinstance(msg, AIMessage)
    )
    tool_msg = ToolMessage(
        content=transfer_message,
        tool_call_id=runtime.tool_call_id,
    )
    return Command(
        goto=target_agent,
        update={
            "active_agent": target_agent,
            "messages": [last_ai_message, tool_msg],
        },
        graph=Command.PARENT,
    )


# --- Orchestrator tools (can transfer to any domain agent) ---


@tool
def transfer_to_scout(runtime: ToolRuntime) -> Command:  # type: ignore[type-arg]
    """Transferir al agente Scout (ojeador de jugadores de otros equipos)."""
    return _build_handoff_command(runtime, AGENT_SCOUT, "Transferido al agente Scout")


@tool
def transfer_to_analyst(runtime: ToolRuntime) -> Command:  # type: ignore[type-arg]
    """Transferir al agente Analista (rendimiento y estadísticas del equipo)."""
    return _build_handoff_command(runtime, AGENT_ANALYST, "Transferido al agente Analista")


@tool
def transfer_to_medical(runtime: ToolRuntime) -> Command:  # type: ignore[type-arg]
    """Transferir al agente Médico deportivo (lesiones y recuperación)."""
    return _build_handoff_command(runtime, AGENT_MEDICAL, "Transferido al agente Médico")


# --- Domain agent tool (can ONLY transfer back to orchestrator) ---


@tool
def transfer_to_orchestrator(runtime: ToolRuntime) -> Command:  # type: ignore[type-arg]
    """Transferir de vuelta al orquestador cuando la consulta no es de tu dominio."""
    return _build_handoff_command(
        runtime, AGENT_ORCHESTRATOR, "Transferido de vuelta al orquestador"
    )
