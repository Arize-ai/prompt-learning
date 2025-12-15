# Quality Validation Checklist: Verbalized Sampling Desktop App

**Purpose**: Pre-release quality gates for production deployment
**Feature**: [spec.md](../spec.md) | [plan.md](../plan.md)
**Created**: 2025-10-16
**Status**: Template (to be validated during Milestone 7 QA)

---

## Security ✅

- [ ] **Stronghold Encryption**: All API keys encrypted via Tauri Stronghold vault with user master password
- [ ] **No Plaintext Storage**: API keys never stored in config files, environment variables, or application state unencrypted
- [ ] **Log Redaction**: All logs show `Authorization: Bearer [REDACTED]` instead of actual keys (validated in diagnostic mode)
- [ ] **UI Masking**: API key fields display `●●●●●●●●` after save; plaintext never shown post-save
- [ ] **IPC Security**: JSON contracts validated on both Tauri and Python sides to prevent injection attacks
- [ ] **Secure Defaults**: Default config files use placeholders (`YOUR_API_KEY_HERE`), never real credentials
- [ ] **Filesystem Permissions**: Stronghold vault files have restrictive permissions (chmod 600 or OS equivalent)
- [ ] **Session Data Sanitization**: Exported session files exclude API keys and sensitive provider config

**Test**: Enter OpenAI key, save, restart app, verify key works but never appears in UI/logs/filesystem unencrypted

---

## Portability ✅

- [ ] **macOS Support**: App runs on macOS 11+ (Intel + Apple Silicon) with native binary
- [ ] **Windows Support**: App runs on Windows 10/11 (x64) with signed executable
- [ ] **Linux Support**: App runs on Ubuntu 20.04+ via AppImage/Flatpak/.deb with all features functional
- [ ] **Cross-Platform UI**: React components render consistently across all three platforms
- [ ] **Path Handling**: File paths (session saves, exports, sidecar binaries) work with OS-specific separators
- [ ] **PyInstaller Bundling**: Python sidecar bundles correctly on all platforms with dependencies included
- [ ] **Platform-Specific Testing**: Stronghold vault, filesystem access, window management tested per OS

**Test**: Build release binaries for macOS/Windows/Linux, verify app launches and completes full workflow on each

---

## Robustness ✅

- [ ] **Graceful Degradation**: When Python sidecar binary missing, display clear error: "Python engine not found. Reinstall application or check sidecar path: [path]"
- [ ] **Sidecar Crash Recovery**: Sidecar crashes trigger automatic restart with user notification; max 3 retries before fallback mode
- [ ] **Health Checks**: Tauri validates sidecar availability via `/health` endpoint before sending commands; timeout=5s
- [ ] **Connection Failures**: Local vLLM endpoint unreachable → clear error with retry/switch-to-API options
- [ ] **Rate Limit Handling**: API rate limits display countdown timer and disable "Verbalize" button until reset
- [ ] **Invalid Input Validation**: k exceeds provider limits → auto-correct to max with warning notification
- [ ] **Schema Mismatch**: Incompatible session version → attempt migration with warnings or fail with actionable message
- [ ] **Disk Space Errors**: Insufficient space during save → preserve in-memory session, prompt user to free space
- [ ] **Normalization Warnings**: Probabilities not summing to 1.0 → normalize and display tooltip with original sum

**Test**: Simulate sidecar crash, missing binary, network failure, rate limit, invalid inputs; verify graceful handling

---

## Performance ✅

- [ ] **API Response Latency**: <2s average end-to-end for k≤10 samples (measured from "Verbalize" click to table render)
- [ ] **Local Inference Latency**: <5s average for k≤10 with local vLLM (measured from command to result display)
- [ ] **Session Load Time**: <2s for sessions with up to 100 distributions (measured from file select to UI render)
- [ ] **Export Speed**: CSV/JSONL export completes in <3s for 1000-distribution sessions
- [ ] **App Startup**: <3s from launch to usable UI (Python sidecar initialization included)
- [ ] **UI Responsiveness**: All interactions <100ms response time (button clicks, table sorts, slider adjustments)
- [ ] **Token Details Rendering**: Expandable rows with token probabilities render in <1s for k≤100
- [ ] **Large Session Handling**: Sessions with 1000+ distributions maintain UI responsiveness without lag
- [ ] **Memory Footprint**: App uses <500MB RAM for typical workflows (10 distributions, k=50 each)

