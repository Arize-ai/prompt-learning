"""
Base provider interface for LLM integrations
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class TokenLogProb:
    """Token-level log probability information"""
    token: str
    logprob: float
    prob: float  # exp(logprob)


@dataclass
class CompletionResult:
    """Single completion result from LLM"""
    text: str
    logprob: float  # Total log probability for this completion
    token_logprobs: Optional[List[TokenLogProb]] = None


class BaseProvider(ABC):
    """Abstract base class for LLM providers"""

    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None):
        self.api_key = api_key
        self.base_url = base_url

    @abstractmethod
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
        Generate k completions with log probabilities

        Args:
            prompt: Input text prompt
            model: Model identifier
            k: Number of completions to generate
            temperature: Sampling temperature
            seed: Random seed for deterministic sampling
            include_token_probabilities: Include token-level log probs

        Returns:
            List of CompletionResult objects with log probabilities
        """
        pass

    @abstractmethod
    def get_max_k(self) -> int:
        """Get maximum k value supported by this provider"""
        pass

    @abstractmethod
    def validate_model(self, model: str) -> bool:
        """Validate if model is supported by this provider"""
        pass

    def _normalize_probabilities(
        self, results: List[CompletionResult], tau: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Normalize log probabilities to probability distribution with temperature scaling

        Args:
            results: List of CompletionResult objects
            tau: Temperature scaling parameter for probability sharpening/smoothing

        Returns:
            List of dicts with text, probability, and optional token_probabilities
        """
        import math

        # Apply temperature scaling to log probabilities
        scaled_logprobs = [r.logprob / tau for r in results]

        # Compute log-sum-exp for numerical stability
        max_logprob = max(scaled_logprobs)
        log_sum = max_logprob + math.log(
            sum(math.exp(lp - max_logprob) for lp in scaled_logprobs)
        )

        # Normalize to probabilities
        normalized = []
        for i, result in enumerate(results):
            prob = math.exp(scaled_logprobs[i] - log_sum)

            completion_dict = {
                "text": result.text,
                "probability": prob,
            }

            # Include token probabilities if available
            if result.token_logprobs:
                completion_dict["token_probabilities"] = [
                    {"token": tlp.token, "prob": tlp.prob}
                    for tlp in result.token_logprobs
                ]

            normalized.append(completion_dict)

        # Sort by probability descending and add rank
        normalized.sort(key=lambda x: x["probability"], reverse=True)
        for rank, item in enumerate(normalized, start=1):
            item["rank"] = rank

        return normalized
