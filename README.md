# ⚽ Football Club - Sistema Multi-Agente

Sistema inteligente de gestión de club de fútbol basado en **LangGraph** con arquitectura multi-agente y patrón orquestador.

## 🎯 Descripción

Sistema de chat interactivo con agentes especializados en diferentes áreas de gestión de un club de fútbol:

- **🔍 Scout** - Ojeador experto en análisis de jugadores externos
- **📊 Analista Técnico** - Especialista en estadísticas y rendimiento del equipo
- **⚕️ Médico Deportivo** - Experto en lesiones y medicina deportiva

El **Orquestador** analiza cada consulta y la redirige automáticamente al agente más adecuado.

## 🚀 Inicio Rápido

### 1. Instalación

```bash
# Instalar dependencias
uv sync
```

### 2. Configuración

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y añadir tu API key de Anthropic
# ANTHROPIC_API_KEY=tu_api_key_aqui
```

### 3. Ejecutar

```bash
# Iniciar el chat interactivo
make run

# O directamente:
uv run python -m football_club
```

## 💬 Uso del Chat

Una vez iniciado, puedes hacer preguntas como:

```
💬 Tú: ¿Cómo está jugando Haaland esta temporada?
🔍 Scout: [Análisis detallado del ojeador]

💬 Tú: ¿Cuál es el rendimiento de nuestro delantero?
📊 Analista: [Estadísticas del analista técnico]

💬 Tú: ¿Cuándo volverá Pedri de su lesión?
⚕️ Médico: [Información médica especializada]
```

**Comandos disponibles:**
- `salir` o `exit` - Terminar el chat
- `limpiar` o `clear` - Limpiar historial de conversación

## 🏗️ Arquitectura

```
Usuario
   ↓
Orquestador → Scout     → Respuesta
           → Analista   → Respuesta
           → Médico     → Respuesta
```

**Flujo:**
1. Usuario hace una pregunta
2. Orquestador analiza y selecciona el agente apropiado
3. Agente especializado procesa la consulta
4. Respuesta se devuelve al usuario

**Nota:** Los agentes de dominio NO se comunican entre sí.

## 🛠️ Desarrollo

### Comandos Comunes

```bash
# Ejecutar aplicación
make run

# Ejecutar tests
make test

# Linting y type checking
make lint

# Formatear código
make format

# CI completo
make ci
```

### Estructura del Proyecto

```
src/football_club/
├── agents/              # Agentes del sistema
│   ├── base.py         # Clase base de agentes
│   ├── orchestrator.py # Orquestador
│   ├── scout.py        # Agente scout
│   ├── analyst.py      # Agente analista
│   └── medical.py      # Agente médico
├── graph/              # Grafo de LangGraph
│   └── workflow.py     # Definición del workflow
├── state.py            # Estado compartido
└── cli.py              # Interfaz de chat
```

## 📋 Requisitos

- Python >= 3.11
- uv (gestión de dependencias)
- API Key de Anthropic (Claude)

## 🧪 Testing

```bash
# Ejecutar todos los tests
make test

# Con cobertura
uv run pytest --cov=football_club --cov-report=html
```

## 📦 Tecnologías

- **LangGraph** - Framework de workflows multi-agente
- **LangChain** - Orquestación de LLMs
- **Claude 4.5 Sonnet** - Modelo de lenguaje
- **Python 3.13** - Lenguaje de programación
