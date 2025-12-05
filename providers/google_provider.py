"""
Google AI provider with Gemini models and grounding support.
"""

import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from .base_provider import BaseProvider

class GoogleProvider(BaseProvider):
    """Google AI provider using Gemini models with grounding."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        
        # Initialize Google AI
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("Google API key required. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=api_key)
        
        # Default model
        self.default_model = kwargs.get("model", "gemini-2.5-flash")
        
    @property
    def supported_models(self) -> List[str]:
        """Let Google's library handle model validation."""
        return []  # Will let genai library validate models
    
    async def generate(self, messages: List[Dict[str, str]], model: Optional[str] = None, **kwargs) -> str:
        """Generate response using Gemini."""
        
        model_name = model or self.default_model
        
        # Convert messages to Gemini format
        prompt_text = self._format_messages(messages)
        
        # Generate response
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt_text
        )
        
        return response.text
    
    async def generate_with_grounding(self, messages: List[Dict[str, str]], query: str, model: Optional[str] = None, **kwargs) -> str:
        """Generate response with Google Search grounding."""
        
        model_name = model or self.default_model
        
        # Configure Google Search tool
        grounding_tool = types.Tool(
            google_search=types.GoogleSearch()
        )
        
        config = types.GenerateContentConfig(
            tools=[grounding_tool]
        )
        
        # Convert messages to Gemini format
        prompt_text = self._format_messages(messages)
        
        # Generate response with grounding
        response = self.client.models.generate_content(
            model=model_name,
            contents=prompt_text,
            config=config,
        )
        
        return response.text
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> str:
        """Convert OpenAI-style messages to Gemini prompt format."""
        
        formatted_parts = []
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                formatted_parts.append(f"System: {content}")
            elif role == "user":
                formatted_parts.append(f"User: {content}")
            elif role == "assistant":
                formatted_parts.append(f"Assistant: {content}")
        
        return "\n\n".join(formatted_parts)