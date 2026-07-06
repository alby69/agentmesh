import asyncio
from podcast_generator.config import Settings
from podcast_generator.translator import get_llm_provider
from agentmesh.llm import BaseLLMProvider

async def main():
    cfg = Settings()
    cfg.llm_provider = "openai"
    cfg.openai_api_key = "test-key"

    try:
        provider = get_llm_provider(cfg)
        print(f"Provider initialized: {type(provider)}")
        assert isinstance(provider, BaseLLMProvider)
        print("Test PASSED: Provider is an instance of BaseLLMProvider")
    except Exception as e:
        print(f"Test FAILED: {e}")

if __name__ == "__main__":
    asyncio.run(main())
