"""
Token pricing calculator for different AI providers.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class ModelPricing:
    """Pricing information for a model."""
    input_price_per_1k: float  # Price per 1K input tokens
    output_price_per_1k: float  # Price per 1K output tokens
    model_name: str


class PricingCalculator:
    """Calculate costs for different AI models."""
    
    # Pricing data (prices per 1K tokens) - based on current industry rates
    MODEL_PRICING: Dict[str, ModelPricing] = {
        # OpenAI models (approximate current pricing)
        "gpt-4": ModelPricing(0.03, 0.06, "gpt-4"),
        "gpt-4-turbo": ModelPricing(0.01, 0.03, "gpt-4-turbo"),
        "gpt-3.5-turbo": ModelPricing(0.0015, 0.002, "gpt-3.5-turbo"),
        
        # Google Gemini models (from Google AI pricing)
        "gemini-2.5-flash": ModelPricing(0.0003, 0.0025, "gemini-2.5-flash"),
        "gemini-2.5-pro": ModelPricing(0.00125, 0.01, "gemini-2.5-pro"),
        "gemini-pro": ModelPricing(0.00125, 0.01, "gemini-pro"),
        
        # Fallback for unknown models (conservative estimate)
        "unknown": ModelPricing(0.01, 0.03, "unknown"),
    }
    
    def __init__(self):
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def get_model_pricing(self, model: str) -> ModelPricing:
        """Get pricing info for a model."""
        # Try exact match first
        if model in self.MODEL_PRICING:
            return self.MODEL_PRICING[model]
        
        # Try partial matches for model families
        model_lower = model.lower()
        for model_key, pricing in self.MODEL_PRICING.items():
            if model_key in model_lower or any(part in model_lower for part in model_key.split("-")):
                return pricing
        
        # Return fallback pricing
        return self.MODEL_PRICING["unknown"]
    
    def calculate_cost(self, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Calculate cost for a model given token usage."""
        pricing = self.get_model_pricing(model)
        
        input_cost = (input_tokens / 1000) * pricing.input_price_per_1k
        output_cost = (output_tokens / 1000) * pricing.output_price_per_1k
        
        return input_cost + output_cost
    
    def add_usage(self, model: str, input_tokens: int, output_tokens: int = 0) -> float:
        """Add usage and return the cost for this call."""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self.total_cost += cost
        self.total_input_tokens += input_tokens
        self.total_output_tokens += output_tokens
        return cost
    
    def get_total_cost(self) -> float:
        """Get total accumulated cost."""
        return self.total_cost
    
    def would_exceed_budget(self, model: str, input_tokens: int, output_tokens: int, budget_limit: float) -> bool:
        """Check if adding this usage would exceed budget."""
        additional_cost = self.calculate_cost(model, input_tokens, output_tokens)
        return (self.total_cost + additional_cost) > budget_limit
    
    def reset(self) -> None:
        """Reset cost tracking."""
        self.total_cost = 0.0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
    
    def get_usage_summary(self) -> Dict[str, float]:
        """Get usage summary."""
        return {
            "total_cost": self.total_cost,
            "total_input_tokens": self.total_input_tokens,
            "total_output_tokens": self.total_output_tokens,
            "total_tokens": self.total_input_tokens + self.total_output_tokens
        }