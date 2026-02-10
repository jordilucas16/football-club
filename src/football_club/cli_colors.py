"""ANSI colored output utilities for CLI logging.

Color scheme:
  🔵 CYAN    — Agent activity (which agent is processing)
  🟡 YELLOW  — Tool usage (which tool an agent is calling)
  🟣 MAGENTA — Handoff events (agent-to-agent transfers)
  🔴 RED     — Errors
  🟢 GREEN   — System messages
  ⬜ DIM     — Timestamps and metadata
"""


class Colors:
    """ANSI escape codes for terminal colors."""

    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # Agent activity
    CYAN = "\033[36m"
    BOLD_CYAN = "\033[1;36m"

    # Tool usage
    YELLOW = "\033[33m"
    BOLD_YELLOW = "\033[1;33m"

    # Handoff events
    MAGENTA = "\033[35m"
    BOLD_MAGENTA = "\033[1;35m"

    # Errors
    RED = "\033[31m"
    BOLD_RED = "\033[1;31m"

    # System / success
    GREEN = "\033[32m"
    BOLD_GREEN = "\033[1;32m"

    # User input
    WHITE = "\033[37m"
    BOLD_WHITE = "\033[1;37m"


# Agent emoji map
AGENT_EMOJI = {
    "orchestrator": "🎯",
    "scout": "🔍",
    "analyst": "📊",
    "medical": "⚕️",
}

# Agent display names
AGENT_DISPLAY = {
    "orchestrator": "Orquestador",
    "scout": "Scout",
    "analyst": "Analista",
    "medical": "Médico",
}


def log_agent_active(agent_name: str) -> None:
    """Log which agent is currently processing (CYAN)."""
    emoji = AGENT_EMOJI.get(agent_name, "🤖")
    display = AGENT_DISPLAY.get(agent_name, agent_name)
    print(
        f"  {Colors.BOLD_CYAN}{emoji} Agente activo: {display}{Colors.RESET}",
        flush=True,
    )


def log_tool_call(agent_name: str, tool_name: str) -> None:
    """Log a tool being called by an agent (YELLOW)."""
    display = AGENT_DISPLAY.get(agent_name, agent_name)
    print(
        f"  {Colors.BOLD_YELLOW}🔧 {display} → herramienta: {tool_name}{Colors.RESET}",
        flush=True,
    )


def log_handoff(from_agent: str, to_agent: str) -> None:
    """Log a handoff between agents (MAGENTA)."""
    from_emoji = AGENT_EMOJI.get(from_agent, "🤖")
    from_display = AGENT_DISPLAY.get(from_agent, from_agent)
    to_emoji = AGENT_EMOJI.get(to_agent, "🤖")
    to_display = AGENT_DISPLAY.get(to_agent, to_agent)
    print(
        f"  {Colors.BOLD_MAGENTA}🔀 Handoff: {from_emoji} {from_display} → {to_emoji} {to_display}{Colors.RESET}",
        flush=True,
    )


def log_error(message: str) -> None:
    """Log an error (RED)."""
    print(f"  {Colors.BOLD_RED}❌ Error: {message}{Colors.RESET}", flush=True)


def log_system(message: str) -> None:
    """Log a system message (GREEN)."""
    print(f"  {Colors.BOLD_GREEN}✓ {message}{Colors.RESET}", flush=True)


def format_agent_response(agent_name: str, content: str) -> str:
    """Format the final agent response with color."""
    emoji = AGENT_EMOJI.get(agent_name, "🤖")
    display = AGENT_DISPLAY.get(agent_name, agent_name)
    return f"\n{Colors.BOLD_WHITE}{emoji} [{display}]:{Colors.RESET} {content}"
