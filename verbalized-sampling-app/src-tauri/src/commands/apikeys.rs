/**
 * API Key Management Commands
 * Secure storage and retrieval of API keys using Tauri Store
 */

use serde::{Deserialize, Serialize};
use tauri::AppHandle;
use tauri_plugin_store::StoreExt;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiKey {
    pub provider: String,
    pub key: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ApiKeyResponse {
    pub provider: String,
    pub has_key: bool,
    pub key_preview: Option<String>, // First 8 chars for verification
}

const STORE_PATH: &str = "api_keys.dat";

/// Store an API key securely
#[tauri::command]
pub async fn store_api_key(
    app: AppHandle,
    provider: String,
    key: String,
) -> Result<(), String> {
    log::info!("🔐 Storing API key for provider: {}", provider);

    if key.trim().is_empty() {
        return Err("API key cannot be empty".to_string());
    }

    // Validate provider
    let valid_providers = vec!["openrouter", "openai", "anthropic", "cohere"];
    if !valid_providers.contains(&provider.to_lowercase().as_str()) {
        return Err(format!("Invalid provider: {}. Valid providers: {:?}", provider, valid_providers));
    }

    let store = app.store(STORE_PATH)
        .map_err(|e| format!("Failed to access store: {}", e))?;

    // Save the key
    store.set(provider.clone(), serde_json::json!(key));
    store.save()
        .map_err(|e| format!("Failed to save API key: {}", e))?;

    log::info!("✅ API key stored successfully for: {}", provider);
    Ok(())
}

/// Retrieve an API key
#[tauri::command]
pub async fn get_api_key(
    app: AppHandle,
    provider: String,
) -> Result<String, String> {
    log::info!("🔓 Retrieving API key for provider: {}", provider);

    let store = app.store(STORE_PATH)
        .map_err(|e| format!("Failed to access store: {}", e))?;

    match store.get(provider.clone()) {
        Some(value) => {
            let key = value.as_str()
                .ok_or_else(|| "Invalid key format".to_string())?
                .to_string();

            log::info!("✅ API key retrieved for: {}", provider);
            Ok(key)
        }
        None => Err(format!("No API key found for provider: {}", provider))
    }
}

/// Check if an API key exists for a provider
#[tauri::command]
pub async fn check_api_key(
    app: AppHandle,
    provider: String,
) -> Result<ApiKeyResponse, String> {
    log::info!("🔍 Checking API key for provider: {}", provider);

    match get_api_key(app, provider.clone()).await {
        Ok(key) => {
            let preview = if key.len() > 8 {
                Some(format!("{}...", &key[..8]))
            } else {
                Some("***".to_string())
            };

            Ok(ApiKeyResponse {
                provider,
                has_key: true,
                key_preview: preview,
            })
        }
        Err(_) => {
            Ok(ApiKeyResponse {
                provider,
                has_key: false,
                key_preview: None,
            })
        }
    }
}

/// Delete an API key
#[tauri::command]
pub async fn delete_api_key(
    app: AppHandle,
    provider: String,
) -> Result<(), String> {
    log::info!("🗑️ Deleting API key for provider: {}", provider);

    let store = app.store(STORE_PATH)
        .map_err(|e| format!("Failed to access store: {}", e))?;

    store.delete(provider.clone());
    store.save()
        .map_err(|e| format!("Failed to delete API key: {}", e))?;

    log::info!("✅ API key deleted for: {}", provider);
    Ok(())
}

/// Get all providers with API keys stored
#[tauri::command]
pub async fn list_api_keys(
    app: AppHandle,
) -> Result<Vec<ApiKeyResponse>, String> {
    log::info!("📋 Listing all stored API keys");

    let providers = vec!["openrouter", "openai", "anthropic", "cohere"];
    let mut results = Vec::new();

    for provider in providers {
        match check_api_key(app.clone(), provider.to_string()).await {
            Ok(response) => results.push(response),
            Err(e) => {
                log::warn!("Failed to check key for {}: {}", provider, e);
                results.push(ApiKeyResponse {
                    provider: provider.to_string(),
                    has_key: false,
                    key_preview: None,
                });
            }
        }
    }

    Ok(results)
}
