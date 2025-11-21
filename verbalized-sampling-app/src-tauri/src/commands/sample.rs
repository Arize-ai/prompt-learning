use crate::models::{SampleRequest, SampleResponse};
use crate::sidecar::ipc;
use serde_json::json;

#[tauri::command]
pub async fn sample(distribution_id: String, seed: Option<u64>) -> Result<SampleResponse, String> {
    log::info!("🎲 Sample command invoked for distribution: {}", distribution_id);

    let endpoint = "/api/v1/sample";
    let payload = json!({
        "distribution_id": distribution_id,
        "seed": seed,
    });

    match ipc::send_request::<serde_json::Value, SampleResponse>(endpoint, payload).await {
        Ok(response) => {
            log::info!("✅ Sample successful: index {}", response.selection_index);
            Ok(response)
        }
        Err(e) => {
            log::error!("❌ Sample failed: {}", e);
            Err(format!("Sample failed: {}", e))
        }
    }
}
