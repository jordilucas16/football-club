# 🏗️ Arquitectura LangGraph - Sistema Multi-Agente

## 📚 Librerías Utilizadas

```python
# LangGraph (framework de workflows)
from langgraph.graph import StateGraph, END, add_messages
from langgraph.graph.state import CompiledStateGraph

# LangChain (para LLMs)
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
```

## 🎯 Conceptos Clave

### 1. Estado Compartido (AgentState)

El estado es un `TypedDict` que todos los nodos comparten:

```python
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import add_messages

class AgentState(TypedDict):
    # messages usa add_messages como "reducer"
    # Esto permite que LangGraph gestione automáticamente la lista de mensajes
    messages: Annotated[list[BaseMessage], add_messages]

    # Campos adicionales del estado
    next_agent: str
    final_answer: str
```

**¿Qué es `add_messages`?**
- Es un **reducer** (función de reducción)
- Gestiona automáticamente cómo se combinan los mensajes cuando múltiples nodos actualizan el estado
- **No deprecado** - es la forma recomendada en LangGraph

### 2. Agentes (Nodos del Grafo)

Los agentes son **clases Python normales** con un método `invoke`:

```python
class BaseAgent:
    def __init__(self):
        # Inicializar el LLM (ChatAnthropic de LangChain)
        self.llm = ChatAnthropic(model_name="claude-sonnet-4-5-20250929")

    def invoke(self, state: AgentState) -> dict:
        """
        Este método es llamado por LangGraph cuando el nodo se ejecuta.

        Args:
            state: Estado actual del grafo

        Returns:
            Diccionario con las actualizaciones del estado
        """
        # 1. Preparar el prompt
        system_msg = SystemMessage(content="Eres un experto...")
        messages = [system_msg] + state["messages"]

        # 2. Llamar al LLM
        response = self.llm.invoke(messages)

        # 3. Devolver actualizaciones del estado
        # LangGraph automáticamente fusiona esto con el estado actual
        return {
            "messages": [response],  # Se añade a la lista existente
            "final_answer": response.content
        }
```

**Puntos importantes:**
- NO heredamos de ninguna clase de LangGraph
- El método `invoke(state) -> dict` es la interfaz estándar
- Devolvemos un diccionario con las actualizaciones del estado
- LangGraph automáticamente fusiona las actualizaciones

### 3. Grafo de LangGraph (StateGraph)

El grafo conecta todos los agentes:

```python
def create_workflow() -> CompiledStateGraph:
    # 1. Crear instancias de los agentes
    orchestrator = OrchestratorAgent()
    scout = ScoutAgent()
    analyst = AnalystAgent()
    medical = MedicalAgent()

    # 2. Crear el grafo
    workflow = StateGraph(AgentState)

    # 3. Añadir nodos (cada nodo es un agente)
    workflow.add_node("orchestrator", orchestrator.invoke)
    workflow.add_node("scout", scout.invoke)
    workflow.add_node("analyst", analyst.invoke)
    workflow.add_node("medical", medical.invoke)

    # 4. Definir punto de entrada
    workflow.set_entry_point("orchestrator")

    # 5. Añadir edges condicionales (routing)
    def route_to_agent(state: AgentState) -> str:
        """Decide el siguiente nodo basándose en el estado."""
        return state["next_agent"]  # "scout", "analyst", "medical", o END

    workflow.add_conditional_edges(
        "orchestrator",  # Desde este nodo
        route_to_agent,  # Función de decisión
        {
            "scout": "scout",
            "analyst": "analyst",
            "medical": "medical",
            END: END
        }
    )

    # 6. Añadir edges directos (todos terminan)
    workflow.add_edge("scout", END)
    workflow.add_edge("analyst", END)
    workflow.add_edge("medical", END)

    # 7. Compilar el grafo
    return workflow.compile()
```

### 4. Flujo de Ejecución

```
Usuario envía pregunta
         ↓
┌────────────────────┐
│  ESTADO INICIAL    │
│  messages: [...]   │
│  next_agent: ""    │
└────────────────────┘
         ↓
┌────────────────────┐
│  ORCHESTRATOR      │ ← Punto de entrada (entry_point)
│  invoke(state)     │
└────────────────────┘
         ↓
Estado actualizado:
  next_agent: "scout"
         ↓
┌────────────────────┐
│  ROUTING           │ ← Conditional edge decide el siguiente nodo
│  route_to_agent()  │
└────────────────────┘
         ↓
┌────────────────────┐
│  SCOUT AGENT       │ ← Nodo seleccionado
│  invoke(state)     │
└────────────────────┘
         ↓
┌────────────────────┐
│  END               │ ← Fin del grafo
└────────────────────┘
         ↓
Respuesta final al usuario
```

## 🔧 APIs Modernas vs Deprecadas

### ✅ APIs que USAMOS (Modernas)

```python
# Estado con reducers
messages: Annotated[list[BaseMessage], add_messages]

# Creación del grafo
workflow = StateGraph(AgentState)

# Nodos
workflow.add_node("name", function)

# Edges
workflow.add_edge("from", "to")
workflow.add_conditional_edges("from", router_fn, mapping)

# Compilación
compiled = workflow.compile()

# Ejecución
result = compiled.invoke(initial_state)
```

### ❌ APIs Deprecadas que NO USAMOS

```python
# ❌ NO USAR: AgentExecutor (deprecado en LangChain)
from langchain.agents import AgentExecutor  # DEPRECADO

# ❌ NO USAR: initialize_agent (deprecado)
from langchain.agents import initialize_agent  # DEPRECADO

# ✅ USAR: LangGraph StateGraph (recomendado)
from langgraph.graph import StateGraph  # MODERNO
```

## 🎨 Características del Diseño Actual

1. **Patrón Orquestador**: Un agente central (orchestrator) decide el routing
2. **Sin comunicación directa**: Los agentes de dominio no se comunican entre sí
3. **Estado compartido**: Todos los agentes acceden al mismo estado
4. **Type-safe**: Todo tipado con TypedDict y type hints
5. **Modular**: Fácil añadir nuevos agentes

## 🔍 Cómo Añadir Tools a los Agentes

Los agentes pueden usar tools (funciones que el LLM puede llamar):

```python
from langchain_core.tools import tool

@tool
def search_player_stats(player_name: str) -> str:
    """Busca estadísticas de un jugador."""
    # Implementación...
    return f"Stats de {player_name}: ..."

class ScoutAgent(BaseAgent):
    def get_tools(self) -> list:
        return [search_player_stats]

    def invoke(self, state: AgentState) -> dict:
        tools = self.get_tools()

        # Bind tools al LLM
        llm_with_tools = self.llm.bind_tools(tools)

        # El LLM puede ahora llamar a las tools
        response = llm_with_tools.invoke(messages)

        return {"messages": [response]}
```

## 📖 Referencias Oficiales

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph State Management](https://langchain-ai.github.io/langgraph/concepts/low_level/#state)
- [LangGraph Multi-Agent Patterns](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)
