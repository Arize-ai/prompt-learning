"""
Token counting interface - pure token counting without model validation.
"""

from abc import ABC, abstractmethod
from typing import List
import pandas as pd


class TokenCounter(ABC):
    """Abstract interface for counting tokens in text."""

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        """Count tokens in a single text string."""
        pass

    @abstractmethod
    def count_dataframe_tokens(self, df: pd.DataFrame, columns: List[str]) -> List[int]:
        """Count tokens for specified columns in a dataframe."""
        pass

    @abstractmethod
    def estimate_tokens(self, text: str) -> int:
        """Fast token estimation (can be less accurate)."""
        pass


class TiktokenCounter(TokenCounter):
    """OpenAI tiktoken-based token counter."""

    def __init__(self, encoding_name: str = "cl100k_base"):
        """Initialize with a specific tiktoken encoding."""
        import tiktoken

        self.encoder = tiktoken.get_encoding(encoding_name)

    def count_tokens(self, text: str) -> int:
        """Count tokens using tiktoken."""
        if pd.isna(text) or text == "":
            return 0
        return len(self.encoder.encode(str(text)))

    def count_dataframe_tokens(self, df: pd.DataFrame, columns: List[str]) -> List[int]:
        """Count tokens for specified columns in dataframe."""
        # Vectorized approach - much faster than iterrows()
        valid_columns = [col for col in columns if col in df.columns]

        if not valid_columns:
            return [0] * len(df)

        # Process each column and sum tokens per row
        token_counts = pd.Series([0] * len(df), dtype=int)

        for col in valid_columns:
            # Vectorized token counting for the entire column
            col_tokens = df[col].fillna("").astype(str).apply(self.count_tokens)
            token_counts += col_tokens

        return token_counts.tolist()

    def estimate_tokens(self, text: str) -> int:
        """For tiktoken, exact count is fast enough."""
        return self.count_tokens(text)


class ApproximateCounter(TokenCounter):
    """Fast approximate token counter (chars/4 rule)."""

    def count_tokens(self, text: str) -> int:
        """Approximate token count using character length."""
        if pd.isna(text) or text == "":
            return 0
        return len(str(text)) // 4  # Rough approximation

    def count_dataframe_tokens(self, df: pd.DataFrame, columns: List[str]) -> List[int]:
        """Count approximate tokens for dataframe columns."""
        # Vectorized approach using numpy for maximum speed
        valid_columns = [col for col in columns if col in df.columns]

        if not valid_columns:
            return [0] * len(df)

        # Convert columns to string lengths in a vectorized way
        total_chars = pd.Series([0] * len(df), dtype=int)

        for col in valid_columns:
            # Vectorized string length calculation
            char_counts = df[col].fillna("").astype(str).str.len()
            total_chars += char_counts

        # Convert to tokens (chars/4) and return as list
        return (total_chars // 4).tolist()

    def estimate_tokens(self, text: str) -> int:
        """Same as count_tokens for approximate counter."""
        return self.count_tokens(text)
