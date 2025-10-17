"""
Anthropic provider implementation
"""

import os
from typing import List, Optional
import anthropic
from .base import BaseProvider, CompletionResult, TokenLogProb


class AnthropicProvider(BaseProvider):
    """Anthropic API provider for Claude models"""

    SUPPORTED_MODELS = {
        "claude-3-opus",
        "claude-3-sonnet",
        "claude-3-haiku",
        "claude-2.1",
        "claude-2.0",
    }

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = anthropic.AsyncAnthropic(
            api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"),
            base_url=base_url,
        )

    def get_max_k(self) -> int:
        """Anthropic supports up to 100 completions"""
        return 100

    def validate_model(self, model: str) -> bool:
        """Check if model is supported"""
        return any(model.startswith(m) for m in self.SUPPORTED_MODELS)

    async def generate_completions(
        self,
        prompt: str,
        model: str,
        k: int,
        temperature: float,
        seed: Optional[int] = None,
        include_token_probabilities: bool = False,
    ) -> List[CompletionResult]:
        """
        Generate k completions using Anthropic API

        Anthropic approach:
        - Claude API doesn't natively support n>1 or log probabilities
        - Generate k completions sequentially
        - Estimate log probabilities from response metadata (if available)
        - For now, use uniform log probs (will be normalized later)
        """
        if k > self.get_max_k():
            raise ValueError(f"k exceeds maximum of {self.get_max_k()} for Anthropic")

        results = []

        # Generate k completions sequentially
        # Note: Anthropic doesn't support batch completions, so we make k requests
        for i in range(k):
            params = {
                "model": model,
                "max_tokens": 1024,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }

            # Anthropic doesn't support seed parameter currently
            # We'll use the same seed conceptually but can't enforce it

            response = await self.client.messages.create(**params)

            # Extract text
            text = ""
            if response.content:
                text = "".join(
                    block.text for block in response.content if hasattr(block, "text")
                )

            # Anthropic doesn't provide log probabilities directly
            # Use uniform log probability (will be normalized in post-processing)
            # This is a limitation of the Anthropic API
            logprob = 0.0  # Uniform (will normalize to 1/k probability)

            results.append(
                CompletionResult(
                    text=text,
                    logprob=logprob,
                    token_logprobs=None,  # Anthropic doesn't provide token-level probs
                )
            )

        return results
