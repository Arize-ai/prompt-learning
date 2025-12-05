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
        token_counts = []
        
        for _, row in df.iterrows():
            total_tokens = 0
            for col in columns:
                if col in row:
                    total_tokens += self.count_tokens(row[col])
            token_counts.append(total_tokens)
        
        return token_counts
    
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
        token_counts = []
        
        for _, row in df.iterrows():
            total_chars = 0
            for col in columns:
                if col in row:
                    total_chars += len(str(row[col]))
            token_counts.append(total_chars // 4)
        
        return token_counts
    
    def estimate_tokens(self, text: str) -> int:
        """Same as count_tokens for approximate counter."""
        return self.count_tokens(text)