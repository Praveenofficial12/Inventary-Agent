import os
import logging
from abc import ABC, abstractmethod
from typing import Any
from app.config import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    @abstractmethod
    def get_llm(self, **kwargs) -> Any:
        pass

class OpenAIProvider(LLMProvider):
    def get_llm(self, **kwargs) -> Any:
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            api_key=settings.OPENAI_API_KEY,
            model=kwargs.get("model", "gpt-4-turbo-preview"),
            temperature=kwargs.get("temperature", 0)
        )

class GeminiProvider(LLMProvider):
    def get_llm(self, **kwargs) -> Any:
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            google_api_key=settings.GEMINI_API_KEY,
            model=kwargs.get("model", "gemini-1.5-pro"),
            temperature=kwargs.get("temperature", 0)
        )

class GroqProvider(LLMProvider):
    def get_llm(self, **kwargs) -> Any:
        from langchain_groq import ChatGroq
        return ChatGroq(
            api_key=settings.GROQ_API_KEY,
            model=kwargs.get("model", "llama-3.3-70b-versatile"),
            temperature=kwargs.get("temperature", 0)
        )

def get_llm_provider(provider_name: str = None) -> Any:
    name = provider_name or settings.LLM_PROVIDER
    
    if name == "openai":
        if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY in ("", "sk-placeholder"):
            raise ValueError("OPENAI_API_KEY is not configured")
        return OpenAIProvider().get_llm()
    elif name == "gemini":
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "":
            raise ValueError("GEMINI_API_KEY is not configured")
        return GeminiProvider().get_llm()
    elif name == "groq":
        if not settings.GROQ_API_KEY or settings.GROQ_API_KEY == "":
            raise ValueError("GROQ_API_KEY is not configured")
        return GroqProvider().get_llm()
    else:
        raise ValueError(f"Unsupported LLM provider: {name}")
