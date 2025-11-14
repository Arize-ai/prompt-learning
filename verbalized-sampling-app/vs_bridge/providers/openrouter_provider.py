"""
OpenRouter provider implementation
Uses OpenAI-compatible API with OpenRouter models
"""

import os
from typing import Optional
from .openai_provider import OpenAIProvider


class OpenRouterProvider(OpenAIProvider):
    """OpenRouter API provider - uses OpenAI-compatible interface"""

    # Popular OpenRouter models
    SUPPORTED_MODELS = {
        # Anthropic
        "anthropic/claude-3.5-sonnet",
        "anthropic/claude-3-opus",
        "anthropic/claude-3-sonnet",
        "anthropic/claude-3-haiku",
        # OpenAI
        "openai/gpt-4-turbo",
        "openai/gpt-4",
        "openai/gpt-3.5-turbo",
        # Google
        "google/gemini-pro",
        "google/gemini-pro-1.5",
        # Meta
        "meta-llama/llama-3.1-70b-instruct",
        "meta-llama/llama-3.1-405b-instruct",
        # Mistral
        "mistralai/mistral-large",
        "mistralai/mistral-medium",
        # Open source via OpenRouter
        "qwen/qwen-2-72b-instruct",
        "deepseek/deepseek-chat",
    }

    def __init__(self, api_key: Optional[str] = None):
        """Initialize OpenRouter provider with OpenRouter base URL"""
        # OpenRouter uses OpenAI-compatible API at this base URL
        super().__init__(
            api_key=api_key or os.environ.get("OPENROUTER_API_KEY"),
            base_url="https://openrouter.ai/api/v1"
        )

    def validate_model(self, model: str) -> bool:
        """Check if model is supported on OpenRouter"""
        # Support both exact matches and prefix matches
        # Also allow any model since OpenRouter has many models
        if any(model.startswith(m) for m in self.SUPPORTED_MODELS):
            return True
        # OpenRouter accepts model IDs not in our list, so be permissive
        return "/" in model  # OpenRouter models use org/model format

    def get_max_k(self) -> int:
        """OpenRouter supports up to 100 completions via n parameter"""
        return 100
