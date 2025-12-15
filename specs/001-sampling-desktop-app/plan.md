# Implementation Plan: Verbalized Sampling Desktop App

**Branch**: `001-sampling-desktop-app` | **Date**: 2025-10-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-sampling-desktop-app/spec.md`

## Summary

Build a cross-platform desktop application (Tauri 2 + React) that visualizes and manipulates LLM sampling distributions from the Python `verbalized_sampling` package. The app enables researchers to explore probability distributions of model completions, run weighted sampling, export data for analysis, and manage sessions with full reproducibility. Core architecture follows sidecar pattern: Rust orchestrates UI and process management, Python handles all inference logic, communication via versioned JSON contracts.

**Key Capabilities**: Offline-first operation (local vLLM + API providers), Stronghold-encrypted secrets, token-level probability drill-down, comprehensive export metadata, auto-refresh with pin-to-analyze toggle, deterministic replay.

## Technical Context

**Language/Version**:
- Rust 1.75+ (Tauri backend)
- Python 3.9+ (inference engine)
- TypeScript/React 18+ (UI)

**Primary Dependencies**:
- Tauri 2.0 (desktop framework)
- React 18 + Vite (frontend)
- Recharts (probability visualizations)
- Tauri Stronghold plugin (secret storage)
- Python `verbalized_sampling` package (inference black box)
- PyInstaller (sidecar binary packaging)

**Storage**:
- SQLite (application state, user preferences)
- Filesystem (session JSON files, JSONL/CSV exports)
- Stronghold vault (encrypted API keys)

**Testing**:
- Rust: `cargo test` (Tauri commands, sidecar lifecycle)
- Python: `pytest` (contract validation, inference logic)
- React: Vitest + React Testing Library (UI components)
- Contract tests: JSON schema validation (Tauri ↔ Python boundary)
- E2E: Playwright or Tauri's test harness (critical workflows)

**Target Platform**:
- Windows 10+ (x64)
- macOS 12+ (x64, ARM64)
- Linux (Ubuntu 20.04+, Fedora 36+, AppImage for broad compatibility)

**Project Type**: Desktop application (Tauri hybrid: Rust backend + web frontend)

**Performance Goals**:
- App startup: <3s (including Python sidecar initialization)
- Distribution generation: <10s (API), <5s (local vLLM) for k=10
- UI responsiveness: <100ms for all interactions
- Export operations: <2s for 100-distribution sessions
- Token details expansion: <1s for k≤100

**Constraints**:
- Offline-capable: Full feature parity without internet
- Zero cloud dependencies for core operation
- Python sidecar must remain black box (no Rust rewrite)
- All UI ↔ core communication via JSON contracts
- Stronghold mandatory for secrets (no alternatives)
- Single-binary distribution where feasible

**Scale/Scope**:
- Support 1000 distributions per session without degradation
- Handle k=100 (API) to k=500 (local vLLM) samples
- Multi-provider support (OpenAI, Anthropic, Cohere, local vLLM)
- Export files compatible with Excel, Python pandas, R (no preprocessing)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### ✅ Principle I: Deployment Flexibility (Offline-First)
- **Compliance**: App supports local vLLM (offline) and API providers (online) with feature parity
- **Validation**: Model backend selection is runtime-configurable (Settings panel); no cloud dependencies for core operation
- **Test**: Verify full workflow (verbalize, sample, export, session save/load) works offline with local vLLM

### ✅ Principle II: Security & Secrets Management
- **Compliance**: Tauri Stronghold plugin used for all API key storage; keys never appear in logs/UI/errors
- **Validation**: Default config files use placeholders; `.gitignore` excludes vault files; keys masked as "●●●●●●●●" in UI
- **Test**: Verify key encryption at rest, redaction in logs ([REDACTED]), persistence across app restarts

### ✅ Principle III: Pluggable Inference Architecture
- **Compliance**: Python `verbalized_sampling` remains black-box sidecar; all communication via JSON contracts in `/schemas/`
- **Validation**: Rust commands invoke Python via IPC/HTTP; no ML logic in Rust; versioned schemas (contract.v1.json, etc.)
- **Test**: Contract tests validate JSON schema compliance on both sides; breaking changes bump schema version

### ✅ Principle IV: Test-First Development
- **Compliance**: Tests written before implementation; Red-Green-Refactor cycle enforced
- **Validation**: Unit tests for Rust commands, Python contract handlers, React components; integration tests for Tauri-Python boundary; E2E tests for critical workflows
- **Test**: Contract test suite validates IPC messages match schemas; UI tests verify acceptance scenarios

### ✅ Principle V: Observability & Debugging
- **Compliance**: In-app log viewer with filtering; structured JSON exports; actionable error messages
- **Validation**: Distribution exports include trace metadata (model, latency, token_count); debug mode exposes intermediate states
- **Test**: Verify exports contain all metadata; error messages guide user actions (not generic "Error occurred")

### ✅ Principle VI: Desktop-First Architecture (Tauri 2)
- **Compliance**: Tauri 2 as primary target; Rust orchestrates sidecar, Python owns inference; sidecar pattern for process management
- **Validation**: React UI in Tauri webview; single-binary distribution (PyInstaller sidecar under `src-tauri/binaries/`)
- **Test**: Cross-platform builds (Win/Mac/Linux); sidecar lifecycle (start/stop/restart); UI renders in webview

### ✅ Principle VII: Module Independence & Maintainability
- **Compliance**: Clear boundaries: UI module (React), Rust module (Tauri commands), Python module (sidecar); JSON contracts prevent coupling
- **Validation**: Module-level READMEs document purpose, inputs/outputs, testing; each module has isolated test suite
- **Test**: Verify modules testable independently; contract changes don't break unrelated modules

### Constitution Compliance Summary
**Status**: ✅ **FULLY COMPLIANT**

No violations detected. Architecture aligns with all 7 core principles:
- Offline-first with API flexibility ✓
- Stronghold-encrypted secrets ✓
- JSON-contracted sidecar pattern ✓
- Test-first with contract validation ✓
- Observable with structured exports ✓
- Tauri desktop-first with sidecar ✓
- Modular with one-person maintainability ✓

## Project Structure

### Documentation (this feature)

```
specs/001-sampling-desktop-app/
├── plan.md                    # This file (/speckit.plan command output)
├── spec.md                    # Feature specification (completed)
├── clarifications.md          # Clarification session log (completed)
├── research.md                # Phase 0 output (/speckit.plan command - TO BE CREATED)
├── data-model.md              # Phase 1 output (/speckit.plan command - TO BE CREATED)
├── quickstart.md              # Phase 1 output (/speckit.plan command - TO BE CREATED)
├── contracts/                 # Phase 1 output (/speckit.plan command - TO BE CREATED)
│   ├── verbalize.v1.json      # Verbalize command contract
│   ├── sample.v1.json         # Sample command contract
│   ├── export.v1.json         # Export command contract
│   └── session.v1.json        # Session persistence contract
├── checklists/
│   └── requirements.md        # Spec quality validation (completed)
└── tasks.md                   # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```
verbalized-sampling-main/
├── verbalized_sampling/           # Python core (EXISTING - DO NOT MODIFY)
│   ├── __init__.py
│   ├── meta_prompt.py
│   ├── prompt_learning_optimizer.py
│   └── backends/                  # Model provider backends
│
├── vs_bridge/                     # NEW: Python sidecar service
│   ├── __init__.py
│   ├── main.py                    # FastAPI server or stdio handler
│   ├── handlers/
│   │   ├── verbalize_handler.py   # Handles verbalize requests
│   │   ├── sample_handler.py      # Handles weighted sampling
│   │   └── export_handler.py      # Handles data export
│   ├── models.py                  # Pydantic models for JSON contracts
│   └── requirements.txt           # Bridge-specific deps
│
├── src-tauri/                     # Tauri Rust backend
│   ├── src/
│   │   ├── lib.rs                 # Main Tauri entry point
│   │   ├── commands/              # Tauri command modules
│   │   │   ├── mod.rs
│   │   │   ├── verbalize.rs       # Verbalize command
│   │   │   ├── sample.rs          # Sample command
│   │   │   ├── export.rs          # Export command
│   │   │   ├── session.rs         # Session save/load
│   │   │   └── settings.rs        # Settings + Stronghold
│   │   ├── sidecar/               # Sidecar lifecycle management
│   │   │   ├── mod.rs
│   │   │   ├── manager.rs         # Start/stop/health checks
│   │   │   └── ipc.rs             # IPC/HTTP client
│   │   └── models.rs              # Rust types for JSON contracts
│   ├── binaries/                  # Sidecar binaries (built via PyInstaller)
│   │   ├── vs-bridge-x86_64-pc-windows-msvc.exe
│   │   ├── vs-bridge-x86_64-apple-darwin
│   │   ├── vs-bridge-aarch64-apple-darwin
│   │   └── vs-bridge-x86_64-unknown-linux-gnu
│   ├── capabilities/
│   │   └── default.json           # Tauri permissions (filesystem, shell, etc.)
│   ├── tauri.conf.json            # Tauri configuration
│   └── Cargo.toml
│
├── ui/                            # React frontend
│   ├── src/
│   │   ├── main.tsx               # React entry point
│   │   ├── App.tsx                # Main app component
│   │   ├── components/
│   │   │   ├── PromptPanel.tsx    # Prompt input + parameter controls
│   │   │   ├── DistributionPanel.tsx  # Table + chart view
│   │   │   ├── DistributionTable.tsx  # Sortable table with token details
│   │   │   ├── ProbabilityChart.tsx   # Recharts bar chart
│   │   │   ├── SettingsPanel.tsx      # Provider config + Stronghold
│   │   │   ├── SessionManager.tsx     # Save/load/replay sessions
│   │   │   └── ExportDialog.tsx       # Export format selection
│   │   ├── hooks/
│   │   │   ├── useVerbalize.ts    # Verbalize command hook
│   │   │   ├── useSample.ts       # Sample command hook
│   │   │   ├── useSession.ts      # Session persistence hook
│   │   │   └── useSettings.ts     # Settings + Stronghold hook
│   │   ├── types/
│   │   │   ├── contracts.ts       # TypeScript types from JSON schemas
│   │   │   └── models.ts          # UI state models
│   │   └── utils/
│   │       ├── tauri.ts           # Tauri invoke wrappers
│   │       └── validation.ts      # Client-side schema validation
│   ├── index.html
│   ├── vite.config.ts
│   ├── package.json
│   └── tsconfig.json
│
├── schemas/                       # JSON contract definitions
│   ├── v1/
│   │   ├── verbalize-request.json     # Verbalize input schema
│   │   ├── verbalize-response.json    # Verbalize output schema
│   │   ├── sample-request.json        # Sample input schema
│   │   ├── sample-response.json       # Sample output schema
│   │   ├── export-request.json        # Export input schema
│   │   ├── export-response.json       # Export output schema
│   │   ├── session-save-request.json  # Session save schema
│   │   └── session-load-response.json # Session load schema
│   └── README.md                      # Schema versioning guide
│
├── tests/                         # Test suites
│   ├── contract/                  # JSON schema contract tests
│   │   ├── test_verbalize_contract.py    # Python side
│   │   ├── test_verbalize_contract.rs    # Rust side
│   │   └── ...
│   ├── integration/               # Cross-module integration tests
│   │   ├── test_sidecar_lifecycle.rs
│   │   ├── test_offline_mode.py
│   │   └── test_export_formats.py
│   ├── e2e/                       # End-to-end UI tests
│   │   ├── test_core_workflow.spec.ts    # Playwright
│   │   └── test_session_replay.spec.ts
│   └── unit/                      # Module-specific unit tests
│       ├── rust/                  # Cargo tests
│       ├── python/                # Pytest tests
│       └── react/                 # Vitest tests
│
├── scripts/                       # Build and utility scripts
│   ├── build-sidecar.sh           # PyInstaller build for all platforms
│   ├── generate-types.sh          # JSON schema → TypeScript types
│   └── validate-contracts.sh     # Schema validation CI check
│
├── .gitignore                     # Excludes: *.stronghold, dist/, target/, node_modules/
├── README.md                      # Project overview + quickstart
└── LICENSE                        # Apache 2.0
```

**Structure Decision**: Desktop application architecture with clear separation:
- **Python module** (`verbalized_sampling/`): Existing inference engine, unchanged
- **Python sidecar** (`vs_bridge/`): FastAPI/stdio service wrapping inference, packaged via PyInstaller
- **Rust backend** (`src-tauri/`): Tauri commands for sidecar orchestration, Stronghold integration, no ML logic
- **React frontend** (`ui/`): Web-based UI in Tauri webview, communicates via Tauri invoke()
- **JSON schemas** (`schemas/`): Versioned contracts enforcing Tauri ↔ Python boundary
- **Tests** (`tests/`): Contract, integration, E2E, and unit tests with isolated module coverage

This structure enforces constitution principles: Python black box (no rewrite), JSON contracts (versioned schemas), sidecar pattern (PyInstaller binaries), module independence (clear boundaries).

## Complexity Tracking

*No constitutional violations detected. This section documents architectural decisions requiring justification.*

| Decision | Why Needed | Simpler Alternative Rejected Because |
|----------|------------|-------------------------------------|
| **PyInstaller sidecar binary** | Single-binary distribution requires bundling Python runtime. Users expect "download and run" without installing Python 3.9+. | **Alternative**: Require user-installed Python. **Rejected**: Violates desktop-first UX; users expect self-contained apps. PyInstaller adds ~50MB but delivers professional packaging. |
| **FastAPI for sidecar** | Long-running operations (k=500 local vLLM) need streaming. FastAPI's async + Server-Sent Events enable progress updates without blocking IPC. | **Alternative**: Tauri IPC only. **Rejected**: IPC is synchronous; k=500 can take 30s+ and UI freezes. FastAPI localhost HTTP adds complexity but enables streaming + cancellation. |
| **Recharts for visualization** | Probability distributions need interactive bar charts with hover tooltips. Recharts is React-native, well-maintained, and handles k=500 bars efficiently. | **Alternative**: Canvas-based D3.js. **Rejected**: D3 has steeper learning curve, manual React integration, overkill for bar charts. Recharts is declarative and sufficient. |
| **SQLite for app state** | User preferences (theme, default provider, last k value) need persistence. SQLite is embedded, cross-platform, and Tauri-compatible. | **Alternative**: JSON files. **Rejected**: JSON requires manual file locking, corruption risk on crashes. SQLite handles concurrency and is standard for desktop apps. |
| **Pydantic for contract validation** | JSON schema validation on Python side prevents malformed IPC messages. Pydantic auto-generates validators from schemas, reducing manual parsing code. | **Alternative**: Manual dict parsing. **Rejected**: Error-prone, verbose, doesn't enforce schema versioning. Pydantic is standard for FastAPI and matches Rust's serde. |

**Maintenance Burden Assessment**:
- PyInstaller: CI builds for 3 platforms (Win/Mac/Linux); manageable via GitHub Actions matrix
- FastAPI sidecar: Adds HTTP server complexity but isolates from Tauri; health checks handle crashes
- Recharts: Standard React dependency, actively maintained, minimal upgrade burden
- SQLite: Embedded, no external service, Tauri plugin handles migrations
- Pydantic: Aligns with Python ecosystem, reduces contract validation code

**One-Person Maintainability**: Each decision preserves module independence:
- Sidecar binary: Python developer owns without Rust knowledge
- FastAPI: Isolated from Tauri, standard Python async patterns
- Recharts: UI developer owns without backend knowledge
- SQLite: Tauri plugin abstracts, no SQL expertise required for basic CRUD
- Pydantic: Standard Python library, auto-validation reduces manual code

**Simpler Alternatives Reconsidered**:
- Could eliminate FastAPI by using Tauri IPC only, but k=500 streaming requirement justifies HTTP
- Could skip PyInstaller and require Python install, but violates desktop-first principle
- Could use JSON files instead of SQLite, but concurrency + corruption risk outweighs simplicity gain

**Conclusion**: Complexity is justified by constitution requirements (offline-first, desktop-first, sidecar pattern) and user expectations (single-binary, streaming for large k). Each addition solves a specific constraint and maintains module boundaries.

## Phase 0: Research & Discovery

**Objective**: Validate technical feasibility of Tauri 2 + Python sidecar architecture; prototype JSON contract flow; confirm PyInstaller bundling; test Stronghold plugin.

**Deliverables**:
- `research.md`: Technical spike findings, proof-of-concept code snippets, dependency compatibility matrix
- Working prototype: Minimal Tauri app invoking "hello world" Python sidecar via JSON contract
- PyInstaller test: Bundle Python script with `verbalized_sampling` dependencies into executable
- Stronghold test: Store/retrieve test API key, verify encryption at rest

**Key Questions to Answer**:
1. Can Tauri 2 shell plugin execute PyInstaller sidecar on all platforms (Win/Mac/Linux)?
2. Does Stronghold plugin work with Tauri 2 stable? (Check version compatibility)
3. Can Pydantic models serialize/deserialize complex types (e.g., token-level probabilities as `List[Dict[str, float]]`)?
4. What's the sidecar startup latency? (Target: <1s for app launch <3s total)
5. Can FastAPI async server run inside PyInstaller bundle without conflicts?
6. Are Recharts and React 18 compatible with Tauri webview (no CSP issues)?

**Research Tasks** (to be detailed in `research.md`):
- [ ] Tauri 2 sidecar proof-of-concept: Create minimal `tauri.conf.json` with shell plugin, execute Python script, verify stdout/stderr capture
- [ ] JSON contract validation: Define sample schema (e.g., `{"prompt": str, "k": int}`), validate with Pydantic (Python) and serde_json (Rust)
- [ ] PyInstaller bundling test: Package `verbalized_sampling` + FastAPI into single exe/binary, verify imports work, measure startup time
- [ ] Stronghold integration: Use Tauri Stronghold plugin to store test key, restart app, retrieve key, verify it persists encrypted
- [ ] FastAPI async test: Run FastAPI server in separate thread/process, call from Rust via HTTP, measure latency (<50ms localhost)
- [ ] Recharts webview test: Create simple React + Recharts bar chart, load in Tauri webview, verify no CSP/CORS errors, test k=500 bars

**Success Criteria**:
- ✅ Prototype demonstrates end-to-end flow: Tauri command → Rust → Python sidecar → JSON response → React UI update
- ✅ PyInstaller bundle <100MB, startup <1s, includes all `verbalized_sampling` deps
- ✅ Stronghold stores key encrypted, survives app restart, never appears in logs
- ✅ FastAPI localhost latency <50ms, async endpoints don't block sidecar
- ✅ Recharts renders k=500 bars without performance degradation (<100ms render time)

**Timeline**: 2-3 days (1 developer)

## Phase 1: Design & Contracts

**Objective**: Define data model, JSON schemas, module interfaces; create quickstart guide; validate architecture against constitution.

**Deliverables**:
- `data-model.md`: Entity definitions, relationships, state management strategy
- `contracts/`: JSON schema files for all Tauri ↔ Python commands (verbalize, sample, export, session, settings)
- `quickstart.md`: Developer onboarding guide (setup, build, test, run)
- Architecture decision records (ADRs) for: sidecar communication (IPC vs HTTP), state management (React Context vs Zustand), session format (JSONL vs JSON)

**Data Model** (to be detailed in `data-model.md`):

Entities:
- **Prompt**: `{ id: UUID, text: string, created_at: datetime, label?: string }`
- **ParameterSet**: `{ k: int, tau: float, temperature: float, seed: int | null, model: string, provider: string }`
- **Completion**: `{ text: string, probability: float, rank: int, token_probabilities?: Array<{token: string, p: float}> }`
- **Distribution**: `{ id: UUID, prompt: Prompt, parameters: ParameterSet, completions: Completion[], timestamp: datetime, trace_metadata: TraceMetadata }`
- **TraceMetadata**: `{ model: string, api_latency_ms: float, token_count: int, api_version: string, endpoint: string }`
- **Session**: `{ id: UUID, distributions: Distribution[], app_version: string, created_at: datetime, notes?: string }`
- **ProviderConfig**: `{ name: string, api_key_id: string (Stronghold ref), endpoint?: string, status: 'active' | 'inactive' | 'error', last_tested: datetime }`

State Management:
- **React Context** for global state: current distribution, pin toggle, active provider
- **Tauri Store plugin** (or SQLite) for persistent preferences: theme, default k, last provider
- **Stronghold** for encrypted keys: never in React state, accessed only via Tauri commands

**JSON Contracts** (to be defined in `contracts/`):

1. **Verbalize** (`verbalize.v1.json`):
   ```json
   {
     "request": {
       "prompt": "string",
       "k": "int (1-500)",
       "tau": "float (0.0-1.0)",
       "temperature": "float (0.0-2.0)",
       "seed": "int | null",
       "model": "string",
       "provider": "string",
       "include_token_probabilities": "boolean"
     },
     "response": {
       "distribution_id": "UUID",
       "completions": [
         {
           "text": "string",
           "probability": "float",
           "rank": "int",
           "token_probabilities": "optional array"
         }
       ],
       "trace_metadata": {
         "model": "string",
         "api_latency_ms": "float",
         "token_count": "int",
         "api_version": "string",
         "endpoint": "string"
       },
       "timestamp": "ISO8601 datetime"
     }
   }
   ```

2. **Sample** (`sample.v1.json`):
   ```json
   {
     "request": {
       "distribution_id": "UUID",
       "seed": "int | null"
     },
     "response": {
       "selected_completion": {
         "text": "string",
         "probability": "float",
         "rank": "int"
       },
       "selection_index": "int"
     }
   }
   ```

3. **Export** (`export.v1.json`):
   ```json
   {
     "request": {
       "distribution_ids": "UUID[]",
       "format": "'csv' | 'jsonl'",
       "include_metadata": "boolean",
       "output_path": "string"
     },
     "response": {
       "file_path": "string",
       "row_count": "int",
       "file_size_bytes": "int"
     }
   }
   ```

4. **Session Save/Load** (`session.v1.json`):
   ```json
   {
     "save_request": {
       "distributions": "Distribution[]",
       "notes": "optional string",
       "output_path": "string"
     },
     "save_response": {
       "session_id": "UUID",
       "file_path": "string"
     },
     "load_request": {
       "file_path": "string"
     },
     "load_response": {
       "session": {
         "id": "UUID",
         "distributions": "Distribution[]",
         "app_version": "string",
         "created_at": "datetime",
         "notes": "optional string"
       }
     }
   }
   ```

**Module Interfaces**:
- **Tauri Commands** (Rust → Python via HTTP):
  - `verbalize(prompt, params) -> Result<Distribution, Error>`
  - `sample(distribution_id, seed) -> Result<Completion, Error>`
  - `export(distribution_ids, format) -> Result<FilePath, Error>`
  - `save_session(distributions, path) -> Result<SessionId, Error>`
  - `load_session(path) -> Result<Session, Error>`
  - `save_api_key(provider, key) -> Result<(), Error>` (Stronghold)
  - `test_connection(provider) -> Result<Status, Error>`

- **Python Sidecar** (FastAPI endpoints):
  - `POST /api/v1/verbalize` → Distribution
  - `POST /api/v1/sample` → Completion
  - `POST /api/v1/export` → File path
  - `POST /api/v1/session/save` → Session ID
  - `POST /api/v1/session/load` → Session data
  - `GET /api/v1/health` → OK (sidecar health check)

**Quickstart Guide** (to be written in `quickstart.md`):
1. Prerequisites: Rust 1.75+, Python 3.9+, Node 18+, Tauri CLI
2. Clone repo, install deps: `npm install`, `cargo build`, `pip install -r vs_bridge/requirements.txt`
3. Build sidecar: `./scripts/build-sidecar.sh` (creates PyInstaller binaries)
4. Run dev mode: `npm run tauri dev` (starts React dev server + Tauri app)
5. Run tests: `cargo test`, `pytest tests/`, `npm test`
6. Build release: `npm run tauri build` (bundles sidecar, creates installer)

**Success Criteria**:
- ✅ All JSON schemas defined, validated with example payloads
- ✅ Data model documented with entity relationships and state flow
- ✅ Module interfaces specify exact inputs/outputs, error types
- ✅ Quickstart guide enables new developer to run app in <15 minutes
- ✅ Constitution check confirms: JSON contracts enforce boundaries, no Python logic in Rust, module READMEs complete

**Timeline**: 3-4 days (1 developer)

## Phase 2: Core Implementation (Milestones 1-7)

### Milestone 1: Scaffold Tauri App (Frontend + Shell Plugin)

**Goal**: Set up Tauri 2 project structure with React frontend, configure sidecar shell plugin, establish build pipeline.

**Tasks**:
1. Initialize Tauri 2 project: `npm create tauri-app@latest` (choose React + TypeScript)
2. Configure `tauri.conf.json`:
   - Add `shell` plugin for sidecar execution
   - Set sidecar binary path: `src-tauri/binaries/vs-bridge-{target}`
   - Configure capabilities: filesystem (read/write for sessions), shell (sidecar exec), store (preferences)
3. Set up React app structure:
   - Create components: `PromptPanel`, `DistributionPanel`, `SettingsPanel`
   - Add Recharts dependency: `npm install recharts`
   - Configure Vite for Tauri: `vite.config.ts` with Tauri plugin
4. Add Tauri Store plugin for persistent preferences (theme, default k)
5. Create build scripts: `scripts/build-sidecar.sh` (placeholder for Milestone 2)

**Acceptance Criteria**:
- ✅ `npm run tauri dev` launches empty Tauri window with React placeholder
- ✅ `tauri.conf.json` references sidecar binary path (will be built in Milestone 2)
- ✅ React components render basic UI structure (no functionality yet)
- ✅ Tauri Store plugin persists test preference across app restart

**Timeline**: 1 day

### Milestone 2: Build PyInstaller Sidecar (vs_bridge.py)

**Goal**: Package Python `verbalized_sampling` + FastAPI service into executable sidecar for all platforms.

**Tasks**:
1. Create `vs_bridge/main.py`:
   - FastAPI app with health check endpoint: `GET /api/v1/health`
   - Placeholder endpoints: `POST /api/v1/verbalize`, `POST /api/v1/sample`, `POST /api/v1/export`
   - CORS middleware for localhost Tauri webview
   - Uvicorn server on `localhost:8765` (random unused port)
2. Create `vs_bridge/requirements.txt`:
   - Include: `fastapi`, `uvicorn`, `pydantic`, `verbalized_sampling` (local package)
   - Pin versions for reproducibility
3. Create PyInstaller spec file: `vs_bridge.spec`
   - Bundle `verbalized_sampling` package
   - Include hidden imports (PyTorch, NumPy, etc.)
   - One-file mode for single executable
4. Update `scripts/build-sidecar.sh`:
   - Use PyInstaller to build for current platform
   - Output to `src-tauri/binaries/vs-bridge-{target}`
   - GitHub Actions matrix for Win/Mac/Linux builds
5. Test sidecar execution:
   - Run binary standalone: `./src-tauri/binaries/vs-bridge-{target}`
   - Verify FastAPI server starts, health check responds
   - Measure startup time (<1s target)

**Acceptance Criteria**:
- ✅ `./scripts/build-sidecar.sh` produces executable for current platform
- ✅ Sidecar binary starts FastAPI server on `localhost:8765` in <1s
- ✅ `curl http://localhost:8765/api/v1/health` returns `{"status": "ok"}`
- ✅ Binary size <100MB, includes all `verbalized_sampling` dependencies
- ✅ No errors when importing `verbalized_sampling` inside bundled binary

