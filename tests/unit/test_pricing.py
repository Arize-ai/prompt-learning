"""
Unit tests for pricing calculator.
"""

import pytest
from core.pricing import PricingCalculator, ModelPricing


class TestPricingCalculator:
    """Test the pricing calculator functionality."""
    
    def test_init(self):
        """Test calculator initialization."""
        calc = PricingCalculator()
        assert calc.total_cost == 0.0
        assert calc.total_input_tokens == 0
        assert calc.total_output_tokens == 0
    
    def test_get_model_pricing_exact_match(self):
        """Test getting pricing for exact model match."""
        calc = PricingCalculator()
        pricing = calc.get_model_pricing("gpt-4")
        assert pricing.model_name == "gpt-4"
        assert pricing.input_price_per_1k == 0.03
        assert pricing.output_price_per_1k == 0.06
    
    def test_get_model_pricing_partial_match(self):
        """Test getting pricing for partial model match."""
        calc = PricingCalculator()
        pricing = calc.get_model_pricing("gpt-4-turbo-preview")
        assert pricing.model_name == "gpt-4"  # Current logic matches gpt-4 first
        assert pricing.input_price_per_1k == 0.03
        assert pricing.output_price_per_1k == 0.06
    
    def test_get_model_pricing_unknown_model(self):
        """Test getting pricing for unknown model returns fallback."""
        calc = PricingCalculator()
        pricing = calc.get_model_pricing("unknown-model")
        assert pricing.model_name == "unknown"
        assert pricing.input_price_per_1k == 0.01
        assert pricing.output_price_per_1k == 0.03
    
    def test_calculate_cost_gpt4(self):
        """Test cost calculation for GPT-4."""
        calc = PricingCalculator()
        cost = calc.calculate_cost("gpt-4", 1000, 500)
        # 1000/1000 * 0.03 + 500/1000 * 0.06 = 0.03 + 0.03 = 0.06
        assert cost == 0.06
    
    def test_calculate_cost_gemini_flash(self):
        """Test cost calculation for Gemini Flash."""
        calc = PricingCalculator()
        cost = calc.calculate_cost("gemini-2.5-flash", 10000, 1000)
        # 10000/1000 * 0.0003 + 1000/1000 * 0.0025 = 0.003 + 0.0025 = 0.0055
        assert cost == 0.0055
    
    def test_add_usage(self):
        """Test adding usage and tracking totals."""
        calc = PricingCalculator()
        
        cost1 = calc.add_usage("gpt-4", 1000, 500)
        assert cost1 == 0.06
        assert calc.total_cost == 0.06
        assert calc.total_input_tokens == 1000
        assert calc.total_output_tokens == 500
        
        cost2 = calc.add_usage("gemini-2.5-flash", 2000, 1000)
        assert cost2 == 0.0031
        assert calc.total_cost == 0.0631
        assert calc.total_input_tokens == 3000
        assert calc.total_output_tokens == 1500
    
    def test_would_exceed_budget(self):
        """Test budget checking."""
        calc = PricingCalculator()
        calc.add_usage("gpt-4", 1000, 500)  # $0.06
        
        # Adding another $0.06 would make total $0.12, which exceeds $0.10 budget
        assert calc.would_exceed_budget("gpt-4", 1000, 500, 0.10) is True
        
        # Adding $0.03 would make total $0.09, which doesn't exceed $0.10 budget
        assert calc.would_exceed_budget("gpt-4", 500, 250, 0.10) is False
    
    def test_reset(self):
        """Test resetting calculator."""
        calc = PricingCalculator()
        calc.add_usage("gpt-4", 1000, 500)
        
        assert calc.total_cost > 0
        calc.reset()
        
        assert calc.total_cost == 0.0
        assert calc.total_input_tokens == 0
        assert calc.total_output_tokens == 0
    
    def test_get_usage_summary(self):
        """Test getting usage summary."""
        calc = PricingCalculator()
        calc.add_usage("gpt-4", 1000, 500)
        calc.add_usage("gemini-2.5-flash", 2000, 1000)
        
        summary = calc.get_usage_summary()
        assert summary["total_cost"] == 0.0631
        assert summary["total_input_tokens"] == 3000
        assert summary["total_output_tokens"] == 1500
        assert summary["total_tokens"] == 4500
    
    def test_zero_tokens(self):
        """Test handling zero tokens."""
        calc = PricingCalculator()
        cost = calc.calculate_cost("gpt-4", 0, 0)
        assert cost == 0.0
        
        calc.add_usage("gpt-4", 0, 1000)
        assert calc.total_input_tokens == 0
        assert calc.total_output_tokens == 1000