**Test**: Benchmark with timer instrumentation; test edge cases (k=500 local, 1000-distribution session)

---

## UX ✅

- [ ] **Color Contrast**: All text/background combinations meet WCAG AA standards (4.5:1 ratio minimum)
- [ ] **Keyboard Navigation**: Full app usable without mouse (Tab, Enter, Esc, arrow keys for table/chart)
- [ ] **Focus Indicators**: Visible focus outlines on all interactive elements (buttons, inputs, dropdowns)
- [ ] **Screen Reader Support**: Semantic HTML with ARIA labels for charts, tables, and dynamic content
- [ ] **Error Messages**: All errors include actionable guidance (e.g., "Check API key in Settings" not "Auth failed")
- [ ] **Loading States**: Spinners/progress indicators for all async operations (verbalize, sample, export)
- [ ] **Tooltips**: Contextual help on hover for technical terms (τ, entropy, seed, normalization)
- [ ] **Responsive Layout**: UI adapts to minimum 1280x720 resolution without horizontal scroll
- [ ] **Theme Support**: Light/dark/system themes apply consistently across all panels

**Test**: Navigate entire app with keyboard only; test with screen reader (NVDA/VoiceOver); validate contrast ratios

---

## Logging ✅

- [ ] **Structured JSON Logs**: All sidecar I/O logged in JSON format with timestamp, request_id, operation, payload (redacted)
- [ ] **Log Levels**: Support DEBUG/INFO/WARN/ERROR levels; default to INFO in production
- [ ] **Diagnostic Mode**: Settings panel enables verbose logging with sidecar request/response bodies (API keys redacted)
- [ ] **Log Viewer**: In-app log viewer with filtering (level, timestamp range, keyword search) and export
- [ ] **Rotation**: Logs auto-rotate at 10MB with max 5 historical files retained
- [ ] **Sidecar Capture**: Python stdout/stderr captured and surfaced in Tauri UI log viewer
- [ ] **Performance Metrics**: Logs include latency measurements for API calls, sidecar IPC, UI render times
- [ ] **Error Context**: Error logs include stack traces (sanitized), operation context, and recovery actions taken

**Test**: Enable diagnostic logging, run full workflow, verify JSON format and redaction; export logs and parse with `jq`

---

## Export ✅

- [ ] **JSONL Format**: Each line is valid JSON; schema matches documented contract (prompt, completion, probability, parameters, trace_metadata)
- [ ] **CSV Format**: Standard comma-separated with headers; opens in Excel/Google Sheets without errors
- [ ] **Schema Compliance**: Exported files validated against `/schemas/export.v1.json` schema
- [ ] **Precision**: Probability values maintain 6 decimal places in both formats
- [ ] **Trace Metadata**: Exports include model, API latency, token_count, k, τ, temperature, seed, API version, timestamp
- [ ] **Multi-Distribution Export**: "Export All" creates single file with clear identifiers (distribution_id, prompt hash)
- [ ] **File Encoding**: UTF-8 encoding with BOM for Excel compatibility; handles non-ASCII characters correctly
- [ ] **Batch Export**: 1000-distribution sessions export without memory issues or timeouts

**Test**: Export single/multiple distributions to CSV/JSONL; validate with schema validator; open in Excel/Python/R

---

## Offline Mode ✅

- [ ] **vLLM Connectivity**: Local endpoint reachable at configured URL (default: `http://localhost:8000`)
- [ ] **Full Feature Parity**: Verbalize, sample, export, session save/load all work offline without network
- [ ] **No Network Calls**: Validated via network traffic monitoring (Wireshark/Charles Proxy) during offline operations
- [ ] **Provider Detection**: App correctly identifies local vLLM vs API providers; disables network features appropriately
- [ ] **Model Selection**: Local models listed from vLLM `/v1/models` endpoint; cached for offline availability
- [ ] **Error Handling**: Network disconnect during API mode → graceful fallback with "Switch to Offline Mode?" prompt
- [ ] **k Limit Enforcement**: Local vLLM enforces k≤500; API mode enforces k≤100
- [ ] **Offline Indicator**: UI displays clear "Offline Mode" badge when using local vLLM

