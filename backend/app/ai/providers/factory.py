import logging
from typing import Optional

from app.ai.providers.base import AIProvider
from app.ai.providers.gemini import GeminiProvider
from app.ai.providers.openai import OpenAIProvider
from app.ai.providers.ollama import OllamaProvider

logger = logging.getLogger(__name__)


class AIProviderFactory:
    _instance: Optional[AIProvider] = None
    _provider_name: Optional[str] = None

    @classmethod
    async def get_provider(cls) -> AIProvider:
        try:
            from app.infrastructure.database import async_session_factory
            from app.infrastructure.repositories.system_setting_repository import SystemSettingRepositoryImpl

            async with async_session_factory() as db:
                repo = SystemSettingRepositoryImpl(db)
                provider_setting = await repo.get_by_key("ai_provider")
                provider_name = provider_setting.value if provider_setting else "gemini"

                if cls._instance and cls._provider_name == provider_name:
                    return cls._instance

                if provider_name == "gemini":
                    api_key_setting = await repo.get_by_key("ai_gemini_api_key")
                    model_setting = await repo.get_by_key("ai_gemini_model")
                    temp_setting = await repo.get_by_key("ai_temperature")
                    tokens_setting = await repo.get_by_key("ai_max_tokens")

                    api_key = api_key_setting.value if api_key_setting else ""
                    if not api_key:
                        raise ValueError("Gemini API key not configured")

                    cls._instance = GeminiProvider(
                        api_key=api_key,
                        model=model_setting.value if model_setting else "gemini-1.5-flash",
                        temperature=float(temp_setting.value) if temp_setting else 0.1,
                        max_tokens=int(tokens_setting.value) if tokens_setting else 4096,
                    )
                elif provider_name == "openai":
                    api_key_setting = await repo.get_by_key("ai_openai_api_key")
                    model_setting = await repo.get_by_key("ai_openai_model")
                    temp_setting = await repo.get_by_key("ai_temperature")
                    tokens_setting = await repo.get_by_key("ai_max_tokens")

                    api_key = api_key_setting.value if api_key_setting else ""
                    if not api_key:
                        raise ValueError("OpenAI API key not configured")

                    cls._instance = OpenAIProvider(
                        api_key=api_key,
                        model=model_setting.value if model_setting else "gpt-4",
                        temperature=float(temp_setting.value) if temp_setting else 0.1,
                        max_tokens=int(tokens_setting.value) if tokens_setting else 4096,
                    )
                elif provider_name == "ollama":
                    url_setting = await repo.get_by_key("ai_ollama_url")
                    model_setting = await repo.get_by_key("ai_ollama_model")
                    temp_setting = await repo.get_by_key("ai_temperature")
                    tokens_setting = await repo.get_by_key("ai_max_tokens")

                    cls._instance = OllamaProvider(
                        base_url=url_setting.value if url_setting else "http://localhost:11434",
                        model=model_setting.value if model_setting else "llama2",
                        temperature=float(temp_setting.value) if temp_setting else 0.1,
                        max_tokens=int(tokens_setting.value) if tokens_setting else 4096,
                    )
                else:
                    raise ValueError(f"Unknown AI provider: {provider_name}")

                cls._provider_name = provider_name
                logger.info("AI provider initialized: %s", provider_name)
                return cls._instance

        except Exception as e:
            logger.warning("Failed to load AI provider from settings, using default Gemini: %s", e)
            return GeminiProvider(api_key="", model="gemini-1.5-flash")

    @classmethod
    def invalidate(cls):
        cls._instance = None
        cls._provider_name = None