**Timeline**: 2 days

### Milestone 3: Add Rust Commands (Verbalize, Sample, Export)

**Goal**: Implement Tauri commands that orchestrate sidecar calls, manage lifecycle, and return JSON responses to React.

**Tasks**:
1. Create `src-tauri/src/sidecar/manager.rs`:
   - `start_sidecar()`: Launch binary via Tauri shell plugin, wait for health check
   - `stop_sidecar()`: Graceful shutdown via HTTP `POST /api/v1/shutdown`
   - `health_check()`: Poll `/api/v1/health` until 200 OK or timeout (5s)
   - `restart_sidecar()`: Stop + start, triggered on crash detection
2. Create `src-tauri/src/sidecar/ipc.rs`:
   - `send_request(endpoint, payload)`: HTTP POST to sidecar, deserialize JSON response
   - Error handling: timeout (30s), connection refused → trigger restart
3. Implement Tauri commands in `src-tauri/src/commands/`:
   - `verbalize(prompt: String, params: VerbParams) -> Result<DistributionResponse, String>`:
     - Validate params (k <= 100 for API, k <= 500 for local)
     - Send to sidecar: `POST /api/v1/verbalize` with JSON payload
     - Parse response, return to React
   - `sample(distribution_id: String, seed: Option<i64>) -> Result<CompletionResponse, String>`:
     - Send to sidecar: `POST /api/v1/sample`
   - `export(dist_ids: Vec<String>, format: String, path: String) -> Result<ExportResponse, String>`:
     - Send to sidecar: `POST /api/v1/export`
