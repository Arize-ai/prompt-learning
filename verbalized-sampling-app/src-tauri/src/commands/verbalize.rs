/*!
 * Verbalize command - Generate weighted completion distribution
 */

use crate::models::{DistributionResponse, VerbParams};
use crate::sidecar::ipc;
use serde_json::json;
use tauri::AppHandle;

/// Tauri command for verbalize endpoint
#[tauri::command]
pub async fn verbalize(
    app: AppHandle,
    params: VerbParams,
) -> Result<DistributionResponse, String> {
    log::info!("🎯 Verbalize command invoked");
    log::debug!("Parameters: {:?}", params);

    // Validate parameters
    params.validate()?;

    // Get API key for the provider
    let provider_str = match params.provider {
        crate::models::Provider::Openai => "openai",
        crate::models::Provider::Anthropic => "anthropic",
        crate::models::Provider::Cohere => "cohere",
        crate::models::Provider::LocalVllm => "",
        crate::models::Provider::Openrouter => "openrouter",
    };

    // Retrieve API key from store (skip for local VLLM)
    let api_key = if provider_str.is_empty() {
        String::new()
    } else {
        crate::commands::apikeys::get_api_key(app.clone(), provider_str.to_string())
            .await
            .map_err(|e| format!("API key not found for {}: {}. Please configure it in Settings.", provider_str, e))?
    };

    // Send request to Python sidecar
    let endpoint = "/api/v1/verbalize";
    let payload = json!({
        "prompt": params.prompt,
        "k": params.k,
        "tau": params.tau,
        "temperature": params.temperature,
        "seed": params.seed,
        "model": params.model,
        "provider": params.provider,
        "api_key": api_key,
        "include_token_probabilities": params.include_token_probabilities,
    });

    log::debug!("Sending request to sidecar: {}", endpoint);

    match ipc::send_request::<serde_json::Value, DistributionResponse>(endpoint, payload).await {
        Ok(response) => {
            log::info!("✅ Verbalize successful: distribution_id={}", response.distribution_id);
            log::debug!("Response: {} completions", response.completions.len());
            Ok(response)
        }
        Err(e) => {
            log::error!("❌ Verbalize failed: {}", e);
            Err(format!("Verbalize failed: {}", e))
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::models::Provider;

    #[tokio::test]
    async fn test_verbalize_validation() {
        let params = VerbParams {
            prompt: "".to_string(), // Invalid: empty prompt
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

    #[tokio::test]
    async fn test_k_limit_validation() {
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
        assert!(result.unwrap_err().contains("exceeds maximum"));
    }
}
