"""
Cohere provider implementation
"""

import os
from typing import List, Optional
import cohere
from .base import BaseProvider, CompletionResult, TokenLogProb


class CohereProvider(BaseProvider):
    """Cohere API provider"""

    SUPPORTED_MODELS = {
        "command",
        "command-light",
        "command-nightly",
        "command-r",
        "command-r-plus",
    }

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        self.client = cohere.AsyncClient(
            api_key=api_key or os.environ.get("COHERE_API_KEY"),
            base_url=base_url,
        )

    def get_max_k(self) -> int:
        """Cohere supports up to 100 completions"""
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
        Generate k completions using Cohere API

        Cohere approach:
        - Use num_generations parameter for k completions
        - Request likelihood for log probabilities
        - Extract token-level likelihoods if requested
        """
        if k > self.get_max_k():
            raise ValueError(f"k exceeds maximum of {self.get_max_k()} for Cohere")

        # Build request parameters
        params = {
            "model": model,
            "prompt": prompt,
            "num_generations": k,
            "temperature": temperature,
            "return_likelihoods": "ALL" if include_token_probabilities else "GENERATION",
        }

        if seed is not None:
            params["seed"] = seed

        # Make API call
        response = await self.client.generate(**params)

        # Extract completions with log probabilities
        results = []
        for generation in response.generations:
            text = generation.text

            # Calculate log probability from likelihoods
            import math

            logprob = 0.0
            token_logprobs = []

            if hasattr(generation, "likelihood") and generation.likelihood is not None:
                # Cohere provides likelihood (not log-likelihood), so convert
                logprob = math.log(max(generation.likelihood, 1e-10))

            # Extract token-level likelihoods if available
            if include_token_probabilities and hasattr(generation, "token_likelihoods"):
                if generation.token_likelihoods:
                    for token_data in generation.token_likelihoods:
                        likelihood = token_data.likelihood
                        token_logprobs.append(
                            TokenLogProb(
                                token=token_data.token,
                                logprob=math.log(max(likelihood, 1e-10)),
                                prob=likelihood,
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
