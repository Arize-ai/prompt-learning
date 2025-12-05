"""
Base provider interface for model integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModelCapabilities:
    """Describes what a model can do."""
    supports_text: bool = True
    supports_images: bool = False
    supports_grounding: bool = False
    max_tokens: Optional[int] = None
    cost_per_1k_tokens: Optional[float] = None


class ModelProvider(ABC):
    """Clean provider interface with explicit capabilities."""
    
    def __init__(self, api_key: Optional[str] = None, **config):
        self.api_key = api_key
        self.config = config
    
    @abstractmethod
    async def generate_text(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> str:
        """Generate text response."""
        pass
    
    @abstractmethod
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for a specific model."""
        pass
    
    @abstractmethod
    def list_available_models(self) -> List[str]:
        """List all available models for this provider."""
        pass
    
    async def generate_with_grounding(
        self, 
        messages: List[Dict[str, str]], 
        model: str,
        **kwargs
    ) -> str:
        """Generate with grounding if supported."""
        capabilities = self.get_model_capabilities(model)
        if not capabilities.supports_grounding:
            raise ValueError(f"Model {model} does not support grounding")
        
        # Default implementation - subclasses should override
        return await self.generate_text(messages, model, **kwargs)