4. Define Rust types in `src-tauri/src/models.rs`:
   - Derive `Serialize`, `Deserialize` (serde) for all request/response structs
   - Match JSON schemas from Phase 1
5. Register commands in `lib.rs`:
   - `tauri::Builder::default().invoke_handler(tauri::generate_handler![verbalize, sample, export])`
6. Add sidecar lifecycle to app startup:
   - `setup` hook: `start_sidecar()` on app launch
   - `cleanup` hook: `stop_sidecar()` on app exit

**Acceptance Criteria**:
- ✅ Tauri app launches sidecar on startup, sidecar health check passes
- ✅ `invoke('verbalize', { prompt, params })` from React returns distribution JSON
- ✅ `invoke('sample', { distribution_id, seed })` returns selected completion
- ✅ `invoke('export', { dist_ids, format, path })` creates CSV/JSONL file
- ✅ Sidecar crash triggers automatic restart, next command succeeds
- ✅ Rust types match JSON schemas (validated via contract tests)

**Timeline**: 3 days

### Milestone 4: Wire UI to Commands via invoke()

**Goal**: Connect React components to Tauri commands, display distributions, handle user interactions.

**Tasks**:
1. Implement `hooks/useVerbalize.ts`:
   - `verbalize(prompt, params)` → calls `invoke('verbalize', { ... })`
   - State: `loading`, `distribution`, `error`
   - Auto-refresh logic: update `distribution` state when response received (unless pinned)
