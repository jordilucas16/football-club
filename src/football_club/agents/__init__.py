"""Multi-agent system for football club management."""

from football_club.agents.analyst import create_analyst_agent
from football_club.agents.medical import create_medical_agent
from football_club.agents.orchestrator import create_orchestrator_agent
from football_club.agents.scout import create_scout_agent

__all__ = [
    "create_orchestrator_agent",
    "create_scout_agent",
    "create_analyst_agent",
    "create_medical_agent",
]
