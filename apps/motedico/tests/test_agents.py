"""Tests for motedico agents."""

from motedico.agents.specialized import ProjectAgent, AdvisorAgent
from agentmesh.core import MeshConfig


def test_project_agent_init():
    agent = ProjectAgent(MeshConfig(agent_id="test-project"))
    assert agent is not None


def test_advisor_agent_init():
    agent = AdvisorAgent(MeshConfig(agent_id="test-advisor"))
    assert agent is not None
