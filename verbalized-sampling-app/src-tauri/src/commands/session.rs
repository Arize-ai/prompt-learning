use crate::models::{SessionSaveRequest, SessionLoadResponse};
use crate::sidecar::ipc;
use serde_json::json;

#[tauri::command]
pub async fn session_save(request: SessionSaveRequest) -> Result<String, String> {
    log::info!("💾 Session save command invoked: {} distributions", request.distributions.len());

    // Validate request
    request.validate()?;

    let endpoint = "/api/v1/session/save";

    match ipc::send_request::<SessionSaveRequest, serde_json::Value>(endpoint, request.clone()).await {
        Ok(response) => {
            let file_path = response.get("file_path")
                .and_then(|v| v.as_str())
                .unwrap_or(&request.output_path)
                .to_string();

            log::info!("✅ Session saved to: {}", file_path);
            Ok(file_path)
        }
        Err(e) => {
            log::error!("❌ Session save failed: {}", e);
            Err(format!("Session save failed: {}", e))
        }
    }
}

#[tauri::command]
pub async fn session_load(file_path: String) -> Result<SessionLoadResponse, String> {
    log::info!("📂 Session load command invoked: {}", file_path);

    let endpoint = "/api/v1/session/load";
    let payload = json!({
        "file_path": file_path,
    });

    match ipc::send_request::<serde_json::Value, SessionLoadResponse>(endpoint, payload).await {
        Ok(response) => {
            log::info!("✅ Session loaded: {} distributions", response.distributions.len());
            Ok(response)
        }
        Err(e) => {
            log::error!("❌ Session load failed: {}", e);
            Err(format!("Session load failed: {}", e))
        }
    }
}
