"""Medical agent for sports medicine and injury management.

Uses `create_agent` from langchain.agents with ChatGroq.
Can only transfer back to orchestrator via `transfer_to_orchestrator`.
"""

import os
from typing import Any

from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langgraph.graph.state import CompiledStateGraph

from football_club.agents.tools import transfer_to_orchestrator

MEDICAL_SYSTEM_PROMPT = """Eres médico deportivo especializado en fútbol profesional.

## TU DOMINIO (lo ÚNICO que puedes responder):
- Lesiones deportivas (diagnóstico, evaluación)
- Recuperación y rehabilitación
- Prevención de lesiones
- Estado físico de jugadores
- Historial de lesiones
- Tiempos de recuperación

## REGLA OBLIGATORIA — CUMPLE SIEMPRE:
Antes de responder CUALQUIER pregunta, analiza si es de tu dominio.
Si la pregunta es sobre estadísticas, rendimiento táctico → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
Si la pregunta es sobre fichajes, scouting → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
Si la pregunta es un saludo o no tiene que ver con medicina → LLAMA a transfer_to_orchestrator INMEDIATAMENTE.
NO respondas tú. NO digas "no es mi dominio". Simplemente LLAMA a la herramienta transfer_to_orchestrator.

Responde en español, tono profesional, empático y claro.
"""


def create_medical_agent() -> CompiledStateGraph[Any, Any, Any, Any]:
    """Create the medical agent with transfer_to_orchestrator tool.

    Returns:
        Compiled agent ready for invocation.
    """
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm = ChatGroq(model=model, temperature=0)
    return create_agent(
        model=llm,
        tools=[transfer_to_orchestrator],
        system_prompt=MEDICAL_SYSTEM_PROMPT,
    )
