"""
Unit tests for PromptLearningOptimizer.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from providers.base_provider import ModelProvider
from interfaces.token_counter import TokenCounter
from core.pricing import PricingCalculator


class TestPromptLearningOptimizer:
    """Test the main optimizer class."""

    def test_init_default(self):
        """Test optimizer initialization with defaults."""
        optimizer = PromptLearningOptimizer(
            prompt="Test prompt", openai_api_key="test_key"
        )

        assert optimizer.prompt == "Test prompt"
        assert optimizer.model_choice == "gpt-4"
        assert optimizer.verbose is False
        assert optimizer.budget_limit == 5.0

    def test_init_with_custom_settings(self):
        """Test optimizer initialization with custom settings."""
        mock_provider = Mock(spec=ModelProvider)
        mock_counter = Mock(spec=TokenCounter)
        mock_pricing = Mock(spec=PricingCalculator)

        optimizer = PromptLearningOptimizer(
            prompt="Custom prompt",
            model_choice="gpt-3.5-turbo",
            provider=mock_provider,
            token_counter=mock_counter,
            pricing_calculator=mock_pricing,
            verbose=True,
            budget_limit=10.0,
        )

        assert optimizer.prompt == "Custom prompt"
        assert optimizer.model_choice == "gpt-3.5-turbo"
        assert optimizer.provider is mock_provider
        assert optimizer.verbose is True
        assert optimizer.pricing_calculator is mock_pricing
        assert optimizer.budget_limit == 10.0

    def test_initialization_list_prompt(self):
        """Test initialization with list-style prompt."""
        list_prompt = [{"role": "user", "content": "Hello"}]
        optimizer = PromptLearningOptimizer(
            prompt=list_prompt, openai_api_key="test_key"
        )

        assert optimizer.prompt == list_prompt

    def test_initialization_custom_model(self):
        """Test initialization with custom model."""
        optimizer = PromptLearningOptimizer(
            prompt="Test", model_choice="gpt-3.5-turbo", openai_api_key="test_key"
        )

        assert optimizer.model_choice == "gpt-3.5-turbo"

    def test_budget_limit_setting(self):
        """Test budget limit configuration."""
        optimizer = PromptLearningOptimizer(
            prompt="Test", budget_limit=15.0, openai_api_key="test_key"
        )

        assert optimizer.budget_limit == 15.0
