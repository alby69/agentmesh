# Integration Plan: `agentstr-sdk` & MCP

This document describes the strategy for integrating `agentstr-sdk` within AgentMesh to enable MCP compatibility, micropayments, and advanced Agent-to-Agent (A2A) communication.

## Objectives
1.  **MCP Compatibility**: Enable AgentMesh agents to use and offer "Tools" via the Model Context Protocol.
2.  **Native Nostr Identity**: Replace or enhance `agentmesh-relay` with `agentstr` abstractions.
3.  **Integrated Economy**: Enable Lightning/Cashu payments for task execution.
4.  **Discovery**: Implement the "Routstr" pattern for agent discovery.

---

## Phase 1: Relay Layer Refactoring
Currently, `agentmesh-relay` manages Nostr in a custom way. `agentstr-sdk` offers a more agent-oriented interface.

**Tasks:**
- [ ] Integrate `agentstr.Agent` within `BaseAgent`.
- [ ] Map existing Nostr keys to the format required by `agentstr`.
- [ ] Implement `agent_discovery.py` to register agent capabilities on relays.

## Phase 2: MCP Support (Model Context Protocol)
MCP allows agents to connect to data sources and external tools in a standardized way.

**Tasks:**
- [ ] Implement an `MCPServer` (via `agentstr`) for each AgentMesh agent that exposes its core functions as tools.
- [ ] Example: `ContentAgent` exposes a `generate_podcast(url)` tool.
- [ ] Implement an `MCPClient` to allow agents to call tools from other agents in the mesh.

## Phase 3: Micropayments & Incentives
Integration of Lightning and Cashu to make agents economically autonomous.

**Tasks:**
- [ ] Configure a wallet (LNbits or Phoenixd) interfaced with `agentstr`.
- [ ] Implement payment flow:
    - Task Request -> Invoice Generation (Lightning) -> Payment -> Task Execution.
- [ ] Support for **Cashu tokens** for offline/private payments between agents.

## Phase 4: Routing & Marketplace (Routstr Style)
Creation of a decentralized marketplace where agents can "rent" computational capacity.

**Tasks:**
- [ ] Define Nostr "Service Announcement" events (inspired by Routstr).
- [ ] Implement "Bidding" logic: agents publish a task and select the provider with the best quality/price ratio.

---

## Target Code Example

```python
from agentstr import Agent, MCPServer
from agentmesh.core import BaseAgent

class MyMeshAgent(BaseAgent):
    def __init__(self, ...):
        self.agent = Agent(name="PodcastAgent", use_lightning=True)

    async def start(self):
        # Register MCP tools
        server = MCPServer(self.agent)
        server.add_tool(self.fetch_newsletter)
        await server.start()

        # Announce presence on Nostr
        await self.agent.publish_announcement(
            skills=["podcast", "tts"],
            price_per_use="50 sats"
        )
```

## Next Steps
1. Create a prototype in `packages/agentmesh-core/examples/agentstr_poc.py`.
2. Update `apps/podcast-generator` to use the new discovery system.
