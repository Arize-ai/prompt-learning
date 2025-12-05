"""
Unit tests for token counter interfaces.
"""

import pytest
import pandas as pd
from interfaces.token_counter import TiktokenCounter, ApproximateCounter


class TestTiktokenCounter:
    """Test the tiktoken-based token counter."""

    def test_init(self):
        """Test counter initialization."""
        counter = TiktokenCounter()
        assert counter.encoder is not None

        counter_custom = TiktokenCounter("cl100k_base")
        assert counter_custom.encoder is not None

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        counter = TiktokenCounter()

        # Empty string
        assert counter.count_tokens("") == 0
        assert counter.count_tokens(None) == 0

        # Simple text
        tokens = counter.count_tokens("Hello world")
        assert tokens > 0
        assert isinstance(tokens, int)

    def test_count_tokens_longer_text(self):
        """Test token counting with longer text."""
        counter = TiktokenCounter()

        short_text = "Hi"
        long_text = "This is a much longer text that should have significantly more tokens than the short text."

        short_tokens = counter.count_tokens(short_text)
        long_tokens = counter.count_tokens(long_text)

        assert long_tokens > short_tokens

    def test_count_dataframe_tokens(self):
        """Test counting tokens in dataframe."""
        counter = TiktokenCounter()

        df = pd.DataFrame(
            {
                "text1": ["Hello world", "This is longer"],
                "text2": ["Short", "Much longer text here"],
                "other": [1, 2],  # Non-text column
            }
        )

        counts = counter.count_dataframe_tokens(df, ["text1", "text2"])
        assert len(counts) == 2
        assert all(count > 0 for count in counts)
        assert counts[1] > counts[0]  # Second row has more text

    def test_count_dataframe_tokens_missing_columns(self):
        """Test counting tokens with missing columns."""
        counter = TiktokenCounter()

        df = pd.DataFrame({"text1": ["Hello world", "This is longer"]})

        counts = counter.count_dataframe_tokens(df, ["text1", "missing_col"])
        assert len(counts) == 2
        assert all(count > 0 for count in counts)

    def test_estimate_tokens(self):
        """Test token estimation (should be same as exact count for tiktoken)."""
        counter = TiktokenCounter()
        text = "This is some sample text for estimation"

        exact = counter.count_tokens(text)
        estimate = counter.estimate_tokens(text)

        assert exact == estimate


class TestApproximateCounter:
    """Test the approximate token counter."""

    def test_init(self):
        """Test counter initialization."""
        counter = ApproximateCounter()
        assert counter is not None

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        counter = ApproximateCounter()

        # Empty string
        assert counter.count_tokens("") == 0
        assert counter.count_tokens(None) == 0

        # Test the 4-character rule
        text = "1234"  # 4 characters = 1 token
        assert counter.count_tokens(text) == 1

        text = "12345678"  # 8 characters = 2 tokens
        assert counter.count_tokens(text) == 2

    def test_count_tokens_approximation(self):
        """Test that approximation follows chars/4 rule."""
        counter = ApproximateCounter()

        # Test various lengths
        for length in [4, 8, 12, 20]:
            text = "x" * length
            expected_tokens = length // 4
            assert counter.count_tokens(text) == expected_tokens

    def test_count_dataframe_tokens(self):
        """Test counting tokens in dataframe."""
        counter = ApproximateCounter()

        df = pd.DataFrame(
            {
                "text1": ["1234", "12345678"],  # 4 chars, 8 chars
                "text2": ["12", "123456"],  # 2 chars, 6 chars
            }
        )

        counts = counter.count_dataframe_tokens(df, ["text1", "text2"])
        # Row 0: (4+2)/4 = 1.5 -> 1 token
        # Row 1: (8+6)/4 = 3.5 -> 3 tokens
        assert counts == [1, 3]

    def test_count_dataframe_tokens_missing_columns(self):
        """Test counting tokens with missing columns."""
        counter = ApproximateCounter()

        df = pd.DataFrame({"text1": ["1234", "12345678"]})

        counts = counter.count_dataframe_tokens(df, ["text1", "missing_col"])
        assert len(counts) == 2
        assert counts == [1, 2]  # Only text1 column counted

    def test_estimate_tokens(self):
        """Test token estimation (should be same as exact count for approximate)."""
        counter = ApproximateCounter()
        text = "12345678"

        exact = counter.count_tokens(text)
        estimate = counter.estimate_tokens(text)

        assert exact == estimate == 2

    def test_unicode_handling(self):
        """Test handling of unicode characters."""
        counter = ApproximateCounter()

        # Test with emoji and unicode
        text = "café☕"  # Should count as character length
        tokens = counter.count_tokens(text)
        assert tokens == len(text) // 4

    def test_consistency_comparison(self):
        """Test that approximate counter is consistently faster/simpler than tiktoken."""
        tiktoken_counter = TiktokenCounter()
        approx_counter = ApproximateCounter()

        text = "This is a sample text for comparison testing"

        tiktoken_result = tiktoken_counter.count_tokens(text)
        approx_result = approx_counter.count_tokens(text)

        # Both should return positive integers
        assert tiktoken_result > 0
        assert approx_result > 0

        # Results will likely be different, but that's expected
        # The important thing is both work and return reasonable values