2. Implement `hooks/useSample.ts`:
   - `sample(distributionId, seed)` → calls `invoke('sample', { ... })`
   - Highlight selected completion in table
3. Implement `hooks/useSession.ts`:
   - `saveSession(distributions, path)` → calls `invoke('save_session', { ... })`
   - `loadSession(path)` → calls `invoke('load_session', { ... })`
   - Replay: call `verbalize` with saved params + seed → verify identical distribution
4. Update `components/PromptPanel.tsx`:
   - Input: prompt text area, k slider (1-100 or 1-500 based on provider), temperature/tau sliders, seed input, model/provider dropdowns
   - Buttons: "Verbalize", "Sample"
   - Call `verbalize()` hook on "Verbalize" click
   - Disable controls during loading
5. Update `components/DistributionPanel.tsx`:
   - Render `DistributionTable` (sortable columns: rank, completion, probability)
   - Render `ProbabilityChart` (Recharts bar chart)
   - "Show Token Details" toggle → expand table rows to show per-token probabilities
   - "Pin Current View" toggle → disable auto-refresh, preserve current distribution
6. Update `components/DistributionTable.tsx`:
   - Sortable columns (click header to sort by rank/probability)
   - Expandable rows (when token details toggle active)
   - Highlight sampled completion (if `sample()` called)
