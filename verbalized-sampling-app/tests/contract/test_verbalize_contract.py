"""
Contract tests for Verbalize endpoint (Python side)
Tests schema validation and type checking for IPC between Tauri and Python sidecar
"""

import pytest
import json
from pathlib import Path
from pydantic import ValidationError
from vs_bridge.models import (
    VerbRequest,
    VerbResponse,
    Provider,
    CompletionResponse,
    TraceMetadata,
    TokenProbability,
)
from datetime import datetime
import uuid


# ============================================================================
# Schema Loading
# ============================================================================

def load_schema(schema_name: str) -> dict:
    """Load JSON schema from schemas/v1 directory"""
    schema_path = Path(__file__).parent.parent.parent / "schemas" / "v1" / schema_name
    with open(schema_path, "r") as f:
        return json.load(f)


# ============================================================================
# Request Validation Tests
# ============================================================================

class TestVerbRequestValidation:
    """Test VerbRequest model validation"""

    def test_valid_minimal_request(self):
        """Test minimal valid request with required fields only"""
        request = VerbRequest(
            prompt="Test prompt",
            k=5,
            model="gpt-4",
            provider=Provider.OPENAI,
        )
        assert request.prompt == "Test prompt"
        assert request.k == 5
        assert request.tau == 1.0  # Default
        assert request.temperature == 0.8  # Default
        assert request.seed is None
        assert request.include_token_probabilities is False

    def test_valid_full_request(self):
        """Test fully specified request"""
        request = VerbRequest(
            prompt="Test prompt",
            k=50,
            tau=1.5,
            temperature=0.9,
            seed=42,
            model="claude-3-opus",
            provider=Provider.ANTHROPIC,
            include_token_probabilities=True,
        )
        assert request.tau == 1.5
        assert request.temperature == 0.9
        assert request.seed == 42
        assert request.include_token_probabilities is True

    def test_invalid_empty_prompt(self):
        """Test validation fails for empty prompt"""
        with pytest.raises(ValidationError) as exc_info:
            VerbRequest(
                prompt="",
                k=5,
                model="gpt-4",
                provider=Provider.OPENAI,
            )
        errors = exc_info.value.errors()
        assert any("prompt" in str(e).lower() for e in errors)

    def test_invalid_prompt_too_long(self):
        """Test validation fails for prompt exceeding max length"""
        long_prompt = "x" * 100001
        with pytest.raises(ValidationError) as exc_info:
            VerbRequest(
                prompt=long_prompt,
                k=5,
                model="gpt-4",
                provider=Provider.OPENAI,
            )
        errors = exc_info.value.errors()
        assert any("prompt" in str(e).lower() for e in errors)

    def test_invalid_k_too_low(self):
        """Test validation fails for k < 1"""
        with pytest.raises(ValidationError):
            VerbRequest(
                prompt="Test",
                k=0,
                model="gpt-4",
                provider=Provider.OPENAI,
            )

    def test_invalid_k_exceeds_provider_limit(self):
        """Test validation fails when k exceeds provider limit"""
        with pytest.raises(ValidationError) as exc_info:
            VerbRequest(
                prompt="Test",
                k=150,  # Exceeds OpenAI limit of 100
                model="gpt-4",
                provider=Provider.OPENAI,
            )
        errors = exc_info.value.errors()
        assert any("k" in str(e).lower() for e in errors)

    def test_local_vllm_allows_higher_k(self):
        """Test local_vllm provider allows k up to 500"""
        request = VerbRequest(
            prompt="Test",
            k=500,
            model="llama-3-70b",
            provider=Provider.LOCAL_VLLM,
        )
        assert request.k == 500

    def test_invalid_tau_out_of_range(self):
        """Test validation fails for tau outside [0.0, 10.0]"""
        with pytest.raises(ValidationError):
            VerbRequest(
                prompt="Test",
                k=5,
                tau=11.0,  # Exceeds max
                model="gpt-4",
                provider=Provider.OPENAI,
            )

    def test_invalid_temperature_out_of_range(self):
        """Test validation fails for temperature outside [0.0, 2.0]"""
        with pytest.raises(ValidationError):
            VerbRequest(
                prompt="Test",
                k=5,
                temperature=3.0,  # Exceeds max
                model="gpt-4",
                provider=Provider.OPENAI,
            )

    def test_invalid_empty_model(self):
        """Test validation fails for empty model string"""
        with pytest.raises(ValidationError):
            VerbRequest(
                prompt="Test",
                k=5,
                model="",
                provider=Provider.OPENAI,
            )


# ============================================================================
# Response Validation Tests
# ============================================================================

