use tauri::AppHandle;
use tauri::async_runtime::spawn;
use tauri_plugin_shell::{ShellExt, process::CommandEvent};
use std::sync::{Arc, Mutex};
use std::time::Duration;

/// Sidecar process handle for lifecycle management
pub struct SidecarHandle {
    pub process: Arc<Mutex<Option<tauri::async_runtime::JoinHandle<()>>>>,
}

impl SidecarHandle {
    pub fn new() -> Self {
        Self {
            process: Arc::new(Mutex::new(None)),
        }
    }
}

/// Start the Python sidecar service
/// Returns a handle for lifecycle management
pub async fn start_sidecar(app: AppHandle) -> Result<(), String> {
    log::info!("🚀 Starting Python sidecar service...");

    // Get the sidecar command
    let sidecar_command = app
        .shell()
        .sidecar("vs-bridge")
        .map_err(|e| format!("Failed to get sidecar command: {}", e))?;

    // Spawn the sidecar process
    let (mut rx, child) = sidecar_command
        .spawn()
        .map_err(|e| format!("Failed to spawn sidecar: {}", e))?;

    log::info!("✅ Sidecar process spawned with PID: {}", child.pid());

    // Monitor sidecar output in background
    spawn(async move {
        while let Some(event) = rx.recv().await {
            match event {
                CommandEvent::Stdout(line) => {
                    log::debug!("Sidecar stdout: {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Stderr(line) => {
                    log::warn!("Sidecar stderr: {}", String::from_utf8_lossy(&line));
                }
                CommandEvent::Error(err) => {
                    log::error!("Sidecar error: {}", err);
                }
                CommandEvent::Terminated(payload) => {
                    log::warn!("Sidecar terminated with code: {:?}", payload.code);
                }
                _ => {}
            }
        }
    });

    Ok(())
}

/// Perform health check on the sidecar service
/// Polls the /api/v1/health endpoint until 200 OK or timeout (5 seconds)
pub async fn health_check() -> Result<(), String> {
    log::info!("🏥 Performing sidecar health check...");

    let client = reqwest::Client::new();
    let health_url = "http://127.0.0.1:8765/api/v1/health";
    let timeout = Duration::from_secs(5);
    let start = std::time::Instant::now();

    while start.elapsed() < timeout {
        match client.get(health_url).timeout(Duration::from_secs(1)).send().await {
            Ok(response) if response.status().is_success() => {
                log::info!("✅ Health check passed in {:?}", start.elapsed());
                return Ok(());
            }
            Ok(response) => {
                log::debug!("Health check returned status: {}", response.status());
            }
            Err(e) => {
                log::debug!("Health check attempt failed: {}", e);
            }
        }

        tokio::time::sleep(Duration::from_millis(200)).await;
    }

    Err(format!("Health check timeout after {:?}", timeout))
}

/// Stop the sidecar service gracefully via HTTP
pub async fn stop_sidecar() -> Result<(), String> {
    log::info!("🛑 Stopping sidecar service...");

    let client = reqwest::Client::new();
    let shutdown_url = "http://127.0.0.1:8765/api/v1/shutdown";

    match client
        .post(shutdown_url)
        .timeout(Duration::from_secs(3))
        .send()
        .await
    {
        Ok(_) => {
            log::info!("✅ Sidecar shutdown signal sent");
            Ok(())
        }
        Err(e) => {
            log::warn!("Failed to send shutdown signal: {}", e);
            Err(format!("Shutdown failed: {}", e))
        }
    }
}

/// Restart the sidecar service (stop + start)
/// Used for crash detection and recovery
pub async fn restart_sidecar(app: AppHandle) -> Result<(), String> {
    log::info!("🔄 Restarting sidecar service...");

    // Attempt graceful shutdown (ignore errors)
    let _ = stop_sidecar().await;

    // Wait for shutdown
    tokio::time::sleep(Duration::from_secs(1)).await;

    // Start fresh instance
    start_sidecar(app).await?;

    // Verify health
    health_check().await?;

    log::info!("✅ Sidecar restarted successfully");
    Ok(())
}