7. Update `components/ProbabilityChart.tsx`:
   - Recharts `<BarChart>` with `<Bar>` for each completion
   - Hover tooltips: show exact p-value + completion text preview
   - Handle k=500 without performance degradation
8. Add loading states, error messages with actionable guidance (per constitution)

**Acceptance Criteria**:
- ✅ User enters prompt "Explain quantum computing", sets k=5, clicks "Verbalize" → table + chart display 5 completions
- ✅ User clicks "Probability" column header → table sorts descending by p-value
- ✅ User activates "Show Token Details" → rows expand to reveal per-token probabilities
- ✅ User activates "Pin Current View", changes k to 10, clicks "Verbalize" → display stays frozen on previous k=5 results
- ✅ User clicks "Sample" → one completion highlights, updates on each click (random seed) or stays same (fixed seed)
- ✅ API error (rate limit) → displays "Rate limit exceeded for OpenAI. Retry in 45 seconds" with countdown

**Timeline**: 4 days

### Milestone 5: Implement Stronghold Key Manager

**Goal**: Integrate Tauri Stronghold plugin for encrypted API key storage, mask keys in UI, redact from logs.

**Tasks**:
1. Add Stronghold plugin to `Cargo.toml`: `tauri-plugin-stronghold`
2. Initialize Stronghold vault in `lib.rs`:
   - Prompt user for master password on first launch (or use OS keychain)
   - Create vault at secure location: `$APP_DATA/verbalized_sampling.stronghold`
