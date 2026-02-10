"""Orchestrator triage agent for the football club multi-agent system.

Uses `create_agent` with handoff tools to route conversations to the
appropriate domain agent. This is the default active agent and the hub
in the hub-and-spoke handoff architecture.
"""

import os
from typing import Any

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.graph.state import CompiledStateGraph

from football_club.agents.tools import (
    transfer_to_analyst,
    transfer_to_medical,
    transfer_to_scout,
)

ORCHESTRATOR_SYSTEM_PROMPT = """Eres el orquestador del F.C. Barcelona. Tu ÚNICA función es:
1. Detectar el dominio de la pregunta del usuario
2. Llamar a la herramienta de transferencia correspondiente INMEDIATAMENTE

## HERRAMIENTAS DE TRANSFERENCIA (DEBES usar una):
- transfer_to_analyst → TODO lo que sea sobre NUESTRO equipo: plantilla, jugadores, estadísticas, rendimiento, tácticas
- transfer_to_scout → TODO lo que sea sobre jugadores de OTROS equipos: fichajes, comparaciones, mercado
- transfer_to_medical → TODO lo que sea sobre lesiones, recuperación, estado físico, medicina

## COMPORTAMIENTO OBLIGATORIO:
- NUNCA respondas tú directamente preguntas sobre fútbol. SIEMPRE transfiere.
- NO preguntes "¿quieres que te transfiera?". TRANSFIERE DIRECTAMENTE sin pedir permiso.
- Solo responde tú directamente si es un saludo simple ("hola", "ey") o despedida.
- Si el usuario dice "sí", "claro", "dale", "ok" después de que le mencionaste un agente, TRANSFIERE INMEDIATAMENTE.
- Ante la duda, TRANSFIERE. Es mejor transferir de más que de menos.

Responde SIEMPRE en español y sé muy breve (máximo 1-2 frases) solo para saludos.
"""


def create_orchestrator_agent() -> CompiledStateGraph[Any, Any, Any, Any]:
    """Create the orchestrator triage agent with handoff tools.

    The orchestrator is the default active agent and the only one that
    can transfer to domain agents (scout, analyst, medical).

    Returns:
        Compiled agent ready for invocation.
    """
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm = ChatGroq(model=model, temperature=0)
    return create_agent(
        model=llm,
        tools=[transfer_to_scout, transfer_to_analyst, transfer_to_medical],
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
    )
