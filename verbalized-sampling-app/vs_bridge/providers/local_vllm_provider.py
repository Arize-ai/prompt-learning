"""
Local vLLM provider implementation for self-hosted models
"""

import os
from typing import List, Optional
import httpx
from .base import BaseProvider, CompletionResult, TokenLogProb


class LocalVLLMProvider(BaseProvider):
    """Local vLLM server provider for self-hosted models"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        super().__init__(api_key, base_url)
        # Default to local vLLM server
        self.base_url = base_url or os.environ.get(
            "VLLM_BASE_URL", "http://localhost:8000"
        )

    def get_max_k(self) -> int:
        """Local vLLM supports up to 500 completions"""
        return 500

    def validate_model(self, model: str) -> bool:
        """
        For local vLLM, we accept any model name
        Validation happens at runtime when connecting to server
        """
        return len(model) > 0

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
        Generate k completions using local vLLM server

        vLLM approach:
        - Use OpenAI-compatible API with n=k
        - Request logprobs for probability calculation
        - vLLM provides full log probability support
        """
        if k > self.get_max_k():
            raise ValueError(f"k exceeds maximum of {self.get_max_k()} for vLLM")

        # Build OpenAI-compatible request
        request_data = {
            "model": model,
            "prompt": prompt,
            "n": k,
            "temperature": temperature,
            "logprobs": 5 if include_token_probabilities else 1,
            "max_tokens": 1024,
        }

        if seed is not None:
            request_data["seed"] = seed

        # Make request to vLLM server
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.base_url}/v1/completions",
                    json=request_data,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                data = response.json()
            except httpx.ConnectError:
                raise ConnectionError(
                    f"Failed to connect to vLLM server at {self.base_url}. "
                    "Ensure vLLM is running and accessible."
                )
            except httpx.HTTPError as e:
                raise ValueError(f"vLLM API error: {str(e)}")

        # Extract completions with log probabilities
        results = []
        for choice in data.get("choices", []):
            text = choice.get("text", "")

            # Calculate total log probability
            logprob = 0.0
            token_logprobs = []

            if "logprobs" in choice and choice["logprobs"]:
                logprobs_data = choice["logprobs"]

                # Sum token log probabilities
                if "token_logprobs" in logprobs_data:
                    for token_lp in logprobs_data["token_logprobs"]:
                        if token_lp is not None:
                            logprob += token_lp

                # Extract token-level data if requested
                if include_token_probabilities:
                    import math

                    tokens = logprobs_data.get("tokens", [])
                    token_lps = logprobs_data.get("token_logprobs", [])

                    for token, lp in zip(tokens, token_lps):
                        if lp is not None:
                            token_logprobs.append(
                                TokenLogProb(
                                    token=token, logprob=lp, prob=math.exp(lp)
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