3. Implement `src-tauri/src/commands/settings.rs`:
   - `save_api_key(provider: String, key: String) -> Result<(), String>`:
     - Store key in Stronghold vault with ID: `api_key:{provider}`
     - Never log key (redact in debug output)
   - `get_api_key(provider: String) -> Result<String, String>`:
     - Retrieve key from vault, return to Python sidecar (never to React)
   - `test_connection(provider: String) -> Result<ConnectionStatus, String>`:
     - Get key from Stronghold
     - Send test request to sidecar: `POST /api/v1/test_connection`
     - Return status: `active`, `inactive`, `error`
4. Update Python sidecar (`vs_bridge/handlers/`):
   - Modify endpoints to accept API key in request header (from Rust, not React)
   - `POST /api/v1/verbalize` → use key to call provider API
   - `POST /api/v1/test_connection` → verify key with provider
5. Update `components/SettingsPanel.tsx`:
   - API key input fields (masked: `●●●●●●●●`) with "Change" button
   - On save: call `invoke('save_api_key', { provider, key })`
   - On load: display "●●●●●●●●" (never fetch key to React)
   - "Test Connection" button → call `invoke('test_connection', { provider })`
6. Add logging redaction:
   - Rust: replace key in logs with `[REDACTED]`
   - Python: FastAPI middleware to redact `Authorization: Bearer [REDACTED]`

