"""Command-line interface for football-club multi-agent chat system.

Uses LangGraph streaming to display real-time colored logs of:
- Agent activity (cyan)
- Tool usage (yellow)
- Handoff events (magenta)
"""

import os
import sys
import uuid

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph.state import CompiledStateGraph

from football_club.cli_colors import (
    Colors,
    format_agent_response,
    log_agent_active,
    log_error,
    log_handoff,
    log_system,
    log_tool_call,
)
from football_club.config import Config
from football_club.graph import create_workflow
from football_club.logging import setup_logging


def print_banner() -> None:
    """Print welcome banner."""
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    banner = f"""
╔══════════════════════════════════════════════════════════════╗
║          FOOTBALL CLUB - Sistema Multi-Agente               ║
║          Modelo: {model:<42}║
║                                                              ║
║  Agentes disponibles:                                        ║
║   🔍 Scout      - Ojeador de jugadores externos             ║
║   📊 Analista   - Analista técnico del equipo               ║
║   ⚕️  Médico     - Especialista en medicina deportiva       ║
║                                                              ║
║  Comandos:                                                   ║
║   'salir' o 'exit' - Terminar el chat                       ║
║   'limpiar' o 'clear' - Nueva conversación                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def _process_stream_events(
    workflow: CompiledStateGraph,  # type: ignore[type-arg]
    user_input: str,
    thread_id: str,
) -> None:
    """Stream workflow events and display colored logs in real-time.

    Uses workflow.stream() to capture each node's output as it happens,
    then parses messages for tool calls and handoff events.
    """
    config = {"configurable": {"thread_id": thread_id}}
    input_state = {"messages": [HumanMessage(content=user_input)]}

    last_agent: str | None = None
    final_answer = ""
    responding_agent = "orchestrator"

    # Track which agents we've seen to detect handoffs
    seen_agents: list[str] = []

    for event in workflow.stream(input_state, config=config, subgraphs=True):  # type: ignore[arg-type]
        # event is a tuple (namespace, chunk) when subgraphs=True
        if isinstance(event, tuple):
            namespace, chunk = event
        else:
            _namespace = ()
            chunk = event

        if not isinstance(chunk, dict):
            continue

        for node_name, node_output in chunk.items():
            if not isinstance(node_output, dict):
                continue

            # Detect agent node execution
            if node_name in {"orchestrator", "scout", "analyst", "medical"}:
                if node_name != last_agent:
                    # Detect handoff: if we've already seen agents, this is a transfer
                    if seen_agents:
                        log_handoff(seen_agents[-1], node_name)
                    else:
                        log_agent_active(node_name)
                    seen_agents.append(node_name)
                    last_agent = node_name

            # Parse messages for tool calls and final response
            messages = node_output.get("messages", [])
            for msg in messages:
                if isinstance(msg, AIMessage):
                    # Log tool calls
                    tool_calls = getattr(msg, "tool_calls", None)
                    if tool_calls:
                        current_agent = last_agent or "orchestrator"
                        for tc in tool_calls:
                            tool_name = tc.get("name", "unknown") if isinstance(tc, dict) else getattr(tc, "name", "unknown")
                            log_tool_call(current_agent, tool_name)
                    # Track final response (last AIMessage without tool calls)
                    elif msg.content and not getattr(msg, "tool_calls", None):
                        final_answer = str(msg.content)
                        responding_agent = last_agent or "orchestrator"

    # Print the final response
    if final_answer:
        print(format_agent_response(responding_agent, final_answer))
    else:
        print(f"\n  {Colors.DIM}[Sistema]: No se obtuvo respuesta.{Colors.RESET}")


def run_chat() -> None:
    """Run the interactive chat interface."""
    load_dotenv()

    if not os.getenv("GROQ_API_KEY"):
        log_error("GROQ_API_KEY no encontrada.")
        print("Por favor, crea un archivo .env con tu API key:")
        print("  GROQ_API_KEY=tu_api_key_aqui")
        print("\nPuedes copiar .env.example como plantilla:")
        print("  cp .env.example .env")
        return

    log_system("Inicializando sistema multi-agente...")
    workflow = create_workflow()
    log_system("Sistema listo!")

    print_banner()

    # Thread ID for checkpointer — persists state across turns
    thread_id = str(uuid.uuid4())

    while True:
        try:
            user_input = input(f"\n{Colors.BOLD_WHITE}Tu:{Colors.RESET} ").strip()

            if user_input.lower() in ["salir", "exit", "quit"]:
                print(f"\n{Colors.BOLD_GREEN}Hasta luego!{Colors.RESET}")
                break

            if user_input.lower() in ["limpiar", "clear"]:
                thread_id = str(uuid.uuid4())
                log_system("Nueva conversación iniciada.")
                continue

            if not user_input:
                continue

            print()  # Blank line before logs
            _process_stream_events(workflow, user_input, thread_id)

        except KeyboardInterrupt:
            print(f"\n\n{Colors.BOLD_GREEN}Hasta luego!{Colors.RESET}")
            break
        except Exception as e:
            log_error(str(e))
            print("Por favor, intenta de nuevo.")


def main() -> int:
    """Main entry point for the CLI."""
    config = Config()
    logger = setup_logging(config.log_level)

    logger.info("Football club multi-agent system starting...")

    try:
        run_chat()
    except Exception as e:
        logger.error(f"Error in chat system: {e}")
        return 1

    logger.info("Application completed successfully")
    return 0


if __name__ == "__main__":
    sys.exit(main())
