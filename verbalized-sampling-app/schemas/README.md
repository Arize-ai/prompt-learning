# JSON Contract Schemas

This directory contains versioned JSON schemas that define the contract between the Tauri Rust backend and the Python sidecar service.

## Schema Versioning

- **v1/**: Version 1 schemas (current)
- Breaking changes require a new version directory (v2/, v3/, etc.)
- Backward compatibility maintained within major versions

## Schemas to be Created in Phase 2

- `verbalize-request.json`: Request schema for verbalize endpoint
- `verbalize-response.json`: Response schema for verbalize endpoint
- `sample-request.json`: Request schema for sample endpoint
- `sample-response.json`: Response schema for sample endpoint
- `export-request.json`: Request schema for export endpoint
- `export-response.json`: Response schema for export endpoint
- `session-save-request.json`: Request schema for session save
- `session-load-response.json`: Response schema for session load

## Compliance

All IPC communication between Tauri and Python must validate against these schemas per Constitution Principle III (Pluggable Architecture).
