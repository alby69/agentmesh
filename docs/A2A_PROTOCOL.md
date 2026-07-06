# Agent-to-Agent (A2A) Protocol

AgentMesh uses a standardized protocol for inter-agent communication, built on top of the Nostr event system.

## 1. Message Structure

All messages between agents must follow the `AgentMessage` schema (defined in `agentmesh-core`).

### JSON Schema
```json
{
  "id": "uuid-v4",
  "sender": "npub1...",
  "receiver": "npub1...",
  "type": "task | response | error | info",
  "payload": {
    "action": "string",
    "params": {}
  },
  "timestamp": 1234567890.0,
  "signature": "optional-sig"
}
```

### Message Types
- **task**: Requesting an agent to perform an action.
- **response**: Returning the results of a task.
- **error**: Reporting a failure in task execution.
- **info**: Sharing state or metadata without requiring a response.

## 2. Agent Capabilities

Agents advertise their presence and skills using `AgentCapability` events.

```json
{
  "agent_id": "unique-id",
  "name": "Friendly Name",
  "capabilities": ["tts", "llm", "search"],
  "public_key": "npub1..."
}
```

## 3. MCP Compatibility

AgentMesh is evolving towards full **Model Context Protocol (MCP)** compatibility. This allows agents to:
- Expose local tools to LLMs.
- Share context across different agent frameworks.
- Use standardized prompts and resources.

Integrations are handled via the `agentstr-sdk`.
