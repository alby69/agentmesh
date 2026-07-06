# AgentMesh LLM

A unified provider interface for Large Language Models.

## Supported Providers

- **Google Gemini**
- **OpenAI**
- **Anthropic**
- **Ollama** (Local models)

## Usage

```python
from agentmesh.llm.factory import LLMProviderFactory
from agentmesh.llm.base import LLMConfig

config = LLMConfig(provider="gemini", api_key="...")
provider = LLMProviderFactory.get_provider(config)

response = provider.generate("Hello, Mesh!")
print(response)
```

## Structure

- `agentmesh.llm.base`: Base provider interface and configuration.
- `agentmesh.llm.factory`: Simple factory to instantiate providers.
- `agentmesh.llm.providers`: Specific implementations for each service.