**Acceptance Criteria**:
- ✅ User enters OpenAI key in Settings, clicks "Save" → key encrypts in Stronghold vault
- ✅ User reopens Settings → key field shows "●●●●●●●●" with "Change" button
- ✅ User clicks "Test Connection" → app calls OpenAI API, displays "Connection successful" or error
- ✅ User restarts app → key persists, verbalize works without re-entering key
- ✅ Debug logs show "Authorization: Bearer [REDACTED]", never plaintext key
- ✅ Vault file (`*.stronghold`) is unreadable without master password

**Timeline**: 2 days

### Milestone 6: Add Charts + Session Persistence

**Goal**: Implement Recharts visualization, session save/load, deterministic replay.

**Tasks**:
1. Finalize `components/ProbabilityChart.tsx`:
   - Recharts `<ResponsiveContainer>` for auto-sizing
   - `<BarChart data={completions} />` with `<Bar dataKey="probability" />`
   - Custom tooltips: `<Tooltip content={<CustomTooltip />} />` showing p-value + text preview
   - Color scale: gradient from low (red) to high (green) probability
   - Performance test: render k=500 bars in <100ms
2. Implement session commands in `src-tauri/src/commands/session.rs`:
   - `save_session(distributions: Vec<Distribution>, path: String) -> Result<SessionId, String>`:
     - Serialize to JSON, write to file
     - Include: session ID, app version, timestamp, distributions with full metadata
   - `load_session(path: String) -> Result<Session, String>`:
     - Read JSON, deserialize
     - Version check: if session v1 and app v2, attempt migration or warn
3. Implement Python sidecar session handlers (`vs_bridge/handlers/`):
   - `POST /api/v1/session/save` → write JSONL or JSON to disk
   - `POST /api/v1/session/load` → read file, return session data
4. Update `components/SessionManager.tsx`:
   - "Save Session" button → opens file picker, calls `invoke('save_session', { ... })`
   - "Load Session" button → opens file picker, calls `invoke('load_session', { ... })`
   - "Replay" button (per distribution) → calls `invoke('verbalize', { ...savedParams })`
5. Implement deterministic replay logic:
   - Replay uses saved seed → Python sidecar reproduces exact distribution
   - Compare: original p-values vs replayed p-values → assert exact match (6 decimal precision)
6. Add export functionality:
   - `components/ExportDialog.tsx`: format selection (CSV/JSONL), field selection (optional)
   - Call `invoke('export', { distribution_ids, format, path })`
   - Verify exported file: open in Excel/Python, validate schema

**Acceptance Criteria**:
- ✅ User generates 3 distributions, clicks "Save Session" → JSON file created with all data
- ✅ User restarts app, clicks "Load Session" → all 3 distributions restore with exact p-values
- ✅ User clicks "Replay" on distribution with seed=42 → new distribution matches original (6 decimal precision)
- ✅ User exports distribution to CSV → file contains all fields (completion, probability, model, latency, token_count, etc.)
- ✅ Recharts renders k=500 bars smoothly (<100ms), hover tooltips work
- ✅ Session file version mismatch → displays "Session created with v1.0, current is v1.1. Attempting migration..." and succeeds/fails gracefully

**Timeline**: 3 days

### Milestone 7: QA Checklist Validation

**Goal**: Execute comprehensive testing against spec acceptance criteria, fix bugs, validate constitution compliance.

**Tasks**:
1. Run contract tests (`tests/contract/`):
   - Validate all Tauri → Python messages match JSON schemas
   - Validate all Python → Tauri responses match schemas
   - Test schema versioning: v1 client with v2 sidecar fails gracefully
2. Run integration tests (`tests/integration/`):
   - `test_sidecar_lifecycle.rs`: Verify start/stop/restart, crash recovery
   - `test_offline_mode.py`: Verify full workflow (verbalize, sample, export, session) works without internet
   - `test_export_formats.py`: Verify CSV/JSONL files parse correctly in Excel, pandas, R
