# 🤖 Agents — Football Club Multi-Agent System

Multi-agent system for F.C. Barcelona management, built with [LangChain](https://docs.langchain.com/) + [LangGraph](https://langchain-ai.github.io/langgraph/) using the **Handoffs** pattern.

## Tech Stack

| Component | Technology | Version |
|---|---|---|
| **Language** | Python | ≥ 3.11 (compatible with 3.11, 3.12, 3.13) |
| **Package Manager** | [uv](https://docs.astral.sh/uv/) | latest |
| **Build System** | [Hatchling](https://hatch.pypa.io/) | latest |
| **LLM Provider** | [Groq](https://console.groq.com/) via `langchain-groq` | ≥ 1.1.2 |
| **LLM Model** | `llama-3.3-70b-versatile` (configurable via `GROQ_MODEL`) | — |
| **Agent Framework** | `langchain` (`create_agent`) | ≥ 1.0 |
| **Orchestration** | `langgraph` (`StateGraph` + `MemorySaver`) | ≥ 1.0.8 |
| **Linting** | [Ruff](https://docs.astral.sh/ruff/) | ≥ 0.9.1 |
| **Type Checking** | [mypy](https://mypy-lang.org/) (strict mode) | ≥ 1.14.1 |
| **Testing** | [pytest](https://docs.pytest.org/) + coverage | ≥ 8.3.5 |
| **Environment** | `python-dotenv` (`.env` file for `GROQ_API_KEY`) | ≥ 1.2.1 |

## Architecture

```
                    ┌──────────────┐
          ┌────────→│  🔍 Scout    │────────┐
          │         └──────────────┘        │
          │                                 │
┌─────────┴────────┐               transfer_to_orchestrator
│  🎯 Orchestrator │◄──────────────────────┤
│   (triage hub)   │                        │
└─────────┬────────┘                        │
          │         ┌──────────────┐        │
          ├────────→│ 📊 Analyst   │────────┤
          │         └──────────────┘        │
          │         ┌──────────────┐        │
          └────────→│ ⚕️  Medical  │────────┘
                    └──────────────┘
```

**Pattern: Handoffs with hub-and-spoke hierarchy**
- The **Orchestrator** is the only agent that can transfer to domain agents
- **Domain agents** can only transfer back to the Orchestrator
- Domain agents **never** transfer directly to each other
- State persists across conversation turns via `MemorySaver` checkpointer

## Project Structure

```
src/football_club/
├── __init__.py
├── __main__.py              # Entry point (python -m football_club)
├── cli.py                   # Interactive CLI with streaming + colored logs
├── cli_colors.py            # ANSI color utilities for terminal output
├── config.py                # Configuration management
├── logging.py               # Logging setup
├── state.py                 # AgentState (TypedDict) + agent constants
├── agents/
│   ├── __init__.py          # Public exports
│   ├── orchestrator.py      # 🎯 Triage agent (hub)
│   ├── scout.py             # 🔍 External player scouting
│   ├── analyst.py           # 📊 Team performance analysis
│   ├── medical.py           # ⚕️  Sports medicine
│   └── tools.py             # Handoff tools (Command-based transfers)
└── graph/
    ├── __init__.py
    └── workflow.py           # LangGraph StateGraph + routing + MemorySaver
```

## Agents

### 🎯 Orchestrator (`orchestrator.py`)

| | |
|---|---|
| **Role** | Triage — detects the domain and transfers to the appropriate specialist |
| **Tools** | `transfer_to_scout`, `transfer_to_analyst`, `transfer_to_medical` |
| **Responds directly** | Only for greetings and farewells |

The orchestrator is the default `active_agent`. Every conversation starts here. It detects the user's intent and immediately transfers to the right specialist — it never answers domain questions itself.

### 🔍 Scout (`scout.py`)

| | |
|---|---|
| **Role** | Scouting and analysis of players from **other teams** |
| **Tools** | `transfer_to_orchestrator` |
| **Domain** | Transfers, scouting reports, external player comparisons, talent tracking |

### 📊 Analyst (`analyst.py`)

| | |
|---|---|
| **Role** | Technical analyst for the **current team** (F.C. Barcelona) |
| **Tools** | `transfer_to_orchestrator` |
| **Domain** | Statistics, performance metrics, tactics, formations |

### ⚕️ Medical (`medical.py`)

| | |
|---|---|
| **Role** | Sports medicine specialist |
| **Tools** | `transfer_to_orchestrator` |
| **Domain** | Injuries, recovery, prevention, fitness, rehabilitation |

## Handoff Tools (`agents/tools.py`)

Each tool uses `Command(graph=Command.PARENT)` to transfer control between agents at the parent graph level:

| Tool | Available to | Target |
|---|---|---|
| `transfer_to_scout` | Orchestrator only | Scout |
| `transfer_to_analyst` | Orchestrator only | Analyst |
| `transfer_to_medical` | Orchestrator only | Medical |
| `transfer_to_orchestrator` | Scout, Analyst, Medical | Orchestrator |

## State Management (`state.py`)

```python
class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]  # Conversation history (auto-merged)
    active_agent: NotRequired[str]                        # Currently active agent (persists across turns)
    final_answer: str                                     # Last response text
```

Key design decisions:
- `add_messages` reducer automatically merges message lists (no duplicates)
- `active_agent` persists across turns via `MemorySaver` checkpointer — this is what enables follow-up questions to stay with the same agent
- `NotRequired` means the field defaults to `None` on first turn (routing defaults to orchestrator)

## Workflow (`graph/workflow.py`)

```python
# Routing logic
route_initial(state)      # START → active_agent (default: orchestrator)
route_after_agent(state)  # AIMessage without tool_calls → END | else → active_agent

# Graph compilation
builder.compile(checkpointer=MemorySaver())
```

The workflow uses `MemorySaver` as an in-memory checkpointer. Each CLI session gets a unique `thread_id` (UUID), and the checkpointer accumulates conversation history across turns.

## CLI (`cli.py`)

Uses `workflow.stream(subgraphs=True)` for real-time event capture with colored output:

| Color | Meaning | Example |
|---|---|---|
| 🔵 Cyan | Agent activation | `🎯 Agente activo: Orquestador` |
| 🟡 Yellow | Tool usage | `🔧 Orquestador → herramienta: transfer_to_analyst` |
| 🟣 Magenta | Handoff event | `🔀 Handoff: 🎯 Orquestador → 📊 Analista` |
| 🔴 Red | Errors | `❌ Error: Rate limit reached` |
| 🟢 Green | System messages | `✓ Sistema listo!` |

## Conversation Flow Example

```
Turn 1: "Hello"
  → Orchestrator responds directly: "Hi! How can I help?"

Turn 2: "How is Lewandowski doing this season?"
  → Orchestrator → transfer_to_analyst → Analyst responds

Turn 3: "Compare him to Haaland" (follow-up)
  → Analyst → transfer_to_orchestrator → Orchestrator → transfer_to_scout → Scout responds

Turn 4: "Has he had any serious injuries?"
  → Scout → transfer_to_orchestrator → Orchestrator → transfer_to_medical → Medical responds
```

## Development

```bash
# Install dependencies
make install          # uv sync

# Run the application
make run              # uv run python -m football_club

# Linting & type checking
make lint             # ruff check + mypy (strict)

# Run tests
make test             # pytest with coverage

# Format code
make format           # ruff check --fix + ruff format

# Full CI pipeline
make ci               # lint + test

# Clean caches
make clean            # remove __pycache__, .mypy_cache, etc.
```

## Configuration

Create a `.env` file in the project root (see `.env.example`):

```env
GROQ_API_KEY=your_api_key_here
GROQ_MODEL=llama-3.3-70b-versatile    # optional, this is the default
```
