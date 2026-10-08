from abc import ABC, abstractmethod

import httpx

from sentinelia.config import Settings
from sentinelia.models import Source


class LLMProvider(ABC):
    @abstractmethod
    async def answer(self, question: str, sources: list[Source]) -> str: ...


def build_prompt(question: str, sources: list[Source]) -> str:
    context = "\n\n".join(
        f"[{index}] {source.filename}, page {source.page or 'n/a'}\n{source.excerpt}"
        for index, source in enumerate(sources, 1)
    )
    return (
        "Réponds uniquement à partir des sources. Cite chaque affirmation avec [n]. "
        "Si elles ne suffisent pas, dis-le explicitement.\n\n"
        f"Sources:\n{context}\n\nQuestion: {question}"
    )


class OllamaProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def answer(self, question: str, sources: list[Source]) -> str:
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/api/generate",
                json={
                    "model": self.settings.llm_model,
                    "prompt": build_prompt(question, sources),
                    "stream": False,
                },
            )
            response.raise_for_status()
            return response.json()["response"]


class OpenAICompatibleProvider(LLMProvider):
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def answer(self, question: str, sources: list[Source]) -> str:
        headers = {"Authorization": f"Bearer {self.settings.llm_api_key}"}
        async with httpx.AsyncClient(timeout=60) as client:
            response = await client.post(
                f"{self.settings.llm_base_url.rstrip('/')}/v1/chat/completions",
                headers=headers,
                json={
                    "model": self.settings.llm_model,
                    "messages": [
                        {"role": "user", "content": build_prompt(question, sources)}
                    ],
                    "temperature": 0,
                },
            )
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]


class MockProvider(LLMProvider):
    async def answer(self, question: str, sources: list[Source]) -> str:
        del question
        return " ".join(f"{source.excerpt} [{index}]" for index, source in enumerate(sources, 1))


def create_provider(settings: Settings) -> LLMProvider:
    if settings.llm_provider == "ollama":
        return OllamaProvider(settings)
    if settings.llm_provider == "openai_compatible":
        return OpenAICompatibleProvider(settings)
    return MockProvider()
