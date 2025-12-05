"""
Clean configuration management with validation.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TokenLimits:
    """Token limit configuration."""

    default_context_size: int = 128000
    batch_size_tokens: int = 32000
    safety_margin: int = 1000


@dataclass
class ProviderConfig:
    """Provider-specific configuration."""

    name: str
    api_key_env_var: str
    default_model: str
    timeout_seconds: int = 60
    max_retries: int = 3


@dataclass
class Settings:
    """Main application settings."""

    # Token limits
    token_limits: TokenLimits = field(default_factory=TokenLimits)

    # Provider configurations
    providers: Dict[str, ProviderConfig] = field(
        default_factory=lambda: {
            "google": ProviderConfig(
                name="google",
                api_key_env_var="GEMINI_API_KEY",
                default_model="gemini-2.5-flash",
            ),
            "openai": ProviderConfig(
                name="openai", api_key_env_var="OPENAI_API_KEY", default_model="gpt-4"
            ),
        }
    )

    # File paths
    output_dir: Path = Path("./outputs")
    temp_dir: Path = Path("./temp")

    # Optimization settings
    optimization_threshold: float = 4.0
    max_optimization_iterations: int = 3

    @classmethod
    def load_from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        settings = cls()

        # Override with env vars if present
        if context_size := os.getenv("PROMPT_LEARNING_CONTEXT_SIZE"):
            settings.token_limits.default_context_size = int(context_size)

        if output_dir := os.getenv("PROMPT_LEARNING_OUTPUT_DIR"):
            settings.output_dir = Path(output_dir)

        if threshold := os.getenv("PROMPT_LEARNING_OPTIMIZATION_THRESHOLD"):
            settings.optimization_threshold = float(threshold)

        return settings

    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)

    def get_api_key(self, provider_name: str) -> Optional[str]:
        """Get API key for a provider from environment."""
        config = self.get_provider_config(provider_name)
        if not config:
            return None

        return os.getenv(config.api_key_env_var)


# Global settings instance
settings = Settings.load_from_env()
