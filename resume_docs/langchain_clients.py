"""LangChain-based LLM clients for content polishing."""
from __future__ import annotations

import os
from abc import ABC, abstractmethod
from typing import Optional


class LangChainLLMClient(ABC):
    """Base class for LangChain LLM clients."""

    @abstractmethod
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt and return the response."""
        pass


class OpenAILangChainClient(LangChainLLMClient):
    """OpenAI LLM client using LangChain."""

    def __init__(self, model: str = "gpt-4o"):
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable not set")

        self.client = ChatOpenAI(
            model=model,
            api_key=api_key,
            temperature=0.7,
        )

    def invoke(self, prompt: str) -> str:
        """Invoke OpenAI model."""
        response = self.client.invoke(prompt)
        content = response.content
        # Remove <think> tags and reasoning from extended thinking models
        content = self._remove_think_tags(content)
        return content

    def _remove_think_tags(self, text: str) -> str:
        """Remove <think>...</think> tags from text."""
        import re
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


class ZhipuLangChainClient(LangChainLLMClient):
    """Zhipu GLM LLM client using LangChain."""

    def __init__(self, model: str = "glm-4"):
        from langchain_community.chat_models import ChatZhipuAI

        api_key = os.getenv("ZHIPU_API_KEY")
        if not api_key:
            raise ValueError("ZHIPU_API_KEY environment variable not set")

        self.client = ChatZhipuAI(
            model=model,
            api_key=api_key,
            temperature=0.7,
        )

    def invoke(self, prompt: str) -> str:
        """Invoke Zhipu GLM model."""
        response = self.client.invoke(prompt)
        content = response.content
        # Remove <think> tags and reasoning from extended thinking models
        content = self._remove_think_tags(content)
        return content

    def _remove_think_tags(self, text: str) -> str:
        """Remove <think>...</think> tags from text."""
        import re
        return re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL).strip()


class OllamaLangChainClient(LangChainLLMClient):
    """Ollama LLM client using LangChain."""

    def __init__(self, model: str = "llama2"):
        from langchain_community.llms import Ollama

        host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = Ollama(
            model=model,
            base_url=host,
        )

    def invoke(self, prompt: str) -> str:
        """Invoke Ollama model."""
        response = self.client.invoke(prompt)
        return response


def get_llm_client(model_name: str) -> LangChainLLMClient:
    """Get appropriate LLM client based on model name."""
    model_lower = model_name.lower()

    if "gpt" in model_lower or "o1" in model_lower or "o4" in model_lower:
        return OpenAILangChainClient(model=model_name)
    elif "glm" in model_lower or "spark" in model_lower:
        return ZhipuLangChainClient(model=model_name)
    elif "ollama" in model_lower or "qwen" in model_lower or "mixtral" in model_lower:
        return OllamaLangChainClient(model=model_name)
    else:
        raise ValueError(f"Unknown model: {model_name}")
