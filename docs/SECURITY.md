# Security & Threat Model

AgentMesh is a decentralized system, which introduces unique security challenges compared to centralized architectures. This document outlines the threat model and suggested mitigations.

## 1. Threat Model

### Identity Theft (Nostr)
- **Threat**: If a user's or agent's private key is compromised, an attacker can impersonate them on the mesh.
- **Impact**: Sending malicious messages, stealing funds (Lightning/Cashu), and damaging reputation.
- **Mitigation**: Use hardware modules for key storage where possible. Implement key rotation protocols.

### Data Poisoning (IPFS)
- **Threat**: Malicious actors can upload harmful content and share its CID.
- **Impact**: Agents might process malicious scripts or users might download harmful files.
- **Mitigation**: Always verify CIDs. Content-addressing ensures that if the data changes, the CID changes. Use sandboxed environments for processing external content.

### Spam and DDoS (Relays)
- **Threat**: Attackers can flood Nostr relays with garbage events.
- **Impact**: Increased latency, high costs for relay operators, and potential exhaustion of agent resources.
- **Mitigation**: Implement rate limiting on the agent side (ignoring too many messages from the same sender). Use relays with authentication (NIP-42) or pay-to-relay models.

### Privacy Leaks
- **Threat**: Public relays broadcast metadata (IP addresses, timing).
- **Impact**: De-anonymization of users and agents.
- **Mitigation**: Use Tor/VPN. Encrypt all sensitive payloads (NIP-04/NIP-44).

## 2. Best Practices for Developers

- **Input Validation**: Never trust the `payload` of an `AgentMessage`. Validate it using Pydantic schemas.
- **Resource Limits**: Set timeouts for LLM calls and TTS synthesis to prevent resource exhaustion.
- **Encrypted Storage**: Sensitive local data should be encrypted at rest.

## 3. Reporting Vulnerabilities

If you find a security vulnerability, please report it via [GitHub Issues] or contact the maintainers privately.
