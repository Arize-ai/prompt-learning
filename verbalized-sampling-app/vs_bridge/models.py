"""
Pydantic models for Verbalized Sampling Desktop App
Contract validation for IPC between Tauri and Python sidecar
"""

from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field, field_validator, constr, conint
from datetime import datetime


class Provider(str, Enum):
    """LLM provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"
    LOCAL_VLLM = "local_vllm"
    OPENROUTER = "openrouter"

    def max_k(self) -> int:
        """Get maximum k value for this provider"""
        if self in (Provider.OPENAI, Provider.ANTHROPIC, Provider.COHERE, Provider.OPENROUTER):
            return 100
        return 500


class VerbRequest(BaseModel):
    """Request schema for verbalize endpoint"""
    prompt: constr(min_length=1, max_length=100000) = Field(
        ..., description="Input text prompt for LLM completion generation"
    )
    k: conint(ge=1, le=500) = Field(
        ..., description="Number of completions to generate"
    )
    tau: float = Field(
        default=1.0, ge=0.0, le=10.0,
        description="Temperature scaling parameter"
    )
    temperature: float = Field(
        default=0.8, ge=0.0, le=2.0,
        description="Sampling temperature"
    )
    seed: Optional[int] = Field(
        default=None, ge=0,
        description="Random seed for deterministic sampling (null = random)"
    )
    model: constr(min_length=1) = Field(
        ..., description="Model identifier (e.g., 'gpt-4', 'claude-3-opus')"
    )
    provider: Provider = Field(
        ..., description="Provider identifier"
    )
    api_key: constr(min_length=1) = Field(
        ..., description="API key for the provider"
    )
    include_token_probabilities: bool = Field(
        default=False, description="Include token-level probabilities in response"
    )

    @field_validator('k')
    @classmethod
    def validate_k_for_provider(cls, v: int, info) -> int:
        """Validate k is within provider limits"""
        if 'provider' in info.data:
            provider = info.data['provider']
            max_k = provider.max_k()
            if v > max_k:
                raise ValueError(f"k exceeds maximum of {max_k} for provider {provider}")
        return v

    class Config:
        json_schema_extra = {
            "$schema": "http://json-schema.org/draft-07/schema#"
        }


class TokenProbability(BaseModel):
    """Token-level probability information"""
    token: str = Field(..., description="Token text")
    prob: float = Field(..., ge=0.0, le=1.0, description="Token probability")


class CompletionResponse(BaseModel):
    """Single completion with metadata"""
    text: str = Field(..., description="Completion text")
    probability: float = Field(..., ge=0.0, le=1.0, description="Normalized probability")
    rank: conint(ge=1) = Field(..., description="Rank by probability (1 = highest)")
    token_probabilities: Optional[List[TokenProbability]] = Field(
        default=None, description="Optional token-level probabilities"
    )


class TraceMetadata(BaseModel):
    """Execution trace metadata for reproducibility"""
    model: str = Field(..., description="Model used for generation")
    provider: str = Field(..., description="Provider used")
    api_latency_ms: float = Field(..., ge=0, description="API call latency in milliseconds")
    token_count: conint(ge=0) = Field(..., description="Total tokens in completions")
    k: Optional[int] = Field(default=None, description="Number of completions requested")
    tau: Optional[float] = Field(default=None, description="Temperature scaling used")
    temperature: Optional[float] = Field(default=None, description="Sampling temperature used")
    seed: Optional[int] = Field(default=None, description="Random seed used (null if random)")
    api_version: Optional[str] = Field(default=None, description="API version used")


class VerbResponse(BaseModel):
    """Response schema for verbalize endpoint"""
    distribution_id: str = Field(..., description="Unique identifier for this distribution (UUID)")
    completions: List[CompletionResponse] = Field(..., min_length=1, description="Array of weighted completions")
    trace_metadata: TraceMetadata = Field(..., description="Execution trace metadata")
    timestamp: datetime = Field(..., description="ISO 8601 timestamp of generation")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SampleRequest(BaseModel):
    """Request schema for weighted sampling"""
    distribution_id: str = Field(..., description="UUID of the distribution to sample from")
    seed: Optional[int] = Field(
        default=None, ge=0,
        description="Random seed for deterministic sampling (null = random)"
    )

    class Config:
        json_schema_extra = {
            "$schema": "http://json-schema.org/draft-07/schema#"
        }


class SampleResponse(BaseModel):
    """Response schema for weighted sampling"""
    selected_completion: str = Field(..., description="Text of the sampled completion")
    selection_index: conint(ge=0) = Field(..., description="Index of selected completion (0-based)")
    probability: Optional[float] = Field(
        default=None, ge=0.0, le=1.0,
        description="Probability of the selected completion"
    )
    seed_used: Optional[int] = Field(
        default=None, description="Seed that was used for this sample"
    )


class ExportFormat(str, Enum):
    """Export format types"""
    CSV = "csv"
    JSONL = "jsonl"


class ExportRequest(BaseModel):
    """Request schema for export operation"""
    distribution_ids: List[str] = Field(
        ..., min_length=1,
        description="Array of distribution UUIDs to export"
    )
    format: ExportFormat = Field(..., description="Export format")
    include_metadata: bool = Field(
        default=True, description="Include trace metadata in export"
    )
    output_path: constr(min_length=1) = Field(
        ..., description="Output file path (absolute or relative)"
    )

    class Config:
        json_schema_extra = {
            "$schema": "http://json-schema.org/draft-07/schema#"
        }


class ExportResponse(BaseModel):
    """Response schema for export operation"""
    file_path: str = Field(..., description="Absolute path to exported file")
    row_count: conint(ge=0) = Field(..., description="Number of rows/entries exported")
    file_size_bytes: conint(ge=0) = Field(..., description="File size in bytes")
    format: Optional[ExportFormat] = Field(default=None, description="Export format used")
    included_metadata: Optional[bool] = Field(
        default=None, description="Whether metadata was included in export"
    )


class SessionDistribution(BaseModel):
    """Distribution object for session save/load"""
    distribution_id: str = Field(..., description="UUID of distribution")
    prompt: str = Field(..., description="Original prompt")
    completions: List[CompletionResponse] = Field(..., description="Completions array")
    trace_metadata: TraceMetadata = Field(..., description="Trace metadata")
    timestamp: Optional[datetime] = Field(default=None, description="Generation timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class SessionSaveRequest(BaseModel):
    """Request schema for session save"""
    distributions: List[SessionDistribution] = Field(
        ..., min_length=1,
        description="Array of distribution objects to save"
    )
    notes: Optional[constr(max_length=10000)] = Field(
        default=None, description="Optional user notes about this session"
    )
    output_path: constr(min_length=1) = Field(
        ..., description="Output file path for session"
    )

    class Config:
        json_schema_extra = {
            "$schema": "http://json-schema.org/draft-07/schema#"
        }


class SessionLoadResponse(BaseModel):
    """Response schema for session load"""
    session_id: str = Field(..., description="Unique session identifier")
    distributions: List[SessionDistribution] = Field(
        ..., description="Array of loaded distributions"
    )
    notes: Optional[str] = Field(default=None, description="User notes from session")
    app_version: str = Field(..., description="App version that created this session")
    schema_version: str = Field(
        default="v1", description="Schema version (e.g., 'v1')"
    )
    created_at: datetime = Field(..., description="Session creation timestamp")
    loaded_at: Optional[datetime] = Field(default=None, description="Session load timestamp")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
