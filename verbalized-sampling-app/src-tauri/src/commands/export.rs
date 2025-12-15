use crate::models::{ExportRequest, ExportResponse};
use crate::sidecar::ipc;

#[tauri::command]
pub async fn export(request: ExportRequest) -> Result<ExportResponse, String> {
    log::info!("📤 Export command invoked for {} distributions", request.distribution_ids.len());

    // Validate request
    request.validate()?;

    let endpoint = "/api/v1/export";

    match ipc::send_request::<ExportRequest, ExportResponse>(endpoint, request).await {
        Ok(response) => {
            log::info!("✅ Export successful: {} rows to {}", response.row_count, response.file_path);
            Ok(response)
        }
        Err(e) => {
            log::error!("❌ Export failed: {}", e);
            Err(format!("Export failed: {}", e))
        }
    }
}