class TestVerbResponseValidation:
    """Test VerbResponse model validation"""

    def test_valid_response(self):
        """Test valid response with all fields"""
        response = VerbResponse(
            distribution_id=str(uuid.uuid4()),
            completions=[
                CompletionResponse(
                    text="Completion 1",
                    probability=0.6,
                    rank=1,
                ),
                CompletionResponse(
                    text="Completion 2",
                    probability=0.4,
                    rank=2,
                ),
            ],
            trace_metadata=TraceMetadata(
                model="gpt-4",
                provider="openai",
                api_latency_ms=150.5,
                token_count=50,
                k=2,
                tau=1.0,
                temperature=0.8,
                seed=42,
            ),
            timestamp=datetime.now(),
        )
        assert len(response.completions) == 2
        assert response.completions[0].rank == 1

    def test_response_with_token_probabilities(self):
        """Test response including token-level probabilities"""
        response = VerbResponse(
            distribution_id=str(uuid.uuid4()),
            completions=[
                CompletionResponse(
                    text="Hello world",
                    probability=1.0,
                    rank=1,
                    token_probabilities=[
                        TokenProbability(token="Hello", prob=0.9),
                        TokenProbability(token=" world", prob=0.85),
                    ],
                ),
            ],
            trace_metadata=TraceMetadata(
                model="gpt-4",
                provider="openai",
                api_latency_ms=100.0,
                token_count=2,
            ),
            timestamp=datetime.now(),
        )
        assert len(response.completions[0].token_probabilities) == 2
        assert response.completions[0].token_probabilities[0].token == "Hello"

    def test_invalid_empty_completions(self):
        """Test validation fails for empty completions array"""
        with pytest.raises(ValidationError):
            VerbResponse(
                distribution_id=str(uuid.uuid4()),
                completions=[],  # Must have at least 1
                trace_metadata=TraceMetadata(
                    model="gpt-4",
                    provider="openai",
                    api_latency_ms=100.0,
                    token_count=0,
                ),
                timestamp=datetime.now(),
            )

    def test_probability_normalization(self):
        """Test probabilities are within [0, 1] range"""
        with pytest.raises(ValidationError):
            VerbResponse(
                distribution_id=str(uuid.uuid4()),
                completions=[
                    CompletionResponse(
                        text="Test",
                        probability=1.5,  # Exceeds 1.0
                        rank=1,
                    ),
                ],
                trace_metadata=TraceMetadata(
                    model="gpt-4",
                    provider="openai",
                    api_latency_ms=100.0,
                    token_count=1,
                ),
                timestamp=datetime.now(),
            )


# ============================================================================
# JSON Schema Compliance Tests
# ============================================================================

class TestJSONSchemaCompliance:
    """Test Pydantic models match JSON schemas"""

    def test_verb_request_schema_fields(self):
        """Test VerbRequest has all required schema fields"""
        schema = load_schema("verbalize-request.json")
        required_fields = set(schema["required"])
        model_fields = set(VerbRequest.model_fields.keys())

        # Check all required fields are present
        assert required_fields.issubset(model_fields)

    def test_verb_response_schema_fields(self):
        """Test VerbResponse has all required schema fields"""
        schema = load_schema("verbalize-response.json")
        required_fields = set(schema["required"])
        model_fields = set(VerbResponse.model_fields.keys())

        # Map snake_case schema to model fields
        field_mapping = {
            "distribution_id": "distribution_id",
            "completions": "completions",
            "trace_metadata": "trace_metadata",
            "timestamp": "timestamp",
        }

        for schema_field in required_fields:
            model_field = field_mapping.get(schema_field, schema_field)
            assert model_field in model_fields, f"Missing field: {schema_field}"

    def test_provider_enum_values(self):
        """Test Provider enum matches schema values"""
        schema = load_schema("verbalize-request.json")
        schema_providers = set(schema["properties"]["provider"]["enum"])
        model_providers = {p.value for p in Provider}

        assert schema_providers == model_providers


# ============================================================================
# Serialization Tests
# ============================================================================

class TestSerialization:
    """Test JSON serialization/deserialization"""

    def test_request_serialization(self):
        """Test VerbRequest can be serialized to JSON"""
        request = VerbRequest(
            prompt="Test",
            k=5,
            model="gpt-4",
            provider=Provider.OPENAI,
        )
        json_str = request.model_dump_json()
        parsed = json.loads(json_str)

        assert parsed["prompt"] == "Test"
        assert parsed["k"] == 5
        assert parsed["provider"] == "openai"

    def test_response_deserialization(self):
        """Test VerbResponse can be deserialized from JSON"""
        json_data = {
            "distribution_id": str(uuid.uuid4()),
            "completions": [
                {"text": "Test", "probability": 1.0, "rank": 1}
            ],
            "trace_metadata": {
                "model": "gpt-4",
                "provider": "openai",
                "api_latency_ms": 100.0,
                "token_count": 1,
            },
            "timestamp": datetime.now().isoformat(),
        }
        response = VerbResponse(**json_data)
        assert response.completions[0].text == "Test"

    def test_datetime_encoding(self):
        """Test datetime fields are properly encoded to ISO format"""
        response = VerbResponse(
            distribution_id=str(uuid.uuid4()),
            completions=[
                CompletionResponse(text="Test", probability=1.0, rank=1)
            ],
            trace_metadata=TraceMetadata(
                model="gpt-4",
                provider="openai",
                api_latency_ms=100.0,
                token_count=1,
            ),
            timestamp=datetime(2024, 1, 15, 10, 30, 0),
        )
        json_str = response.model_dump_json()
        parsed = json.loads(json_str)

        # Check timestamp is ISO 8601 string
        assert "2024-01-15" in parsed["timestamp"]
        assert "T" in parsed["timestamp"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
