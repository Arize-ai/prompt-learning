"""
prompt-learning: A prompt optimization SDK using meta-prompt approaches.

This package provides tools for optimizing LLM prompts using feedback
and evaluation data.
"""

from .prompt_learning_optimizer import PromptLearningOptimizer
from .annotator import Annotator
from .meta_prompt import MetaPrompt
from .tiktoken_splitter import TiktokenSplitter

__version__ = "0.1.0"

__all__ = [
    "PromptLearningOptimizer",
    "Annotator",
    "MetaPrompt",
    "TiktokenSplitter",
]
