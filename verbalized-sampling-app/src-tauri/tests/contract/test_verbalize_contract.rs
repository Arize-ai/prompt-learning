/*!
 * Contract tests for Verbalize endpoint (Rust side)
 * Tests schema validation and type checking for IPC between Tauri and Python sidecar
 */

use serde_json;
use std::fs;
use std::path::PathBuf;

// Import models from the main crate
use verbalized_sampling_app_lib::models::{
    CompletionResponse, DistributionResponse, Provider, TokenProbability, TraceMetadata,
    VerbParams,
};

// ============================================================================
// Schema Loading
// ============================================================================

fn load_schema(schema_name: &str) -> serde_json::Value {
    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let schema_path = manifest_dir
        .parent()
        .unwrap()
        .join("schemas")
        .join("v1")
        .join(schema_name);

    let schema_content = fs::read_to_string(&schema_path)
        .unwrap_or_else(|_| panic!("Failed to read schema: {:?}", schema_path));

    serde_json::from_str(&schema_content).expect("Invalid JSON schema")
}

// ============================================================================
// Request Validation Tests
// ============================================================================

#[cfg(test)]
mod test_verb_params_validation {
    use super::*;

    #[test]
    fn test_valid_minimal_request() {
        let params = VerbParams {
            prompt: "Test prompt".to_string(),
            k: 5,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        assert!(params.validate().is_ok());
        assert_eq!(params.k, 5);
        assert_eq!(params.tau, 1.0);
        assert_eq!(params.temperature, 0.8);
    }

    #[test]
    fn test_valid_full_request() {
        let params = VerbParams {
            prompt: "Test prompt".to_string(),
            k: 50,
            tau: 1.5,
            temperature: 0.9,
            seed: Some(42),
            model: "claude-3-opus".to_string(),
            provider: Provider::Anthropic,
            include_token_probabilities: true,
        };

        assert!(params.validate().is_ok());
        assert_eq!(params.seed, Some(42));
        assert!(params.include_token_probabilities);
    }

    #[test]
    fn test_invalid_empty_prompt() {
        let params = VerbParams {
            prompt: "".to_string(),
            k: 5,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Prompt cannot be empty"));
    }

    #[test]
    fn test_invalid_prompt_too_long() {
        let long_prompt = "x".repeat(100001);
        let params = VerbParams {
            prompt: long_prompt,
            k: 5,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("exceeds maximum length"));
    }

    #[test]
    fn test_invalid_k_too_low() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 0,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("k must be at least 1"));
    }

    #[test]
    fn test_invalid_k_exceeds_provider_limit() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 150, // Exceeds OpenAI limit of 100
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("exceeds maximum of 100"));
    }

    #[test]
    fn test_local_vllm_allows_higher_k() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 500,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "llama-3-70b".to_string(),
            provider: Provider::LocalVllm,
            include_token_probabilities: false,
        };

        assert!(params.validate().is_ok());
    }

    #[test]
    fn test_invalid_tau_out_of_range() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 5,
            tau: 11.0, // Exceeds max of 10.0
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("tau must be between"));
    }

    #[test]
    fn test_invalid_temperature_out_of_range() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 5,
            tau: 1.0,
            temperature: 3.0, // Exceeds max of 2.0
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("temperature must be between"));
    }

    #[test]
    fn test_invalid_empty_model() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 5,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let result = params.validate();
        assert!(result.is_err());
        assert!(result.unwrap_err().contains("Model cannot be empty"));
    }
}

// ============================================================================
// Provider Tests
// ============================================================================

#[cfg(test)]
mod test_provider {
    use super::*;

    #[test]
    fn test_provider_max_k_api() {
        assert_eq!(Provider::Openai.max_k(), 100);
        assert_eq!(Provider::Anthropic.max_k(), 100);
        assert_eq!(Provider::Cohere.max_k(), 100);
    }

    #[test]
    fn test_provider_max_k_local() {
        assert_eq!(Provider::LocalVllm.max_k(), 500);
    }

