#!/usr/bin/env python3
"""
Tiktoken-based Dataframe Splitter

Uses tiktoken for accurate token counting to split dataframes into batches
that fit within LLM context windows.
"""
from typing import List, Tuple

import pandas as pd
import tiktoken

from arize_toolkit.extensions.prompt_optimizer.constants import SUPPORTED_MODELS


class TiktokenSplitter:
    """Split dataframes using tiktoken for accurate token counting.

    Args:
        model: The model to use for tokenization (default: gpt-4o)

    Methods:
        get_batch_dataframes: Generate batches of dataframes that fit within the context window

    Example:
    ```python
    from arize_toolkit.extensions.prompt_optimizer import TiktokenSplitter

    splitter = TiktokenSplitter()
    batches = splitter.get_batch_dataframes(
        df=pd.DataFrame({"text": ["Hello, world!", "This is a test", "Another example"]}),
        columns=["text"],
        context_size_tokens=10,
    )
    print(batches)
    ```
    """

    def __init__(self, model: str = "gpt-4o"):
        """
        Initialize splitter with tiktoken encoder.

        Args:
            model: The model to use for tokenization (default: gpt-4o)
        """
        if model not in SUPPORTED_MODELS:
            raise ValueError(f"Model {model} not supported. Supported models: {SUPPORTED_MODELS}")

        self.tiktoken_encoder = tiktoken.encoding_for_model(model)

    def _count_tokens(self, text: str) -> int:
        """Count tokens in text using tiktoken."""
        if pd.isna(text) or text == "":
            return 0

        text_str = str(text)
        return len(self.tiktoken_encoder.encode(text_str))

    def _count_row_tokens(self, df: pd.DataFrame, columns: List[str], row_idx: int) -> int:
        """Count total tokens for a specific row across selected columns."""
        row = df.iloc[row_idx]
        total_tokens = 0

        for col in columns:
            if col in df.columns:
                cell_value = row[col]
                total_tokens += self._count_tokens(str(cell_value))

        return total_tokens

    def _create_batches(
        self,
        df: pd.DataFrame,
        columns: List[str],
        context_size_tokens: int,
        show_progress: bool = True,
    ) -> List[Tuple[int, int]]:
        """
        Create batches of dataframe rows that fit within the context window.

        Args:
            df: The dataframe to split
            columns: List of column names to include in token counting
            context_size_tokens: Maximum tokens per batch
            show_progress: Whether to show progress information

        Returns:
            List of (start_row, end_row) tuples for each batch
        """

        print(f"\n🔧 Creating batches with {context_size_tokens:,} token limit")

        # Validate columns exist
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Columns not found in dataframe: {missing_cols}")

        row_tokens = []
        for i in range(len(df)):
            tokens = self._count_row_tokens(df, columns, i)
            row_tokens.append(tokens)

        batches = []
        current_start = 0
        current_tokens = 0

        for i, tokens in enumerate(row_tokens):
            # If adding this row would exceed context limit, start a new batch
            if current_tokens + tokens > context_size_tokens and current_start < i:
                batches.append((current_start, i - 1))
                current_start = i
                current_tokens = tokens
            else:
                current_tokens += tokens

        # Add the final batch if there are remaining rows
        if current_start < len(df):
            batches.append((current_start, len(df) - 1))

        return batches

    def get_batch_dataframes(self, df: pd.DataFrame, columns: List[str], context_size_tokens: int) -> List[pd.DataFrame]:
        """
        Get list of dataframe batches that fit within context window.

        Args:
            df: The dataframe to split
            columns: List of column names to include in token counting
            context_size_tokens: Maximum tokens per batch

        Returns:
            List of dataframe batches
        """
        batches = self._create_batches(df, columns, context_size_tokens)

        batch_dataframes = []
        for start, end in batches:
            batch_df = df.iloc[start : (end + 1)].copy()  # noqa
            batch_dataframes.append(batch_df)

        return batch_dataframes
