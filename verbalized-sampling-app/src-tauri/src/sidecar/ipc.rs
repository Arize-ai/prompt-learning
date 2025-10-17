use serde::{Deserialize, Serialize};
use std::time::Duration;

/// Generic request wrapper for sidecar IPC
#[derive(Debug, Serialize)]
pub struct SidecarRequest<T> {
    pub payload: T,
}

/// Generic response wrapper for sidecar IPC
#[derive(Debug, Deserialize)]
pub struct SidecarResponse<T> {
    pub data: Option<T>,
    pub error: Option<String>,
}

/// Send HTTP request to sidecar service
/// endpoint: API endpoint path (e.g., "/api/v1/verbalize")
/// payload: JSON-serializable request payload
pub async fn send_request<T, R>(endpoint: &str, payload: T) -> Result<R, String>
where
    T: Serialize,
    R: for<'de> Deserialize<'de>,
{
    let url = format!("http://127.0.0.1:8765{}", endpoint);
    let client = reqwest::Client::new();

    log::debug!("📡 Sending request to sidecar: {}", url);

    let response = client
        .post(&url)
        .json(&payload)  // Send payload directly, not wrapped
        .timeout(Duration::from_secs(30))
        .send()
        .await
        .map_err(|e| {
            log::error!("❌ Request failed: {}", e);

            // Check for connection refused (sidecar not running)
            if e.is_connect() {
                return "Sidecar connection refused - service may be down".to_string();
            }

            // Check for timeout
            if e.is_timeout() {
                return "Request timeout after 30 seconds".to_string();
            }

            format!("HTTP request error: {}", e)
        })?;

    // Check HTTP status
    if !response.status().is_success() {
        let status = response.status();
        let error_body = response.text().await.unwrap_or_default();
        log::error!("❌ HTTP error {}: {}", status, error_body);
        return Err(format!("HTTP {} - {}", status, error_body));
    }

    // Parse response directly (FastAPI returns data unwrapped)
    let result: R = response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))?;

    Ok(result)
}

/// Send GET request to sidecar service
pub async fn get_request<R>(endpoint: &str) -> Result<R, String>
where
    R: for<'de> Deserialize<'de>,
{
    let url = format!("http://127.0.0.1:8765{}", endpoint);
    let client = reqwest::Client::new();

    log::debug!("📡 GET request to sidecar: {}", url);

    let response = client
        .get(&url)
        .timeout(Duration::from_secs(30))
        .send()
        .await
        .map_err(|e| {
            if e.is_connect() {
                return "Sidecar connection refused - service may be down".to_string();
            }
            if e.is_timeout() {
                return "Request timeout after 30 seconds".to_string();
            }
            format!("HTTP request error: {}", e)
        })?;

    if !response.status().is_success() {
        let status = response.status();
        let error_body = response.text().await.unwrap_or_default();
        return Err(format!("HTTP {} - {}", status, error_body));
    }

    response
        .json()
        .await
        .map_err(|e| format!("Failed to parse response: {}", e))
}
