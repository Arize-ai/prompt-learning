"""
OpenAI provider implementation
"""

import os
from typing import List, Optional
import openai
from .base import BaseProvider, CompletionResult, TokenLogProb


class OpenAIProvider(BaseProvider):
    """OpenAI API provider for GPT models"""

    SUPPORTED_MODELS = {
        "gpt-4",
        "gpt-4-turbo",
        "gpt-4-turbo-preview",
        "gpt-3.5-turbo",
        "gpt-3.5-turbo-16k",
    }

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = openai.AsyncOpenAI(
            api_key=api_key or os.environ.get("OPENAI_API_KEY"),
            base_url=base_url,
        )

    def get_max_k(self) -> int:
        """OpenAI supports up to 100 completions"""
        return 100

    def validate_model(self, model: str) -> bool:
        """Check if model is supported"""
        # Support both exact matches and prefix matches
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
        Generate k completions using OpenAI API with log probabilities

        OpenAI approach:
        1. Generate k completions with n=k parameter
        2. Request logprobs for probability calculation
        3. Extract log probabilities from response
        """
        # Validate k
        if k > self.get_max_k():
            raise ValueError(f"k exceeds maximum of {self.get_max_k()} for OpenAI")

        # Build request parameters
        params = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "n": k,
            "temperature": temperature,
            "logprobs": True,  # Request log probabilities
            "top_logprobs": 5 if include_token_probabilities else None,
        }

        if seed is not None:
            params["seed"] = seed

        # Make API call
        response = await self.client.chat.completions.create(**params)

        # Extract completions with log probabilities
        results = []
        for choice in response.choices:
            text = choice.message.content or ""

            # Calculate total log probability
            logprob = 0.0
            token_logprobs = []

            if choice.logprobs and choice.logprobs.content:
                for token_data in choice.logprobs.content:
                    logprob += token_data.logprob

                    if include_token_probabilities:
                        import math

                        token_logprobs.append(
                            TokenLogProb(
                                token=token_data.token,
                                logprob=token_data.logprob,
                                prob=math.exp(token_data.logprob),
                            )
                        )

            results.append(
                CompletionResult(
                    text=text,
                    logprob=logprob,
                    token_logprobs=token_logprobs if include_token_probabilities else None,
                )
            )

        return results
