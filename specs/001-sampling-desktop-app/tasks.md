# Tasks: Verbalized Sampling Desktop App

**Input**: Design documents from `/specs/001-sampling-desktop-app/`
**Prerequisites**: plan.md (complete), spec.md (complete), clarifications.md (complete)

**Tests**: Tests are included per constitution requirement (Principle IV: Test-First Development). All contract tests, integration tests, and E2E tests are mandatory.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions
- **Desktop app**: `src-tauri/` (Rust backend), `ui/` (React frontend), `vs_bridge/` (Python sidecar)
- **Schemas**: `schemas/v1/` (JSON contracts)
- **Tests**: `tests/contract/`, `tests/integration/`, `tests/e2e/`, `tests/unit/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, Tauri scaffold, and build pipeline setup

- [ ] T001 Initialize Tauri 2 project with React + TypeScript using `npm create tauri-app@latest`
- [ ] T002 Configure `src-tauri/tauri.conf.json` with shell plugin for sidecar execution
- [ ] T003 [P] Add Tauri Store plugin to `src-tauri/Cargo.toml` for persistent preferences
- [ ] T004 [P] Add Tauri Stronghold plugin to `src-tauri/Cargo.toml` for secret storage
- [ ] T005 Configure sidecar binary paths in `src-tauri/tauri.conf.json`: `binaries/vs-bridge-{target}`
- [ ] T006 Set Tauri capabilities in `src-tauri/capabilities/default.json`: filesystem, shell, store
- [ ] T007 [P] Create React app structure: `ui/src/components/`, `ui/src/hooks/`, `ui/src/types/`, `ui/src/utils/`
- [ ] T008 [P] Add Recharts dependency to `ui/package.json`: `npm install recharts`
- [ ] T009 [P] Configure Vite for Tauri in `ui/vite.config.ts` with Tauri plugin
- [ ] T010 Create build script `scripts/build-sidecar.sh` (placeholder for Phase 2)
- [ ] T011 [P] Create `.gitignore` entries: `*.stronghold`, `dist/`, `target/`, `node_modules/`, `binaries/`
- [ ] T012 [P] Add Python project structure: `vs_bridge/handlers/`, `vs_bridge/models.py`, `vs_bridge/requirements.txt`

**Checkpoint**: Tauri scaffold complete, React structure ready, build pipeline initialized

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Sidecar Infrastructure

- [ ] T013 Create FastAPI server in `vs_bridge/main.py` with health check endpoint `GET /api/v1/health`
- [ ] T014 Add CORS middleware in `vs_bridge/main.py` for localhost Tauri webview
- [ ] T015 Configure Uvicorn server in `vs_bridge/main.py` on `localhost:8765`
- [ ] T016 Create `vs_bridge/requirements.txt` with: `fastapi`, `uvicorn`, `pydantic`, `verbalized_sampling`
- [ ] T017 Create PyInstaller spec file `vs_bridge.spec` for one-file executable with hidden imports
- [ ] T018 Implement `scripts/build-sidecar.sh` to build PyInstaller binary for current platform
- [ ] T019 Test sidecar binary execution: verify FastAPI starts and health check responds in <1s

### Sidecar Lifecycle Management

- [ ] T020 Create `src-tauri/src/sidecar/manager.rs` with `start_sidecar()` function using Tauri shell plugin
- [ ] T021 Implement `health_check()` in `src-tauri/src/sidecar/manager.rs`: poll `/api/v1/health` until 200 OK (5s timeout)
- [ ] T022 Implement `stop_sidecar()` in `src-tauri/src/sidecar/manager.rs`: graceful shutdown via HTTP
- [ ] T023 Implement `restart_sidecar()` in `src-tauri/src/sidecar/manager.rs`: stop + start on crash detection
- [ ] T024 Create `src-tauri/src/sidecar/ipc.rs` with `send_request(endpoint, payload)` HTTP client
- [ ] T025 Add error handling in `src-tauri/src/sidecar/ipc.rs`: timeout (30s), connection refused → restart trigger
- [ ] T026 Register sidecar lifecycle in `src-tauri/src/lib.rs`: `setup` hook starts sidecar, `cleanup` hook stops

### JSON Contract Schemas

- [ ] T027 [P] Create `schemas/v1/verbalize-request.json` with: prompt, k, tau, temperature, seed, model, provider, include_token_probabilities
- [ ] T028 [P] Create `schemas/v1/verbalize-response.json` with: distribution_id, completions[], trace_metadata, timestamp
- [ ] T029 [P] Create `schemas/v1/sample-request.json` with: distribution_id, seed
- [ ] T030 [P] Create `schemas/v1/sample-response.json` with: selected_completion, selection_index
- [ ] T031 [P] Create `schemas/v1/export-request.json` with: distribution_ids[], format, include_metadata, output_path
- [ ] T032 [P] Create `schemas/v1/export-response.json` with: file_path, row_count, file_size_bytes
- [ ] T033 [P] Create `schemas/v1/session-save-request.json` with: distributions[], notes, output_path
- [ ] T034 [P] Create `schemas/v1/session-load-response.json` with: session object (id, distributions, app_version, etc.)
- [ ] T035 Create `schemas/README.md` documenting schema versioning strategy and compatibility rules

### Rust Type Definitions

- [ ] T036 Create `src-tauri/src/models.rs` with Rust structs: `VerbParams`, `DistributionResponse`, `CompletionResponse`, `ExportResponse`
- [ ] T037 Derive `Serialize`, `Deserialize` (serde) for all structs in `src-tauri/src/models.rs` to match JSON schemas
- [ ] T038 Add validation logic in `src-tauri/src/models.rs`: k ≤ 100 for API, k ≤ 500 for local vLLM

### Python Contract Models

- [ ] T039 Create Pydantic models in `vs_bridge/models.py`: `VerbRequest`, `VerbResponse`, `SampleRequest`, `SampleResponse`
- [ ] T040 Add Pydantic models in `vs_bridge/models.py`: `ExportRequest`, `ExportResponse`, `SessionSaveRequest`, `SessionLoadResponse`
- [ ] T041 Add JSON schema validation decorators to all Pydantic models in `vs_bridge/models.py`

### TypeScript Type Definitions

- [ ] T042 Generate TypeScript types in `ui/src/types/contracts.ts` from JSON schemas using `scripts/generate-types.sh`
- [ ] T043 Create UI state models in `ui/src/types/models.ts`: Distribution, Completion, Session, ProviderConfig

### Contract Testing Infrastructure

- [ ] T044 [P] Create contract test template in `tests/contract/test_verbalize_contract.py` (Python side schema validation)
- [ ] T045 [P] Create contract test template in `tests/contract/test_verbalize_contract.rs` (Rust side schema validation)
- [ ] T046 Create `scripts/validate-contracts.sh` for CI schema validation checks

**Checkpoint**: Foundation ready - sidecar working, contracts defined, types generated. User story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Basic Distribution Exploration (Priority: P1) 🎯 MVP

**Goal**: Enable researchers to visualize probability distributions of LLM completions with prompt input controls, sortable table, probability bar chart, token details toggle, and pin-to-analyze feature.

**Independent Test**: Enter prompt "Explain quantum entanglement", set k=5, temperature=0.8, click "Verbalize" → see table + chart of 5 weighted completions with p-values summing to ~1.0.

### Tests for User Story 1

**NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T047 [P] [US1] Contract test for verbalize endpoint in `tests/contract/test_verbalize_contract.py`
- [ ] T048 [P] [US1] Contract test for verbalize endpoint in `tests/contract/test_verbalize_contract.rs`
- [ ] T049 [P] [US1] Integration test for offline verbalize in `tests/integration/test_offline_mode.py`
- [ ] T050 [P] [US1] E2E test for core workflow in `tests/e2e/test_core_workflow.spec.ts` (Playwright)

### Python Sidecar Implementation for User Story 1

- [ ] T051 [US1] Create verbalize handler in `vs_bridge/handlers/verbalize_handler.py`: invoke `verbalized_sampling` package
- [ ] T052 [US1] Add endpoint `POST /api/v1/verbalize` in `vs_bridge/main.py` calling verbalize handler
- [ ] T053 [US1] Implement token-level probability extraction in `vs_bridge/handlers/verbalize_handler.py` (optional field)
- [ ] T054 [US1] Add probability normalization logic in `vs_bridge/handlers/verbalize_handler.py` if sum ≠ 1.0
- [ ] T055 [US1] Add trace metadata collection in `vs_bridge/handlers/verbalize_handler.py`: model, latency, token_count, API version

### Rust Commands for User Story 1

- [ ] T056 [US1] Implement `verbalize` command in `src-tauri/src/commands/verbalize.rs`: validate params, call sidecar
- [ ] T057 [US1] Add k validation in `src-tauri/src/commands/verbalize.rs`: check provider type (API ≤100, local ≤500)
- [ ] T058 [US1] Register `verbalize` command in `src-tauri/src/lib.rs` invoke handler
- [ ] T059 [US1] Add error mapping in `src-tauri/src/commands/verbalize.rs`: timeout → restart sidecar, rate limit → actionable error

### React Components for User Story 1

- [ ] T060 [P] [US1] Create `ui/src/components/PromptPanel.tsx`: prompt textarea, k/temperature/tau/seed inputs, model/provider dropdowns
- [ ] T061 [P] [US1] Create `ui/src/components/DistributionPanel.tsx`: container for table + chart + toggles
- [ ] T062 [US1] Create `ui/src/components/DistributionTable.tsx`: sortable table (rank, completion, probability columns)
- [ ] T063 [US1] Add expandable rows to `ui/src/components/DistributionTable.tsx` for token-level probabilities
- [ ] T064 [US1] Add sort functionality to `ui/src/components/DistributionTable.tsx`: click header to sort by rank/probability
- [ ] T065 [US1] Create `ui/src/components/ProbabilityChart.tsx`: Recharts `<BarChart>` with `<Bar dataKey="probability">`
- [ ] T066 [US1] Add custom tooltips to `ui/src/components/ProbabilityChart.tsx`: show p-value + text preview on hover
- [ ] T067 [US1] Performance test `ui/src/components/ProbabilityChart.tsx`: render k=500 bars in <100ms

### React Hooks for User Story 1

- [ ] T068 [US1] Implement `ui/src/hooks/useVerbalize.ts`: call `invoke('verbalize')`, manage loading/distribution/error state
- [ ] T069 [US1] Add auto-refresh logic to `ui/src/hooks/useVerbalize.ts`: update distribution state when response received (unless pinned)
- [ ] T070 [US1] Add "Pin Current View" toggle state to `ui/src/hooks/useVerbalize.ts`: disable auto-refresh when active

### UI Integration for User Story 1

- [ ] T071 [US1] Wire "Verbalize" button in `ui/src/components/PromptPanel.tsx` to `useVerbalize` hook
- [ ] T072 [US1] Add "Show Token Details" toggle to `ui/src/components/DistributionPanel.tsx` controlling table expansion
- [ ] T073 [US1] Add "Pin Current View" toggle to `ui/src/components/DistributionPanel.tsx` controlling auto-refresh
- [ ] T074 [US1] Add loading spinner to `ui/src/components/PromptPanel.tsx` during verbalize operation
- [ ] T075 [US1] Add error display to `ui/src/components/PromptPanel.tsx`: show actionable messages (e.g., "Rate limit exceeded for OpenAI. Retry in 45 seconds")
- [ ] T076 [US1] Test offline mode: disconnect network, use local vLLM, verify full verbalize workflow works

**Checkpoint**: User Story 1 complete - prompt input, verbalize, visualize distribution (table + chart), token details, pin view. Independently testable.

---

## Phase 4: User Story 2 - Weighted Sampling Execution (Priority: P2)

**Goal**: Enable users to sample one completion from distribution based on probabilities, with deterministic (seed-based) and random sampling modes.

**Independent Test**: Load pre-generated distribution (or use US1), click "Sample", verify one completion is highlighted according to probability weights.

### Tests for User Story 2

- [ ] T077 [P] [US2] Contract test for sample endpoint in `tests/contract/test_sample_contract.py`
- [ ] T078 [P] [US2] Contract test for sample endpoint in `tests/contract/test_sample_contract.rs`
- [ ] T079 [P] [US2] Integration test for deterministic sampling in `tests/integration/test_sampling.py`

### Python Sidecar Implementation for User Story 2

- [ ] T080 [US2] Create sample handler in `vs_bridge/handlers/sample_handler.py`: weighted random selection based on p-values
- [ ] T081 [US2] Add endpoint `POST /api/v1/sample` in `vs_bridge/main.py` calling sample handler
- [ ] T082 [US2] Implement seed-based deterministic sampling in `vs_bridge/handlers/sample_handler.py`: same seed → same completion
- [ ] T083 [US2] Add random seed generation in `vs_bridge/handlers/sample_handler.py`: when seed=null, use random

### Rust Commands for User Story 2

- [ ] T084 [US2] Implement `sample` command in `src-tauri/src/commands/sample.rs`: accept distribution_id, seed, call sidecar
- [ ] T085 [US2] Register `sample` command in `src-tauri/src/lib.rs` invoke handler
- [ ] T086 [US2] Add error handling in `src-tauri/src/commands/sample.rs`: distribution not found → clear error

### React Hooks for User Story 2

- [ ] T087 [US2] Implement `ui/src/hooks/useSample.ts`: call `invoke('sample')`, manage selected completion state
- [ ] T088 [US2] Add highlight logic to `ui/src/hooks/useSample.ts`: update selected_index in distribution state

### UI Integration for User Story 2

- [ ] T089 [US2] Add "Sample" button to `ui/src/components/PromptPanel.tsx` calling `useSample` hook
- [ ] T090 [US2] Add selected completion highlighting to `ui/src/components/DistributionTable.tsx`: row background color change
- [ ] T091 [US2] Add "Export Sample" button to `ui/src/components/DistributionPanel.tsx`: export selected completion with metadata
- [ ] T092 [US2] Test deterministic sampling: seed=42, sample 10 times → verify same completion selected

**Checkpoint**: User Story 2 complete - weighted sampling with deterministic/random modes, highlighting. Works independently or combined with US1.

---

## Phase 5: User Story 5 - Provider Configuration & Security (Priority: P2)

**Goal**: Enable secure configuration of API keys (OpenAI, Anthropic, Cohere) and local endpoints with Stronghold encryption, UI masking, log redaction.

**Independent Test**: Open Settings, enter OpenAI key, save, restart app, verify (1) key persists, (2) key works for API calls, (3) key never appears in logs/UI after save.

### Tests for User Story 5

- [ ] T093 [P] [US5] Integration test for Stronghold encryption in `tests/integration/test_stronghold_security.rs`
- [ ] T094 [P] [US5] Integration test for log redaction in `tests/integration/test_log_redaction.py`
- [ ] T095 [P] [US5] Integration test for connection testing in `tests/integration/test_connection.py`

### Stronghold Integration

- [ ] T096 [US5] Initialize Stronghold vault in `src-tauri/src/lib.rs`: prompt for master password, create vault at `$APP_DATA/verbalized_sampling.stronghold`
- [ ] T097 [US5] Implement `save_api_key` command in `src-tauri/src/commands/settings.rs`: store key in Stronghold with ID `api_key:{provider}`
- [ ] T098 [US5] Implement `get_api_key` command in `src-tauri/src/commands/settings.rs`: retrieve key from vault (never return to React)
- [ ] T099 [US5] Add log redaction in `src-tauri/src/commands/settings.rs`: replace key with `[REDACTED]` in debug output
- [ ] T100 [US5] Register settings commands in `src-tauri/src/lib.rs`: `save_api_key`, `get_api_key`, `test_connection`

### Python Sidecar Security

- [ ] T101 [US5] Modify verbalize endpoint in `vs_bridge/handlers/verbalize_handler.py` to accept API key in request header (from Rust, not React)
- [ ] T102 [US5] Add FastAPI middleware in `vs_bridge/main.py` to redact `Authorization: Bearer [REDACTED]` in logs
- [ ] T103 [US5] Create connection test handler in `vs_bridge/handlers/connection_handler.py`: verify key with provider API
- [ ] T104 [US5] Add endpoint `POST /api/v1/test_connection` in `vs_bridge/main.py` calling connection handler

### React Settings UI

- [ ] T105 [P] [US5] Create `ui/src/components/SettingsPanel.tsx`: provider dropdowns, API key inputs (masked), endpoint URL input
- [ ] T106 [US5] Implement masked key input in `ui/src/components/SettingsPanel.tsx`: display "●●●●●●●●" with "Change" button
- [ ] T107 [US5] Add "Save" button to `ui/src/components/SettingsPanel.tsx`: call `invoke('save_api_key')`
- [ ] T108 [US5] Add "Test Connection" button to `ui/src/components/SettingsPanel.tsx`: call `invoke('test_connection')`, display status
- [ ] T109 [US5] Add theme selector to `ui/src/components/SettingsPanel.tsx`: light/dark/system modes using Tauri Store
- [ ] T110 [US5] Add diagnostic logging toggle to `ui/src/components/SettingsPanel.tsx`: enable/disable verbose logs

### React Hook for Settings

- [ ] T111 [US5] Implement `ui/src/hooks/useSettings.ts`: manage provider configs, API keys, theme, diagnostic settings
- [ ] T112 [US5] Add Tauri Store persistence in `ui/src/hooks/useSettings.ts`: save/load theme, default provider, k value

### Security Validation

- [ ] T113 [US5] Test key encryption: save key, inspect Stronghold vault file → verify unreadable without master password
- [ ] T114 [US5] Test key masking: reopen Settings after save → verify "●●●●●●●●" displayed, not plaintext
- [ ] T115 [US5] Test log redaction: enable diagnostic logs, run verbalize → verify "Authorization: Bearer [REDACTED]" in logs
- [ ] T116 [US5] Test connection validation: enter invalid key → verify clear error "Invalid API key for OpenAI. Check key in Settings"

**Checkpoint**: User Story 5 complete - Stronghold-encrypted secrets, masked UI, log redaction, connection testing. Security validated.

---

## Phase 6: User Story 3 - Session Persistence & Replay (Priority: P2)

**Goal**: Enable saving/loading sessions with all distributions, prompts, parameters for reproducibility and collaboration.

**Independent Test**: Create 3 distributions, save session, close app, reopen, load session → verify exact reproduction of all distributions and parameters.

### Tests for User Story 3

- [ ] T117 [P] [US3] Contract test for session save in `tests/contract/test_session_contract.py`
- [ ] T118 [P] [US3] Contract test for session load in `tests/contract/test_session_contract.rs`
- [ ] T119 [P] [US3] E2E test for session replay in `tests/e2e/test_session_replay.spec.ts`

### Python Sidecar Implementation for User Story 3

- [ ] T120 [US3] Create session save handler in `vs_bridge/handlers/session_handler.py`: serialize distributions to JSON, write to file
- [ ] T121 [US3] Create session load handler in `vs_bridge/handlers/session_handler.py`: read JSON, deserialize to session object
- [ ] T122 [US3] Add endpoint `POST /api/v1/session/save` in `vs_bridge/main.py` calling session save handler
- [ ] T123 [US3] Add endpoint `POST /api/v1/session/load` in `vs_bridge/main.py` calling session load handler
- [ ] T124 [US3] Add version check in `vs_bridge/handlers/session_handler.py`: detect schema mismatch, attempt migration or warn

### Rust Commands for User Story 3

- [ ] T125 [US3] Implement `save_session` command in `src-tauri/src/commands/session.rs`: accept distributions[], path, call sidecar
- [ ] T126 [US3] Implement `load_session` command in `src-tauri/src/commands/session.rs`: read file, return session object
- [ ] T127 [US3] Register session commands in `src-tauri/src/lib.rs`: `save_session`, `load_session`
- [ ] T128 [US3] Add error handling in `src-tauri/src/commands/session.rs`: file not found → clear error, disk full → actionable message

### React Components for User Story 3

- [ ] T129 [P] [US3] Create `ui/src/components/SessionManager.tsx`: "Save Session", "Load Session", "Replay" buttons
- [ ] T130 [US3] Add file picker integration to `ui/src/components/SessionManager.tsx` for save/load dialogs
- [ ] T131 [US3] Implement replay logic in `ui/src/components/SessionManager.tsx`: call `invoke('verbalize')` with saved params + seed

### React Hook for Sessions

- [ ] T132 [US3] Implement `ui/src/hooks/useSession.ts`: manage session state (distributions, metadata)
- [ ] T133 [US3] Add `saveSession` function to `ui/src/hooks/useSession.ts`: call `invoke('save_session')`
- [ ] T134 [US3] Add `loadSession` function to `ui/src/hooks/useSession.ts`: call `invoke('load_session')`, restore distributions
- [ ] T135 [US3] Add `replayDistribution` function to `ui/src/hooks/useSession.ts`: re-run verbalize with saved params

### Deterministic Replay Validation

- [ ] T136 [US3] Test deterministic replay: generate distribution with seed=100, save, reload, replay → verify identical p-values (6 decimal precision)
- [ ] T137 [US3] Test cross-platform replay: save session on macOS, load on Windows → verify identical distributions
- [ ] T138 [US3] Test version migration: create v1 session, load in v1.1 app → verify successful migration or graceful failure

**Checkpoint**: User Story 3 complete - session save/load, deterministic replay, version compatibility. Reproducibility validated.

---

## Phase 7: User Story 4 - Export & Analysis (Priority: P3)

**Goal**: Enable exporting distributions to CSV/JSONL with comprehensive trace metadata for external analysis (Excel, Python, R).

**Independent Test**: Generate distribution, click "Export to CSV/JSONL", verify file contains all fields (completion, probability, model, latency, token_count, etc.).

### Tests for User Story 4

- [ ] T139 [P] [US4] Contract test for export endpoint in `tests/contract/test_export_contract.py`
- [ ] T140 [P] [US4] Contract test for export endpoint in `tests/contract/test_export_contract.rs`
- [ ] T141 [P] [US4] Integration test for export formats in `tests/integration/test_export_formats.py`

### Python Sidecar Implementation for User Story 4

- [ ] T142 [US4] Create export handler in `vs_bridge/handlers/export_handler.py`: serialize distributions to CSV/JSONL
- [ ] T143 [US4] Add CSV export logic in `vs_bridge/handlers/export_handler.py`: include all trace metadata fields
- [ ] T144 [US4] Add JSONL export logic in `vs_bridge/handlers/export_handler.py`: one JSON object per line, valid schema
- [ ] T145 [US4] Add endpoint `POST /api/v1/export` in `vs_bridge/main.py` calling export handler
- [ ] T146 [US4] Ensure 6 decimal precision for probability values in `vs_bridge/handlers/export_handler.py`

### Rust Commands for User Story 4

- [ ] T147 [US4] Implement `export` command in `src-tauri/src/commands/export.rs`: accept distribution_ids[], format, path, call sidecar
- [ ] T148 [US4] Register `export` command in `src-tauri/src/lib.rs` invoke handler
- [ ] T149 [US4] Add error handling in `src-tauri/src/commands/export.rs`: disk full → actionable message, invalid path → clear error

### React Components for User Story 4

- [ ] T150 [P] [US4] Create `ui/src/components/ExportDialog.tsx`: format selection (CSV/JSONL), field selection, file path picker
- [ ] T151 [US4] Add "Export" button to `ui/src/components/DistributionPanel.tsx` opening export dialog
- [ ] T152 [US4] Add "Export All" button to `ui/src/components/SessionManager.tsx` for multi-distribution export

### Export Validation

- [ ] T153 [US4] Test CSV export: generate distribution, export to CSV, open in Excel → verify loads without errors
- [ ] T154 [US4] Test JSONL export: generate distribution, export to JSONL, parse with Python pandas → verify schema compliance
- [ ] T155 [US4] Test precision: export distribution with p=0.123456789, verify CSV shows 0.123457 (6 decimals)
- [ ] T156 [US4] Test metadata: verify exported file contains model, api_latency_ms, token_count, k, τ, temperature, seed, timestamp

**Checkpoint**: User Story 4 complete - CSV/JSONL export with comprehensive metadata, validated with Excel/Python/R.

---

## Phase 8: User Story 6 - Advanced Analysis (Optional) (Priority: P4)

**Goal**: Enable comparative experiments (side-by-side distributions) and entropy metrics for power users.

**Independent Test**: Create 2+ distributions with same prompt but different parameters, click "Compare", see side-by-side visualization.

### Tests for User Story 6

- [ ] T157 [P] [US6] Integration test for comparative analysis in `tests/integration/test_comparative_analysis.py`
- [ ] T158 [P] [US6] Unit test for entropy calculation in `tests/unit/python/test_entropy.py`

### Python Sidecar Implementation for User Story 6

- [ ] T159 [US6] Create entropy calculation function in `vs_bridge/handlers/analysis_handler.py`: Shannon entropy H = -Σ(p*log₂(p))
- [ ] T160 [US6] Add endpoint `POST /api/v1/analyze/entropy` in `vs_bridge/main.py` calling entropy calculation
- [ ] T161 [US6] Add comparative delta calculation in `vs_bridge/handlers/analysis_handler.py`: probability differences between distributions

### React Components for User Story 6

- [ ] T162 [P] [US6] Create `ui/src/components/ComparativeView.tsx`: side-by-side bar charts with difference highlighting
- [ ] T163 [US6] Add "Compare" button to `ui/src/components/SessionManager.tsx`: select 2+ distributions, open comparative view
- [ ] T164 [US6] Add "Show Entropy" button to `ui/src/components/DistributionPanel.tsx`: display H value with interpretation
- [ ] T165 [US6] Add entropy sorting to `ui/src/components/SessionManager.tsx`: rank distributions by certainty (low H → high H)

### Comparative Validation

- [ ] T166 [US6] Test comparative view: create 2 distributions with different temperatures, compare → verify delta tooltips show ΔP
- [ ] T167 [US6] Test entropy: generate uniform distribution (all p ≈ 0.2) → verify high H; generate peaked distribution (one p ≈ 0.9) → verify low H

**Checkpoint**: User Story 6 complete (optional) - comparative analysis, entropy metrics for power users.

---

## Phase 9: QA & Validation (Milestone 7)

**Purpose**: Execute comprehensive testing against spec acceptance criteria, fix bugs, validate constitution compliance

### Contract Testing

- [ ] T168 [P] Run all contract tests in `tests/contract/`: validate Tauri ↔ Python messages match JSON schemas
- [ ] T169 [P] Test schema versioning: v1 client with v2 sidecar → verify graceful failure with version mismatch error

### Integration Testing

- [ ] T170 [P] Run `tests/integration/test_sidecar_lifecycle.rs`: verify start/stop/restart, crash recovery
- [ ] T171 [P] Run `tests/integration/test_offline_mode.py`: verify full workflow without internet (verbalize, sample, export, session)
- [ ] T172 [P] Run `tests/integration/test_export_formats.py`: verify CSV/JSONL parse correctly in Excel, pandas, R

### E2E Testing

- [ ] T173 [P] Run `tests/e2e/test_core_workflow.spec.ts`: Playwright test of full flow (prompt → verbalize → sample → export)
- [ ] T174 [P] Run `tests/e2e/test_session_replay.spec.ts`: save session → restart app → load → replay → verify exact match

### Manual QA Against Spec

- [ ] T175 Validate User Story 1 acceptance scenarios 1-7 (spec.md lines 20-26): basic distribution exploration
- [ ] T176 Validate User Story 2 acceptance scenarios 1-4 (spec.md lines 40-43): weighted sampling
- [ ] T177 Validate User Story 3 acceptance scenarios 1-4 (spec.md lines 57-60): session persistence
- [ ] T178 Validate User Story 4 acceptance scenarios 1-4 (spec.md lines 74-77): export & analysis
- [ ] T179 Validate User Story 5 acceptance scenarios 1-5 (spec.md lines 91-95): provider config & security
- [ ] T180 Validate edge cases (spec.md lines 118-125): rate limit, endpoint crash, k limits, version mismatch, normalization, malformed input, disk full, unsaved changes

### Constitution Compliance Audit

- [ ] T181 [P] Verify Principle I (Offline-First): test local vLLM workflow without internet, verify feature parity
- [ ] T182 [P] Verify Principle II (Security): verify keys encrypted, never in logs/UI/errors, Stronghold vault secure
- [ ] T183 [P] Verify Principle III (JSON Contracts): verify all IPC uses versioned schemas, breaking changes bump version
- [ ] T184 [P] Verify Principle IV (Test-First): verify contract/integration/E2E tests exist and pass
- [ ] T185 [P] Verify Principle V (Observability): verify exports include trace metadata, errors are actionable
- [ ] T186 [P] Verify Principle VI (Desktop-First): verify Rust orchestrates, Python owns inference, sidecar pattern works
- [ ] T187 [P] Verify Principle VII (Module Independence): verify UI/Rust/Python modules testable in isolation

### Performance Validation

- [ ] T188 Benchmark app startup time: verify <3s including sidecar initialization
- [ ] T189 Benchmark verbalize latency: verify <10s for API (k=10), <5s for local vLLM (k=10)
- [ ] T190 Benchmark export speed: verify <2s for 100-distribution sessions
- [ ] T191 Benchmark token details expansion: verify <1s for k≤100
- [ ] T192 Benchmark UI responsiveness: verify all interactions <100ms (button clicks, table sorts, slider adjustments)

### Cross-Platform Testing

- [ ] T193 [P] Test Windows 10: install, run, validate core workflow (verbalize, sample, export, session)
- [ ] T194 [P] Test macOS 12 (x64 + ARM64): install, run, validate core workflow
- [ ] T195 [P] Test Ubuntu 20.04: install via AppImage, run, validate core workflow

### Bug Fixes & Polish

- [ ] T196 Fix all failing contract tests: update schemas or implementations to match
- [ ] T197 Fix all failing integration tests: address sidecar lifecycle issues, offline mode bugs
- [ ] T198 Fix all failing E2E tests: resolve UI interaction issues, timing problems
- [ ] T199 Improve error messages: ensure 95% are actionable (not generic "Error occurred")
- [ ] T200 Add loading spinners to all async operations: verbalize, sample, export, session load
- [ ] T201 Add progress indicators for long operations: k=500 verbalize, large session export
- [ ] T202 Refine UI layout: ensure responsive design for 1280x720 minimum resolution

**Checkpoint**: All tests pass, all user stories validated, constitution compliance 100%, cross-platform builds working.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final improvements, documentation, deployment readiness

- [ ] T203 [P] Create user documentation in `README.md`: quickstart, feature overview, screenshots
- [ ] T204 [P] Create developer documentation in `CONTRIBUTING.md`: setup, build, test, architecture overview
- [ ] T205 [P] Update `schemas/README.md` with versioning guide and compatibility matrix
- [ ] T206 [P] Create troubleshooting guide in `docs/TROUBLESHOOTING.md`: common errors, solutions
- [ ] T207 Run `scripts/validate-contracts.sh` in CI: ensure all JSON schemas are valid and match implementations
- [ ] T208 Optimize PyInstaller bundle: exclude unnecessary deps, use UPX compression if size >100MB
- [ ] T209 [P] Add accessibility improvements: ARIA labels, keyboard navigation (Tab, Enter, Esc), screen reader support
- [ ] T210 [P] Add internationalization (i18n) placeholders: prepare for multi-language support in future
- [ ] T211 Performance optimization: profile k=500 rendering, optimize if >100ms
- [ ] T212 Security hardening: review all input validation, sanitization, error handling
- [ ] T213 Create GitHub Actions workflow: CI for contract tests, integration tests, cross-platform builds
- [ ] T214 Create release workflow: signed binaries (Win/Mac code signing), AppImage/Flatpak for Linux
- [ ] T215 Run final validation of `specs/001-sampling-desktop-app/checklists/quality.md`: all items must pass
- [ ] T216 Tag release v1.0.0: create Git tag, GitHub release with changelog, binaries attached

**Checkpoint**: Production-ready desktop app, documented, tested, deployed.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (Phase 1) completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational (Phase 2) completion
  - User stories can proceed in parallel (if staffed)
  - Or sequentially in priority order: US1 (P1) → US5 (P2) → US2 (P2) → US3 (P2) → US4 (P3) → US6 (P4)
- **QA & Validation (Phase 9)**: Depends on desired user stories being complete
- **Polish (Phase 10)**: Depends on QA validation passing

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Works best with US1 for full experience but independently testable
- **User Story 5 (P2)**: Can start after Foundational (Phase 2) - Independent, enables API access for US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Works best with US1 to save/load distributions
- **User Story 4 (P3)**: Can start after Foundational (Phase 2) - Works best with US1 to export distributions
- **User Story 6 (P4)**: Can start after Foundational (Phase 2) - Works best with US1 for comparative analysis

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Python handlers before Rust commands (sidecar endpoints must exist before Rust calls them)
- Rust commands before React hooks (invoke targets must exist before hooks call them)
- React hooks before React components (hooks provide state/actions for components)
- Core implementation before integration with other stories

### Parallel Opportunities

#### Phase 1 (Setup)
- Tasks T003, T004, T007, T008, T009, T011, T012 can run in parallel (different files)

#### Phase 2 (Foundational)
- JSON schemas T027-T035 can run in parallel (independent files)
- Contract test templates T044, T045 can run in parallel
- Type definitions: Python (T039-T041), Rust (T036-T038), TypeScript (T042-T043) can run in parallel after schemas exist

#### Phase 3 (User Story 1)
- Tests T047-T050 can run in parallel (different test files)
- React components T060, T061 can run in parallel initially (different files)

#### Phase 4 (User Story 2)
- Tests T077-T079 can run in parallel

#### Phase 5 (User Story 5)
- Tests T093-T095 can run in parallel
- Settings UI T105 can start while backend security work is in progress (T096-T104)

#### Phase 6 (User Story 3)
- Tests T117-T119 can run in parallel
- Session manager component T129 can run in parallel with hook T132

#### Phase 7 (User Story 4)
- Tests T139-T141 can run in parallel
- Export dialog T150 can run in parallel with export command T147

#### Phase 8 (User Story 6)
- Tests T157-T158 can run in parallel
- Comparative view T162 can run in parallel with entropy calculation T159

#### Phase 9 (QA)
- All contract tests (T168-T169) can run in parallel
- All integration tests (T170-T172) can run in parallel
- All E2E tests (T173-T174) can run in parallel
- All constitution audits (T181-T187) can run in parallel
- All platform tests (T193-T195) can run in parallel

#### Phase 10 (Polish)
- All documentation tasks (T203-T206) can run in parallel
- Accessibility (T209) and i18n (T210) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Step 1: Launch all tests together (they should FAIL):
Task T047: "Contract test for verbalize endpoint in tests/contract/test_verbalize_contract.py"
Task T048: "Contract test for verbalize endpoint in tests/contract/test_verbalize_contract.rs"
Task T049: "Integration test for offline verbalize in tests/integration/test_offline_mode.py"
Task T050: "E2E test for core workflow in tests/e2e/test_core_workflow.spec.ts"

# Step 2: Implement Python sidecar (sequential - T051 → T052):
Task T051: "Create verbalize handler in vs_bridge/handlers/verbalize_handler.py"
Task T052: "Add endpoint POST /api/v1/verbalize in vs_bridge/main.py"
Task T053: "Implement token-level probability extraction"
Task T054: "Add probability normalization logic"
Task T055: "Add trace metadata collection"

# Step 3: Implement Rust commands (sequential):
Task T056: "Implement verbalize command in src-tauri/src/commands/verbalize.rs"
Task T057: "Add k validation"
Task T058: "Register verbalize command in lib.rs"
Task T059: "Add error mapping"

# Step 4: Launch React components together (different files):
Task T060: "Create ui/src/components/PromptPanel.tsx"
Task T061: "Create ui/src/components/DistributionPanel.tsx"

# Step 5: Then sequential UI refinement:
Task T062: "Create ui/src/components/DistributionTable.tsx"
Task T063: "Add expandable rows for token details"
Task T064: "Add sort functionality"
Task T065: "Create ui/src/components/ProbabilityChart.tsx"
Task T066: "Add custom tooltips"
Task T067: "Performance test k=500 bars"

# Step 6: Wire everything together (sequential):
Task T068: "Implement ui/src/hooks/useVerbalize.ts"
Task T069: "Add auto-refresh logic"
Task T070: "Add Pin Current View toggle"
Task T071: "Wire Verbalize button to hook"
Task T072: "Add Show Token Details toggle"
Task T073: "Add Pin Current View toggle to UI"
Task T074: "Add loading spinner"
Task T075: "Add error display"
Task T076: "Test offline mode"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (Tasks T001-T012)
2. Complete Phase 2: Foundational (Tasks T013-T046) - CRITICAL
3. Complete Phase 3: User Story 1 (Tasks T047-T076)
4. **STOP and VALIDATE**: Run all US1 tests, verify independently functional
5. Optional: Deploy/demo MVP before continuing

**MVP Delivers**: Prompt input → verbalize → visualize distribution (table + chart + token details + pin view)

### Incremental Delivery

1. Setup + Foundational → Foundation ready (Tasks T001-T046)
2. Add US1 (P1) → Test independently → Deploy/Demo (MVP!) (Tasks T047-T076)
3. Add US5 (P2) → Test independently → Deploy/Demo (Secure API access) (Tasks T093-T116)
4. Add US2 (P2) → Test independently → Deploy/Demo (Weighted sampling) (Tasks T077-T092)
5. Add US3 (P2) → Test independently → Deploy/Demo (Session persistence) (Tasks T117-T138)
6. Add US4 (P3) → Test independently → Deploy/Demo (Export analysis) (Tasks T139-T156)
7. Add US6 (P4) → Test independently → Deploy/Demo (Advanced analysis) (Tasks T157-T167)
8. QA Validation → Production ready (Tasks T168-T202)
9. Polish → Release v1.0.0 (Tasks T203-T216)

**Each story adds value without breaking previous stories**

### Parallel Team Strategy

With 3 developers after Foundational phase completes:

1. **Team completes Setup + Foundational together** (Tasks T001-T046)
2. **Once Foundational done, split work**:
   - **Developer A**: User Story 1 (P1) - Tasks T047-T076 (MVP core)
   - **Developer B**: User Story 5 (P2) - Tasks T093-T116 (Security/settings)
   - **Developer C**: User Story 2 (P2) - Tasks T077-T092 (Sampling)
3. **After parallel stories complete**:
   - **Developer A**: User Story 3 (P2) - Tasks T117-T138
   - **Developer B**: User Story 4 (P3) - Tasks T139-T156
   - **Developer C**: User Story 6 (P4) - Tasks T157-T167
4. **All together**: QA & Polish - Tasks T168-T216

**Stories integrate independently, minimal merge conflicts**

---

## Task Statistics

- **Total Tasks**: 216
- **Phase 1 (Setup)**: 12 tasks (5 parallelizable)
- **Phase 2 (Foundational)**: 34 tasks (16 parallelizable) - BLOCKS all user stories
- **Phase 3 (US1 - P1)**: 30 tasks (4 test tasks, 4 parallelizable) 🎯 MVP
- **Phase 4 (US2 - P2)**: 16 tasks (3 test tasks, 2 parallelizable)
- **Phase 5 (US5 - P2)**: 24 tasks (3 test tasks, 4 parallelizable)
- **Phase 6 (US3 - P2)**: 22 tasks (3 test tasks, 3 parallelizable)
- **Phase 7 (US4 - P3)**: 18 tasks (3 test tasks, 2 parallelizable)
- **Phase 8 (US6 - P4)**: 11 tasks (2 test tasks, 3 parallelizable) - Optional
- **Phase 9 (QA)**: 35 tasks (19 parallelizable)
- **Phase 10 (Polish)**: 14 tasks (6 parallelizable)

**Parallelizable Tasks**: 72 (33% can run in parallel within phases)

**Test Tasks**: 24 contract/integration/E2E tests (11% of tasks, constitutional requirement)

**MVP Scope**: Setup (12) + Foundational (34) + US1 (30) = **76 tasks for minimal viable product**

**Full Release**: All 216 tasks for complete v1.0.0 with all user stories

---

## Notes

- [P] tasks = different files, no dependencies, can run in parallel
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- Tests MUST fail before implementing features (Red-Green-Refactor)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Constitution compliance validated in Phase 9 (tasks T181-T187)
- Performance benchmarks validated in Phase 9 (tasks T188-T192)
- Cross-platform testing in Phase 9 (tasks T193-T195)
- All 7 constitution principles enforced throughout implementation
- Schema versioning enforced via `schemas/v1/` directory structure
- Stronghold mandatory for secrets (Principle II) - validated in T113-T116
- Python black box preserved (Principle III) - no ML logic in Rust
- Module independence (Principle VII) - validated in T187
