"""
Verbalize endpoint handler
"""

import uuid
from datetime import datetime
from typing import Dict, Any
from fastapi import HTTPException
import time

from ..models import (
    VerbRequest,
    VerbResponse,
    CompletionResponse,
    TraceMetadata,
    Provider,
)
from ..providers import (
    BaseProvider,
    OpenAIProvider,
    AnthropicProvider,
    CohereProvider,
    LocalVLLMProvider,
)


class VerbalizationService:
    """Service for handling verbalized sampling requests"""

    def __init__(self):
        # Store in-memory distributions for sampling
        # In production, use Redis or similar
        self.distributions: Dict[str, VerbResponse] = {}

    def _get_provider(self, request: VerbRequest) -> BaseProvider:
        """Get appropriate provider based on request"""
        providers = {
            Provider.OPENAI: OpenAIProvider,
            Provider.ANTHROPIC: AnthropicProvider,
            Provider.COHERE: CohereProvider,
            Provider.LOCAL_VLLM: LocalVLLMProvider,
        }

        provider_class = providers.get(request.provider)
        if not provider_class:
            raise HTTPException(
                status_code=400, detail=f"Unsupported provider: {request.provider}"
            )

        # Initialize provider
        # In production, API keys should come from secure storage
        provider = provider_class()

        # Validate model
        if not provider.validate_model(request.model):
            raise HTTPException(
                status_code=400,
                detail=f"Model {request.model} not supported by {request.provider}",
            )

        return provider

    async def verbalize(self, request: VerbRequest) -> VerbResponse:
        """
        Generate verbalized sampling distribution

        1. Validate request
        2. Get appropriate provider
        3. Generate k completions with log probabilities
        4. Apply temperature scaling (tau)
        5. Normalize to probability distribution
        6. Rank by probability
        7. Return VerbResponse
        """
        # Get provider
        provider = self._get_provider(request)

        # Validate k against provider limits
        max_k = provider.get_max_k()
        if request.k > max_k:
            raise HTTPException(
                status_code=400,
                detail=f"k={request.k} exceeds maximum of {max_k} for {request.provider}",
            )

        # Track API latency
        start_time = time.time()

        # Generate completions with log probabilities
        try:
            completion_results = await provider.generate_completions(
                prompt=request.prompt,
                model=request.model,
                k=request.k,
                temperature=request.temperature,
                seed=request.seed,
                include_token_probabilities=request.include_token_probabilities,
            )
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Provider error: {str(e)}"
            )

        # Calculate API latency
        api_latency_ms = (time.time() - start_time) * 1000

        # Normalize probabilities with tau scaling
        normalized = provider._normalize_probabilities(completion_results, tau=request.tau)

        # Convert to CompletionResponse models
        completions = []
        total_tokens = 0

        for item in normalized:
            # Create completion response
            completion = CompletionResponse(
                text=item["text"],
                probability=item["probability"],
                rank=item["rank"],
            )

            # Add token probabilities if included
            if "token_probabilities" in item:
                from ..models import TokenProbability

                completion.token_probabilities = [
                    TokenProbability(token=tp["token"], prob=tp["prob"])
                    for tp in item["token_probabilities"]
                ]
                total_tokens += len(completion.token_probabilities)

            completions.append(completion)

        # Generate distribution ID
        distribution_id = str(uuid.uuid4())

        # Create trace metadata
        trace_metadata = TraceMetadata(
            model=request.model,
            provider=request.provider.value,
            api_latency_ms=api_latency_ms,
            token_count=total_tokens,
            k=request.k,
            tau=request.tau,
            temperature=request.temperature,
            seed=request.seed,
        )

        # Create response
        response = VerbResponse(
            distribution_id=distribution_id,
            completions=completions,
            trace_metadata=trace_metadata,
            timestamp=datetime.now(),
        )

        # Store distribution for later sampling
        self.distributions[distribution_id] = response

        return response

    def get_distribution(self, distribution_id: str) -> VerbResponse:
        """Retrieve stored distribution by ID"""
        if distribution_id not in self.distributions:
            raise HTTPException(
                status_code=404, detail=f"Distribution {distribution_id} not found"
            )
        return self.distributions[distribution_id]


# Global service instance
verbalization_service = VerbalizationService()