**Test**: Disconnect network, configure local vLLM, complete full workflow; monitor traffic to confirm zero external calls

---

## Reproducibility ✅

- [ ] **Deterministic Sampling**: Same seed + parameters → identical distribution 100% of the time (tested across 100 runs)
- [ ] **Session Replay**: "Replay" feature reproduces exact results from saved session (same p-values, completion order)
- [ ] **Parameter Fidelity**: Loaded sessions restore k, τ, temperature, seed, model, provider exactly as saved
- [ ] **Cross-Platform Consistency**: Same seed on macOS/Windows/Linux produces identical distributions (verified)
- [ ] **Version Stability**: v1.x sessions load correctly in v1.y (backward compatibility within major version)
- [ ] **Probability Precision**: Saved/loaded p-values maintain 6 decimal places without rounding errors
- [ ] **Random Seed Handling**: Null seed generates new random seed on each run; integer seed is deterministic
- [ ] **Model Version Tracking**: Session metadata includes model version; warns if replaying with different version

**Test**: Generate distribution with seed=42, save session, reload, replay; verify identical output; test across platforms

---

## Extensibility ✅

- [ ] **Provider Plugin System**: New provider addable via `/vs_bridge/providers/` without modifying core handlers
- [ ] **Interface Compliance**: All providers implement common interface (authenticate, generate_completions, health_check)
- [ ] **JSON Contract Versioning**: Schema changes bump version (`contract.v2.json`); old versions supported for 1 major release
- [ ] **Backend Registration**: New backends registered in `vs_bridge/config.py` with zero changes to Rust/React layers
- [ ] **UI Provider Dropdown**: Settings panel auto-populates from available providers; no hardcoded list
- [ ] **Custom Endpoints**: Generic OpenAI-compatible provider supports arbitrary endpoint URLs
- [ ] **Model Discovery**: New providers' models auto-discovered via standardized `/v1/models` endpoint
- [ ] **Parameter Mapping**: Provider-specific parameters (e.g., Anthropic's `max_tokens_to_sample`) mapped transparently

**Test**: Add mock provider plugin, register in config, verify appears in UI without core code changes; test custom endpoint

---

## Constitution Compliance ✅

- [ ] **Offline-First (Principle I)**: All features work offline with local vLLM; API mode is optional enhancement
- [ ] **Security (Principle II)**: Stronghold encrypts all secrets; logs/UI never expose plaintext credentials
- [ ] **Pluggable Architecture (Principle III)**: Python `verbalized_sampling` remains unmodified black box; JSON contracts enforce boundaries
- [ ] **Test-First (Principle IV)**: Unit tests for handlers, integration tests for IPC, contract tests for JSON schemas
- [ ] **Observability (Principle V)**: Structured logs, in-app viewer, exportable distributions, actionable errors
- [ ] **Desktop-First (Principle VI)**: Tauri 2 cross-platform; Rust orchestrates, Python owns inference; sidecar pattern
- [ ] **Module Independence (Principle VII)**: Each module testable in isolation; DAG dependencies; one-person maintainable

**Test**: Constitution audit validates all 7 principles; review plan.md Constitution Check section for per-principle tests

---

## Success Criteria Validation (from spec.md)

- [ ] **SC-001**: Distributions generated in <10s (API) / <5s (local) for k=10
- [ ] **SC-002**: Probability precision to 6 decimals; normalized sums within 0.001 of 1.0
- [ ] **SC-003**: Deterministic replay 100% identical with same seed
- [ ] **SC-004**: Session save/load <2s for 100-distribution sessions
- [ ] **SC-005**: Exported files compatible with Excel/pandas/R without preprocessing
- [ ] **SC-006**: Zero API key exposure (logs/UI/errors/network)
- [ ] **SC-007**: Offline mode full feature parity
- [ ] **SC-008**: 95% of errors have actionable messages
- [ ] **SC-009**: Core workflow <30s after initial setup
- [ ] **SC-010**: Comparative analysis renders <3s for 10 comparisons (optional feature)
- [ ] **SC-011**: App startup <3s
- [ ] **SC-012**: 1000-distribution sessions maintain <100ms UI responsiveness
- [ ] **SC-013**: Token details render <1s for k≤100
- [ ] **SC-014**: Pin toggle prevents auto-refresh 100% when active

**Test**: Run acceptance tests from spec.md User Stories; validate all 14 success criteria against benchmarks

---

## Pre-Release Gates

**All checklist items MUST pass before v1.0.0 release:**

1. ✅ **Security Audit**: External review of Stronghold implementation, log redaction, IPC validation
2. ✅ **Cross-Platform Build**: Signed binaries for macOS/Windows/Linux with zero critical bugs
3. ✅ **Performance Benchmarks**: All latency/throughput metrics meet or exceed success criteria
4. ✅ **Accessibility Testing**: WCAG AA compliance verified; keyboard navigation complete
5. ✅ **Documentation**: User guide, API docs, troubleshooting guide published
6. ✅ **Backward Compatibility**: v1.0 sessions loadable in future v1.x releases

**Validation Process**:
- Milestone 7 (QA) dedicates 4 days to checklist validation
- Each item tested with pass/fail evidence documented
- Critical failures block release; must be resolved or mitigated
- Non-critical issues logged as post-v1.0 enhancements

---

## Testing Instructions

### Manual Test Scenarios

**Scenario 1: End-to-End Offline Workflow**
1. Disconnect network
2. Configure local vLLM endpoint (`http://localhost:8000`)
3. Enter prompt "Explain quantum computing" with k=10, temperature=0.8, seed=42
4. Click "Verbalize" → verify 10 completions with probabilities summing to ~1.0
5. Click "Sample" → verify deterministic selection (same completion each time with seed=42)
6. Export to CSV → verify file contains trace metadata (model, latency, token_count)
7. Save session → reload session → replay → verify identical distribution
8. ✅ Pass if zero network calls detected and all features work

**Scenario 2: API Provider Security**
1. Open Settings, enter OpenAI API key in masked field
2. Click "Save" → verify key encrypts (check Stronghold vault file)
3. Restart app → verify key field shows `●●●●●●●●`
4. Enable diagnostic logging, run verbalize with API mode
5. Check logs → verify `Authorization: Bearer [REDACTED]`, not actual key
6. Export session → verify API key not in exported JSON
7. ✅ Pass if key never appears in plaintext post-save

**Scenario 3: Sidecar Robustness**
1. Start app normally (sidecar healthy)
2. Kill Python sidecar process manually (simulate crash)
3. Attempt "Verbalize" → verify auto-restart with notification
4. Rename sidecar binary to break path
5. Restart app → verify clear error with binary path shown
6. ✅ Pass if graceful recovery/error handling works

**Scenario 4: Cross-Platform Consistency**
1. Generate distribution with seed=100, k=20, temperature=1.0 on macOS
2. Save session to cloud/USB drive
3. Load session on Windows → replay → verify identical p-values
4. Repeat on Linux → verify same results
5. ✅ Pass if all three platforms produce byte-identical distributions

### Automated Test Coverage

- **Unit Tests**: `vs_bridge/handlers/`, `src-tauri/src/commands/`
- **Integration Tests**: IPC contract validation, sidecar lifecycle, Stronghold encryption
- **Contract Tests**: JSON schema compliance (request/response pairs)
- **Performance Tests**: Latency benchmarks for SC-001, SC-004, SC-009, SC-011, SC-012
- **Security Tests**: Log redaction, API key masking, session data sanitization
- **UI Tests**: Playwright/Tauri-driver for keyboard navigation, accessibility, workflows

**Run All Tests**:
```bash
# Backend tests
cd vs_bridge && pytest tests/ --cov
cd src-tauri && cargo test

# Frontend tests
cd ui && npm test

# Contract tests
./scripts/validate_contracts.sh

# E2E tests
npm run test:e2e
```

---

## Sign-Off

**QA Engineer**: ________________ Date: ________
**Security Reviewer**: ________________ Date: ________
**Product Owner**: ________________ Date: ________

**Release Decision**: [ ] APPROVED [ ] BLOCKED (reason: _____________)

---

**Version**: 1.0.0 | **Last Updated**: 2025-10-16
