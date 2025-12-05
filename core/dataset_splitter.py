"""
Clean dataset splitter with dependency injection.
"""

from typing import List
import pandas as pd

from interfaces.token_counter import TokenCounter


class DatasetSplitter:
    """Split datasets into batches based on token limits."""
    
    def __init__(self, token_counter: TokenCounter):
        """Initialize with a token counter dependency."""
        self.token_counter = token_counter
    
    def split_into_batches(
        self, 
        df: pd.DataFrame, 
        columns: List[str], 
        max_tokens: int
    ) -> List[pd.DataFrame]:
        """
        Split dataframe into batches that fit within token limit.
        
        Args:
            df: DataFrame to split
            columns: Column names to count tokens for
            max_tokens: Maximum tokens per batch
            
        Returns:
            List of DataFrame batches
        """
        if df.empty:
            return []
        
        # Count tokens for each row
        row_token_counts = self.token_counter.count_dataframe_tokens(df, columns)
        
        # Pre-calculate batch boundaries to minimize DataFrame operations
        batch_boundaries = []
        current_batch_start = 0
        current_batch_tokens = 0
        
        for idx, token_count in enumerate(row_token_counts):
            # If adding this row would exceed limit, finalize current batch
            if current_batch_tokens + token_count > max_tokens and idx > current_batch_start:
                batch_boundaries.append((current_batch_start, idx))
                current_batch_start = idx
                current_batch_tokens = token_count
            else:
                current_batch_tokens += token_count
        
        # Add final batch boundary
        if current_batch_start < len(df):
            batch_boundaries.append((current_batch_start, len(df)))
        
        # Create DataFrame slices efficiently using boundaries
        batches = []
        for start_idx, end_idx in batch_boundaries:
            # Use iloc with slice for better performance than index lists
            batch_df = df.iloc[start_idx:end_idx].copy()
            batches.append(batch_df)
        
        return batches
    
    def estimate_batch_count(self, df: pd.DataFrame, columns: List[str], max_tokens: int) -> int:
        """Quickly estimate how many batches will be needed."""
        if df.empty:
            return 0
        
        # Use fast estimation
        total_tokens = sum(
            self.token_counter.estimate_tokens(str(df[col].sum())) 
            for col in columns if col in df.columns
        )
        
        return max(1, (total_tokens + max_tokens - 1) // max_tokens)  # Ceiling division