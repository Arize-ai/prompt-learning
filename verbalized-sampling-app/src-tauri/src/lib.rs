mod sidecar;
pub mod models;

use tauri::Manager;

// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! You've been greeted from Rust!", name)
}

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_store::Builder::default().build())
        .plugin(tauri_plugin_stronghold::Builder::new(|password| {
            // Simple password hash function for development
            // In production, use a proper password from user
            use std::collections::hash_map::DefaultHasher;
            use std::hash::{Hash, Hasher};
            let mut hasher = DefaultHasher::new();
            password.hash(&mut hasher);
            hasher.finish().to_ne_bytes().to_vec()
        }).build())
        .setup(|app| {
            // Start sidecar service on application startup
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                log::info!("🚀 Initializing sidecar service...");

                match sidecar::start_sidecar(app_handle.clone()).await {
                    Ok(_) => {
                        log::info!("✅ Sidecar started, performing health check...");

                        match sidecar::health_check().await {
                            Ok(_) => {
                                log::info!("✅ Sidecar is healthy and ready");
                            }
                            Err(e) => {
                                log::error!("❌ Health check failed: {}", e);
                                // Attempt restart on health check failure
                                if let Err(restart_err) = sidecar::restart_sidecar(app_handle).await {
                                    log::error!("❌ Sidecar restart failed: {}", restart_err);
                                }
                            }
                        }
                    }
                    Err(e) => {
                        log::error!("❌ Failed to start sidecar: {}", e);
                    }
                }
            });

            Ok(())
        })
        .on_page_load(|window, _payload| {
            log::debug!("Page loaded in window: {}", window.label());
        })
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
