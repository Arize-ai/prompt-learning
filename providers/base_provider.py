"""
Base provider interface for model integrations.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseProvider(ABC):
    """Base class for model providers."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
    
    @abstractmethod
    async def generate(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from messages."""
        pass
    
    @abstractmethod
    async def generate_with_grounding(self, messages: List[Dict[str, str]], query: str, **kwargs) -> str:
        """Generate response with grounding/search."""
        pass
    
    @property
    @abstractmethod
    def supported_models(self) -> List[str]:
        """List of supported model names."""
        pass