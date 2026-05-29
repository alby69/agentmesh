# AgentMesh Architecture Rules

- **Modular Agents**: Every agent must inherit from `BaseAgent` in `agentmesh-core`.
- **Package Separation**:
    - `agentmesh-core`: Logic only, no protocol-specific dependencies if possible.
    - `agentmesh-relay`: Nostr protocol specific.
    - `agentmesh-vault`: IPFS/Storage specific.
- **Orchestration**: Use `MeshOrchestrator` to manage agent lifecycles.
- **Async Everywhere**: All agent methods (`start`, `stop`, tasks) must be `async`.
- **Configuration**: Use `MeshConfig` (Pydantic) for all agent settings.
- **Cross-App Reuse**: Keep `packages/` generic enough to be used by any app in `apps/`.
