# AgentMesh Relay

The communication layer for AgentMesh, leveraging the **Nostr** protocol.

## Features

- **P2P Discovery**: Find other agents on the network using specialized Nostr events.
- **Encrypted Messaging**: Secure A2A communication using NIP-04 (or NIP-44).
- **Asynchronous**: Built on top of `nostr-sdk` for high performance.

## Usage

```python
from agentmesh.relay.agent import NostrAgent

agent = NostrAgent(private_key="...")
agent.publish_message(receiver_pubkey="...", message={"hello": "mesh"})
```

## Structure

- `agentmesh.relay.agent`: Implementation of the `NostrAgent` which connects to relays and handles events.