3. Run E2E tests (`tests/e2e/`):
   - `test_core_workflow.spec.ts`: Playwright test of entire flow (prompt → verbalize → sample → export)
   - `test_session_replay.spec.ts`: Save session → restart app → load session → replay → verify exact match
4. Manual QA against spec acceptance scenarios:
   - User Story 1, Scenarios 1-7 (basic distribution exploration)
   - User Story 2, Scenarios 1-4 (weighted sampling)
   - User Story 3, Scenarios 1-4 (session persistence)
   - User Story 4, Scenarios 1-4 (export & analysis)
   - User Story 5, Scenarios 1-5 (provider config & security)
   - Edge cases: API rate limit, endpoint crash, k exceeds limit, etc.
5. Constitution compliance audit:
   - ✅ Offline mode: Verify local vLLM works without internet
   - ✅ Secrets: Verify keys encrypted, never in logs/UI/errors
   - ✅ JSON contracts: Verify all IPC uses versioned schemas
   - ✅ Sidecar pattern: Verify Rust has no ML logic, Python black box unchanged
   - ✅ Module independence: Verify each module (UI, Rust, Python) testable in isolation
6. Performance validation:
   - App startup <3s (including sidecar)
   - Verbalize <10s (API, k=10), <5s (local, k=10)
   - Export <2s (100 distributions)
   - Token details expansion <1s (k≤100)
   - UI responsiveness <100ms
7. Cross-platform testing:
   - Windows 10: Install, run, test core workflow
   - macOS 12 (x64 + ARM64): Install, run, test core workflow
   - Ubuntu 20.04: Install, run, test core workflow
8. Bug fixes and polish:
   - Address all failing tests
   - Improve error messages for actionable guidance
   - Add loading spinners, progress indicators
   - Refine UI layout, responsive design

**Acceptance Criteria**:
- ✅ All contract tests pass (Tauri ↔ Python schema validation)
- ✅ All integration tests pass (sidecar lifecycle, offline mode, export formats)
- ✅ All E2E tests pass (core workflow, session replay)
- ✅ All spec acceptance scenarios validated manually (36+ scenarios)
- ✅ All edge cases handled gracefully (8 scenarios)
- ✅ All success criteria met (14 metrics: SC-001 to SC-014)
- ✅ Constitution compliance: 100% on all 7 principles
- ✅ Cross-platform: App runs on Win/Mac/Linux without errors
- ✅ Performance: All benchmarks within targets

**Timeline**: 4 days

## Total Timeline Estimate

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Phase 0: Research | 2-3 days | `research.md`, prototype, PyInstaller test, Stronghold test |
| Phase 1: Design | 3-4 days | `data-model.md`, `contracts/`, `quickstart.md`, ADRs |
| **Phase 2: Implementation** | **19 days total** | **Working app** |
| ├─ Milestone 1: Scaffold | 1 day | Tauri + React structure |
| ├─ Milestone 2: Sidecar | 2 days | PyInstaller binary |
| ├─ Milestone 3: Commands | 3 days | Rust commands + sidecar IPC |
| ├─ Milestone 4: UI Wiring | 4 days | React → Tauri → Python flow |
| ├─ Milestone 5: Stronghold | 2 days | Encrypted secrets |
| ├─ Milestone 6: Charts + Sessions | 3 days | Recharts, save/load, replay |
| ├─ Milestone 7: QA | 4 days | Testing, validation, bug fixes |
| **Total** | **24-26 days** | **Production-ready desktop app** |

**Assumptions**:
- 1 full-time developer (or equivalent distributed capacity)
- No major blockers in Tauri 2 + Stronghold compatibility
- PyInstaller bundling works without significant debugging
- Existing `verbalized_sampling` package is stable and well-tested

**Risk Mitigation**:
- **Risk**: PyInstaller binary size exceeds 100MB → **Mitigation**: Exclude unnecessary deps, use UPX compression
- **Risk**: Stronghold plugin incompatible with Tauri 2 stable → **Mitigation**: Fallback to OS keychain (macOS/Windows), encrypted JSON (Linux)
- **Risk**: FastAPI async conflicts with PyInstaller → **Mitigation**: Use sync Flask alternative, or stdio IPC instead of HTTP
- **Risk**: Recharts k=500 bars cause lag → **Mitigation**: Virtualized scrolling, lazy render, or limit UI to k=100 (export supports 500)

## Next Steps

1. **Start Phase 0**: Run `/speckit.plan` research tasks to validate technical feasibility
2. **Create `research.md`**: Document prototype findings, dependency compatibility, performance benchmarks
3. **Start Phase 1**: Define JSON schemas in `contracts/`, document data model in `data-model.md`
4. **Write `quickstart.md`**: Enable new developers to contribute
5. **Kick off Phase 2**: Begin Milestone 1 (Tauri scaffold) once research validates architecture

**Dependencies**:
- Tauri 2 stable release (verify version)
- Stronghold plugin compatibility (research Phase 0)
- PyInstaller bundling of `verbalized_sampling` (test Phase 0)
- React + Recharts in Tauri webview (test Phase 0)

**Success Metrics** (from spec):
- ✅ App startup <3s
- ✅ Verbalize <10s (API), <5s (local)
- ✅ UI responsive <100ms
- ✅ Offline mode feature-complete
- ✅ Deterministic replay 100% accurate
- ✅ Zero key exposure in logs/UI/errors
- ✅ All 7 constitution principles compliant

**Ready to proceed with `/speckit.tasks` to generate detailed task breakdown** once Phase 0 research confirms architecture feasibility.
