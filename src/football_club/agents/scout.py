"""Scout agent for player scouting and recruitment analysis.

Uses `create_agent` from langchain.agents with ChatGroq.
Can only transfer back to orchestrator via `transfer_to_orchestrator`.
"""

import os
from typing import Any

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.graph.state import CompiledStateGraph

from football_club.agents.tools import transfer_to_orchestrator

SCOUT_SYSTEM_PROMPT = """Eres un ojeador profesional de fútbol con 20+ años de experiencia.

## TU DOMINIO (lo ÚNICO que puedes responder):
- Análisis de jugadores de OTROS EQUIPOS
- Recomendaciones de fichajes
- Comparación de jugadores externos
- Seguimiento de talentos de otros clubes

## REGLA OBLIGATORIA — CUMPLE SIEMPRE:
Antes de responder CUALQUIER pregunta, analiza si es de tu dominio.
Si la pregunta es sobre lesiones, recuperación, estado físico → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
Si la pregunta es sobre rendimiento de NUESTRO equipo → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
Si la pregunta es un saludo o no tiene que ver con scouting → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
NO respondas tú. NO digas "no es mi dominio". Simplemente LLAMA a la herramienta transfer_to_orchestrator.

Responde en español, tono profesional pero accesible.
"""


def create_scout_agent() -> CompiledStateGraph[Any, Any, Any, Any]:
    """Create the scout agent with transfer_to_orchestrator tool.

    Returns:
        Compiled agent ready for invocation.
    """
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm = ChatGroq(model=model, temperature=0)
    return create_agent(
        model=llm,
        tools=[transfer_to_orchestrator],
        system_prompt=SCOUT_SYSTEM_PROMPT,
    )
