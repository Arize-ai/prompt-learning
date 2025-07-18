"""
Prompt Learning SDK for Arize Toolkit

This module provides tools for automatically optimizing prompts using meta-prompt techniques.
Requires the 'prompt_optimizer' optional dependency to be installed.
"""

try:
    from arize_toolkit.extensions.prompt_optimizer.prompt_learning_optimizer import PromptLearningOptimizer
    from arize_toolkit.extensions.prompt_optimizer.tiktoken_splitter import TiktokenSplitter

    __all__ = [
        "TiktokenSplitter",
        "PromptLearningOptimizer",
    ]
except ImportError as e:
    # If optional dependencies are not installed, provide helpful error message
    raise ImportError("The prompt learning functionality requires the 'prompt_optimizer' optional dependency." "Install it with: pip install arize_toolkit[prompt_optimizer]") from e
