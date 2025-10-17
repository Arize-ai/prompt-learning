use serde::{Deserialize, Serialize};

/// Provider types for LLM services
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "snake_case")]
pub enum Provider {
    Openai,
    Anthropic,
    Cohere,
    LocalVllm,
}

impl Provider {
    /// Get maximum k value for this provider
    pub fn max_k(&self) -> u32 {
        match self {
            Provider::Openai | Provider::Anthropic | Provider::Cohere => 100,
            Provider::LocalVllm => 500,
        }
    }
}

/// Verbalize request parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct VerbParams {
    pub prompt: String,
    pub k: u32,
    #[serde(default = "default_tau")]
    pub tau: f64,
    #[serde(default = "default_temperature")]
    pub temperature: f64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub seed: Option<u64>,
    pub model: String,
    pub provider: Provider,
    #[serde(default)]
    pub include_token_probabilities: bool,
}

impl VerbParams {
    /// Validate parameters
    pub fn validate(&self) -> Result<(), String> {
        // Validate prompt
        if self.prompt.is_empty() {
            return Err("Prompt cannot be empty".to_string());
        }
        if self.prompt.len() > 100_000 {
            return Err("Prompt exceeds maximum length of 100,000 characters".to_string());
        }

        // Validate k based on provider
        let max_k = self.provider.max_k();
        if self.k < 1 {
            return Err("k must be at least 1".to_string());
        }
        if self.k > max_k {
            return Err(format!(
                "k exceeds maximum of {} for provider {:?}",
                max_k, self.provider
            ));
        }

        // Validate tau
        if self.tau < 0.0 || self.tau > 10.0 {
            return Err("tau must be between 0.0 and 10.0".to_string());
        }

        // Validate temperature
        if self.temperature < 0.0 || self.temperature > 2.0 {
            return Err("temperature must be between 0.0 and 2.0".to_string());
        }

        // Validate model
        if self.model.is_empty() {
            return Err("Model cannot be empty".to_string());
        }

        Ok(())
    }
}

fn default_tau() -> f64 {
    1.0
}

fn default_temperature() -> f64 {
    0.8
}

/// Token-level probability information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TokenProbability {
    pub token: String,
    pub prob: f64,
}

/// Single completion with metadata
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CompletionResponse {
    pub text: String,
    pub probability: f64,
    pub rank: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub token_probabilities: Option<Vec<TokenProbability>>,
}

/// Trace metadata for reproducibility
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct TraceMetadata {
    pub model: String,
    pub provider: String,
    pub api_latency_ms: f64,
    pub token_count: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub k: Option<u32>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub tau: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub temperature: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub seed: Option<u64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub api_version: Option<String>,
}

/// Verbalize response with distribution
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DistributionResponse {
    pub distribution_id: String,
    pub completions: Vec<CompletionResponse>,
    pub trace_metadata: TraceMetadata,
    pub timestamp: String,
}

/// Sample request parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SampleRequest {
    pub distribution_id: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub seed: Option<u64>,
}

/// Sample response with selected completion
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SampleResponse {
    pub selected_completion: String,
    pub selection_index: u32,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub probability: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub seed_used: Option<u64>,
}

/// Export format enum
#[derive(Debug, Clone, Serialize, Deserialize, PartialEq)]
#[serde(rename_all = "lowercase")]
pub enum ExportFormat {
    Csv,
    Jsonl,
}

/// Export request parameters
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportRequest {
    pub distribution_ids: Vec<String>,
    pub format: ExportFormat,
    #[serde(default = "default_include_metadata")]
    pub include_metadata: bool,
    pub output_path: String,
}

impl ExportRequest {
    pub fn validate(&self) -> Result<(), String> {
        if self.distribution_ids.is_empty() {
            return Err("At least one distribution ID required".to_string());
        }
        if self.output_path.is_empty() {
            return Err("Output path cannot be empty".to_string());
        }
        Ok(())
    }
}

fn default_include_metadata() -> bool {
    true
}

/// Export response with file information
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ExportResponse {
    pub file_path: String,
    pub row_count: u64,
    pub file_size_bytes: u64,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub format: Option<ExportFormat>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub included_metadata: Option<bool>,
}

/// Distribution object for session save
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionDistribution {
    pub distribution_id: String,
    pub prompt: String,
    pub completions: Vec<CompletionResponse>,
    pub trace_metadata: TraceMetadata,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub timestamp: Option<String>,
}

/// Session save request
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionSaveRequest {
    pub distributions: Vec<SessionDistribution>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
    pub output_path: String,
}

impl SessionSaveRequest {
    pub fn validate(&self) -> Result<(), String> {
        if self.distributions.is_empty() {
            return Err("At least one distribution required".to_string());
        }
        if self.output_path.is_empty() {
            return Err("Output path cannot be empty".to_string());
        }
        if let Some(notes) = &self.notes {
            if notes.len() > 10_000 {
                return Err("Notes exceed maximum length of 10,000 characters".to_string());
            }
        }
        Ok(())
    }
}

/// Session load response
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct SessionLoadResponse {
    pub session_id: String,
    pub distributions: Vec<SessionDistribution>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub notes: Option<String>,
    pub app_version: String,
    #[serde(default = "default_schema_version")]
    pub schema_version: String,
    pub created_at: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub loaded_at: Option<String>,
}

fn default_schema_version() -> String {
    "v1".to_string()
}
