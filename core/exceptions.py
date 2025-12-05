"""
Custom exceptions for prompt learning system.
"""


class PromptLearningError(Exception):
    """Base exception for prompt learning operations."""
    pass


class DatasetError(PromptLearningError):
    """Dataset loading or validation errors."""
    pass


class TokenLimitError(PromptLearningError):
    """Token counting or limit errors."""
    pass


class ProviderError(PromptLearningError):
    """Model provider errors."""
    pass


class OptimizationError(PromptLearningError):
    """Prompt optimization errors."""
    pass


class ConfigurationError(PromptLearningError):
    """Configuration or setup errors."""
    pass