    #[test]
    fn test_provider_serialization() {
        let provider = Provider::Openai;
        let json = serde_json::to_string(&provider).unwrap();
        assert_eq!(json, r#""openai""#);

        let provider = Provider::LocalVllm;
        let json = serde_json::to_string(&provider).unwrap();
        assert_eq!(json, r#""local_vllm""#);
    }

    #[test]
    fn test_provider_deserialization() {
        let json = r#""openai""#;
        let provider: Provider = serde_json::from_str(json).unwrap();
        assert_eq!(provider, Provider::Openai);

        let json = r#""local_vllm""#;
        let provider: Provider = serde_json::from_str(json).unwrap();
        assert_eq!(provider, Provider::LocalVllm);
    }
}

// ============================================================================
// Response Structure Tests
// ============================================================================

#[cfg(test)]
mod test_distribution_response {
    use super::*;

    #[test]
    fn test_valid_response() {
        let response = DistributionResponse {
            distribution_id: "123e4567-e89b-12d3-a456-426614174000".to_string(),
            completions: vec![
                CompletionResponse {
                    text: "Completion 1".to_string(),
                    probability: 0.6,
                    rank: 1,
                    token_probabilities: None,
                },
                CompletionResponse {
                    text: "Completion 2".to_string(),
                    probability: 0.4,
                    rank: 2,
                    token_probabilities: None,
                },
            ],
            trace_metadata: TraceMetadata {
                model: "gpt-4".to_string(),
                provider: "openai".to_string(),
                api_latency_ms: 150.5,
                token_count: 50,
                k: Some(2),
                tau: Some(1.0),
                temperature: Some(0.8),
                seed: Some(42),
                api_version: None,
            },
            timestamp: "2024-01-15T10:30:00Z".to_string(),
        };

        assert_eq!(response.completions.len(), 2);
        assert_eq!(response.completions[0].rank, 1);
        assert_eq!(response.trace_metadata.model, "gpt-4");
    }

    #[test]
    fn test_response_with_token_probabilities() {
        let response = DistributionResponse {
            distribution_id: "123e4567-e89b-12d3-a456-426614174000".to_string(),
            completions: vec![CompletionResponse {
                text: "Hello world".to_string(),
                probability: 1.0,
                rank: 1,
                token_probabilities: Some(vec![
                    TokenProbability {
                        token: "Hello".to_string(),
                        prob: 0.9,
                    },
                    TokenProbability {
                        token: " world".to_string(),
                        prob: 0.85,
                    },
                ]),
            }],
            trace_metadata: TraceMetadata {
                model: "gpt-4".to_string(),
                provider: "openai".to_string(),
                api_latency_ms: 100.0,
                token_count: 2,
                k: None,
                tau: None,
                temperature: None,
                seed: None,
                api_version: None,
            },
            timestamp: "2024-01-15T10:30:00Z".to_string(),
        };

        assert_eq!(
            response.completions[0]
                .token_probabilities
                .as_ref()
                .unwrap()
                .len(),
            2
        );
        assert_eq!(
            response.completions[0]
                .token_probabilities
                .as_ref()
                .unwrap()[0]
                .token,
            "Hello"
        );
    }
}

// ============================================================================
// Serialization Tests
// ============================================================================

#[cfg(test)]
mod test_serialization {
    use super::*;

    #[test]
    fn test_request_serialization() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 5,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let json = serde_json::to_string(&params).unwrap();
        let parsed: serde_json::Value = serde_json::from_str(&json).unwrap();

        assert_eq!(parsed["prompt"], "Test");
        assert_eq!(parsed["k"], 5);
        assert_eq!(parsed["provider"], "openai");
    }

    #[test]
    fn test_response_deserialization() {
        let json_data = r#"{
            "distribution_id": "123e4567-e89b-12d3-a456-426614174000",
            "completions": [
                {
                    "text": "Test",
                    "probability": 1.0,
                    "rank": 1
                }
            ],
            "trace_metadata": {
                "model": "gpt-4",
                "provider": "openai",
                "api_latency_ms": 100.0,
                "token_count": 1
            },
            "timestamp": "2024-01-15T10:30:00Z"
        }"#;

        let response: DistributionResponse = serde_json::from_str(json_data).unwrap();
        assert_eq!(response.completions[0].text, "Test");
        assert_eq!(response.trace_metadata.model, "gpt-4");
    }

    #[test]
    fn test_optional_fields_omitted() {
        let params = VerbParams {
            prompt: "Test".to_string(),
            k: 5,
            tau: 1.0,
            temperature: 0.8,
            seed: None,
            model: "gpt-4".to_string(),
            provider: Provider::Openai,
            include_token_probabilities: false,
        };

        let json = serde_json::to_value(&params).unwrap();

        // seed should not be present when None
        assert!(!json.as_object().unwrap().contains_key("seed"));
    }
}

// ============================================================================
// JSON Schema Compliance Tests
// ============================================================================

#[cfg(test)]
mod test_json_schema_compliance {
    use super::*;

    #[test]
    fn test_verb_request_schema_exists() {
        let schema = load_schema("verbalize-request.json");
        assert_eq!(schema["title"], "Verbalize Request");
        assert!(schema["required"].is_array());
    }

    #[test]
    fn test_verb_response_schema_exists() {
        let schema = load_schema("verbalize-response.json");
        assert_eq!(schema["title"], "Verbalize Response");
        assert!(schema["required"].is_array());
    }

    #[test]
    fn test_provider_enum_matches_schema() {
        let schema = load_schema("verbalize-request.json");
        let schema_providers = schema["properties"]["provider"]["enum"]
            .as_array()
            .unwrap();

        let model_providers = vec!["openai", "anthropic", "cohere", "local_vllm"];

        for provider in &model_providers {
            assert!(
                schema_providers
                    .iter()
                    .any(|v| v.as_str().unwrap() == *provider),
                "Provider {} not in schema",
                provider
            );
        }
    }
}
