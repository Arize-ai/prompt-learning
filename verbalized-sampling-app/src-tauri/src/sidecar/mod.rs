pub mod manager;
pub mod ipc;

pub use manager::{start_sidecar, health_check, stop_sidecar, restart_sidecar, SidecarHandle};
pub use ipc::{send_request, get_request, SidecarRequest, SidecarResponse};
