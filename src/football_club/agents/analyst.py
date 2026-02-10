"""Analyst agent for team performance and statistics analysis.

Uses `create_agent` from langchain.agents with ChatGroq.
Can only transfer back to orchestrator via `transfer_to_orchestrator`.
"""

import os
from typing import Any

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.graph.state import CompiledStateGraph

from football_club.agents.tools import transfer_to_orchestrator

ANALYST_SYSTEM_PROMPT = """Eres el analista técnico del F.C. Barcelona.

## TU DOMINIO (lo ÚNICO que puedes responder):
- Estadísticas y rendimiento de jugadores de NUESTRO equipo (F.C. Barcelona)
- Análisis táctico del equipo
- Formaciones, patrones de juego
- Comparación de rendimiento entre jugadores NUESTROS

## REGLA OBLIGATORIA — CUMPLE SIEMPRE:
Antes de responder CUALQUIER pregunta, analiza si es de tu dominio.
Si la pregunta menciona jugadores de OTROS equipos, fichajes, mercado, Serie A, Bundesliga, \
Premier League, u otra liga → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
Si la pregunta es sobre lesiones, recuperación, estado físico → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
NO respondas tú. NO digas "no es mi dominio". Simplemente LLAMA a la herramienta transfer_to_orchestrator.

Responde en español, tono profesional y analítico.
"""


def create_analyst_agent() -> CompiledStateGraph[Any, Any, Any, Any]:
    """Create the analyst agent with transfer_to_orchestrator tool.

    Returns:
        Compiled agent ready for invocation.
    """
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm = ChatGroq(model=model, temperature=0)
    return create_agent(
        model=llm,
        tools=[transfer_to_orchestrator],
        system_prompt=ANALYST_SYSTEM_PROMPT,
    )
