"""
Google AI provider with Gemini models and grounding support.
"""

import os
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types

from .base_provider import ModelProvider, ModelCapabilities
from core.exceptions import ProviderError

class GoogleProvider(ModelProvider):
    """Google AI provider using Gemini models with grounding."""
    
    def __init__(self, api_key: Optional[str] = None, **kwargs: Any) -> None:
        super().__init__(api_key, **kwargs)
        
        # Initialize Google AI
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ProviderError("Google API key required. Set GOOGLE_API_KEY or GEMINI_API_KEY environment variable.")
        
        self.client = genai.Client(api_key=api_key)
        
        # Default model
        self.default_model: str = kwargs.get("model", "gemini-2.5-flash")
        
        # Model capabilities mapping
        self._model_capabilities: Dict[str, ModelCapabilities] = {
            "gemini-2.5-flash": ModelCapabilities(
                supports_text=True,
                supports_images=False,
                supports_grounding=True,
                max_tokens=128000
            ),
            "gemini-2.5-pro": ModelCapabilities(
                supports_text=True,
                supports_images=False, 
                supports_grounding=True,
                max_tokens=128000
            ),
            "gemini-2.5-flash-image": ModelCapabilities(
                supports_text=True,
                supports_images=True,
                supports_grounding=False,
                max_tokens=128000
            )
        }
    
    def list_available_models(self) -> List[str]:
        """List available Gemini models."""
        return list(self._model_capabilities.keys())
    
    def get_model_capabilities(self, model: str) -> ModelCapabilities:
        """Get capabilities for a Gemini model."""
        return self._model_capabilities.get(model, ModelCapabilities())
    
    async def generate_text(self, messages: List[Dict[str, str]], model: str, **kwargs) -> str:
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
    
    async def generate_with_grounding(self, messages: List[Dict[str, str]], model: str, **kwargs: Any) -> str:
        """Generate response with Google Search grounding."""
        
        model_name = model or self.default_model
        
        try:
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
        except Exception as e:
            raise ProviderError(f"Google grounding generation failed: {e}")
    
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
    
    def generate_image(self, prompt: str, model: str = "gemini-2.5-flash-image", save_path: Optional[str] = None) -> str:
        """Generate image using Gemini image models (nano banana)."""
        
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=prompt
            )
            
            generated_images = []
            
            for part in response.parts:
                if part.text is not None:
                    print(f"Model response: {part.text}")
                elif part.inline_data is not None:
                    image = part.as_image()
                    
                    if save_path:
                        # Generate unique filename if multiple images
                        if len(generated_images) > 0:
                            name, ext = save_path.rsplit('.', 1)
                            unique_path = f"{name}_{len(generated_images)}.{ext}"
                        else:
                            unique_path = save_path
                            
                        image.save(unique_path)
                        generated_images.append(unique_path)
                        print(f"Image saved to: {unique_path}")
                    else:
                        generated_images.append(image)
            
            return f"Generated {len(generated_images)} image(s)"
            
        except Exception as e:
            return f"Error generating image: {e}"