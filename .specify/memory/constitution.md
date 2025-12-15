<!--
Sync Impact Report
==================
Version Change: 1.1.0 → 1.2.0
Modified Principles:
  - I. Deployment Flexibility → Strengthened offline-first mandate, clarified reasoning toolkit nature
  - III. Pluggable Inference Architecture → Refined to emphasize JSON contracts, sidecar pattern
  - VI. Desktop-First Architecture → Updated to focus on visualization of sampling distributions
Added Sections:
  - VII. Module Independence & Maintainability (one-person ownership model)
  - Architecture Requirements → Added JSON Contract Requirements, Sidecar Orchestration Pattern
Removed Sections: None
Templates Requiring Updates:
  ✅ plan-template.md - Constitution Check validates JSON contracts and module independence
  ✅ spec-template.md - User stories align with toolkit and visualization features
  ✅ tasks-template.md - Task organization supports modular architecture with clear boundaries
Follow-up TODOs: None
-->

# Prompt Learning Constitution

## Project Identity

This repository defines a **local and API-connected reasoning toolkit** that evolves into
a cross-platform Tauri 2 desktop app for visualizing and manipulating LLM sampling
distributions produced by the Python `verbalized_sampling` package.

## Core Principles

### I. Deployment Flexibility (Offline-First)

**The system MUST support both offline and API-based deployment with zero cloud dependency.**

- All inference capabilities MUST work with local vLLM deployment (offline mode)
- All inference capabilities MUST work with API providers (OpenAI, Anthropic, etc.)
- Model backend selection MUST be runtime-configurable, not compile-time
- **No functionality may assume internet connectivity or cloud services for core operation**
- API keys and endpoints MUST be optional configuration, not hard requirements
- Desktop application MUST function fully offline without feature degradation
- **Offline mode via local vLLM must remain feature-complete** (parity with API mode)

**Rationale**: As a reasoning toolkit, the system must be trustworthy and independent.
Academic users need offline capabilities for reproducibility and cost control. Production
users need API flexibility. Removing cloud dependencies ensures users maintain control
over their prompts, data, and inference pipelines regardless of network availability.

### II. Security & Secrets Management

**All secrets MUST be encrypted at rest using Stronghold (mandatory) and never logged.**

- API keys, tokens, and credentials MUST be encrypted via Tauri's Stronghold vault
- **Stronghold is mandatory for secret storage** - no alternative backends permitted
- Secrets MUST NOT appear in logs, error messages, stack traces, or debug output
- Default configuration files MUST use placeholders (e.g., `YOUR_API_KEY_HERE`), never real keys
- Repository MUST include `.gitignore` entries for all secret-containing files
- Stronghold vault MUST be the single source of truth for all credentials
- Desktop app MUST use OS-level keychain integration where available (via Stronghold)
- Documentation MUST provide clear guidance on Stronghold secret management

**Rationale**: Reasoning toolkits handle sensitive API keys and proprietary prompts.
Stronghold provides military-grade encryption and secure secret storage, eliminating
plaintext credential risks. This is critical for desktop deployment where users have
filesystem access and expect professional-grade security.

### III. Pluggable Inference Architecture

**Core inference logic MUST be modular with Python `verbalized_sampling` as the
black-box engine (no rewrite). All UI ↔ core communication via JSON contracts.**

- **The `verbalized_sampling` Python package remains the black-box inference engine**
- Python core MUST NOT be rewritten in Rust or any other language
- **All UI ↔ core communication occurs via JSON contracts** (versioned schemas)
- Model backends (HuggingFace, vLLM, OpenAI, Anthropic, MLX, Ollama) MUST implement common interface
- Tauri frontend MUST communicate with Python backend via JSON over IPC or HTTP
- Python engine MUST be executable as standalone process (sidecar pattern)
- New backends MUST be addable without modifying core optimizer logic
- Prompt optimization algorithms MUST be independent of specific model providers
- Evaluator and feedback components MUST work with any backend
- Backend-specific code MUST be isolated in dedicated modules (e.g., `optimizer_sdk/backends/`)

**Rationale**: The `verbalized_sampling` module encapsulates research innovations and
probabilistic reasoning logic. Preserving it as a Python black box maintains research
velocity, NumPy/PyTorch ecosystem access, and scientific reproducibility. JSON contracts
provide clean boundaries enabling independent evolution of UI and inference layers.

### IV. Test-First Development

**Tests MUST be written before implementation for all core functionality.**

- Red-Green-Refactor cycle: Write failing test → Implement → Refactor
- New features require unit tests for isolated components
- Integration tests MUST verify cross-backend compatibility
- Desktop app MUST include UI tests for critical user workflows
- **IPC/API boundary between Tauri and Python MUST have contract tests** (JSON schema validation)
- Optimizer workflows MUST have end-to-end tests with sample datasets
- Breaking changes MUST include tests demonstrating backward compatibility or migration path
- JSON contract changes MUST include schema version bump and compatibility tests

**Rationale**: Prompt learning involves complex feedback loops and probabilistic outputs.
Test-first development catches regressions early, documents expected behavior, and ensures
reliability across model backends. JSON contract testing prevents silent breaking changes
at the Tauri-Python boundary.

### V. Observability & Debugging

**All optimizer operations MUST produce structured, debuggable output.**

- Optimizer runs MUST log: input prompts, feedback, generated variants, selection criteria
- **Sampling distributions MUST be exportable in JSON and human-readable formats**
- Model calls MUST log: backend used, tokens consumed, latency, errors
- Outputs MUST support both JSON (machine-readable) and human-readable formats
- Desktop app MUST provide in-app log viewer with filtering and export
- Debug mode MUST expose intermediate states without requiring code changes
- Error messages MUST include actionable guidance (e.g., "Check API key" not "Auth failed")
- Tauri-Python IPC errors MUST surface clearly in UI with troubleshooting hints

**Rationale**: Debugging prompt optimization failures requires visibility into the
feedback loop and sampling distributions. Desktop users expect visual debugging tools,
not CLI log diving. Structured logs enable analysis of which feedback improved prompts
and integration with observability tools like Arize Phoenix.

### VI. Desktop-First Architecture (Tauri 2)

**The application MUST evolve into a cross-platform desktop app built with Tauri 2 that
visualizes and manipulates LLM sampling distributions.**

- Tauri 2 is the primary deployment target (Windows, macOS, Linux)
- Python `verbalized_sampling` package remains the inference engine (no rewrite)
- **Rust layer orchestrates sidecar calls, NOT business logic** (Python owns inference)
- **Primary UX: visualize and manipulate LLM sampling distributions** from `verbalized_sampling`
- Rust backend handles: UI rendering, sidecar process management, filesystem access, system integration
- Python backend handles: model inference, prompt optimization, feedback processing, distribution generation
- Communication via JSON contracts over Tauri commands (IPC) or localhost HTTP for streaming
- Application MUST support single-binary distribution where feasible
- Web-based UI (HTML/CSS/JS) running in Tauri webview for cross-platform consistency
- NO Electron dependency - Tauri's Rust core for security and performance

**Rationale**: Desktop deployment provides better UX for reasoning toolkit users
(visualization, drag-drop, native menus) while maintaining the research SDK's Python core.
Tauri 2 offers smaller binaries, better security, and lower resource usage than Electron.
The sidecar pattern keeps Rust focused on orchestration, not ML logic, preserving the
Python-Rust boundary.

### VII. Module Independence & Maintainability

**Each module MUST be independently maintainable with one-person ownership model.**

- **Each module is independently maintainable** - clear boundaries, minimal coupling
- Modules MUST have single-person ownership capability (one developer can understand/maintain)
- Module interfaces MUST be documented with JSON schemas or typed contracts
- Inter-module communication MUST use versioned contracts (prevent implicit dependencies)
- Breaking a module MUST NOT cascade failures to other modules (graceful degradation)
- Module dependencies MUST form a DAG (Directed Acyclic Graph) - no circular dependencies
- Each module MUST have isolated test suite runnable without other modules
- Module-level README MUST document: purpose, inputs/outputs, testing instructions, ownership

**Rationale**: One-person maintainability ensures the project remains manageable as it
grows. Clear module boundaries with JSON contracts prevent the codebase from becoming
a tangled monolith. This principle enables contributors to work independently on
visualization, inference, or UI without coordinating complex merges.

## Architecture Requirements

### Technology Stack

- **Frontend**: Tauri 2 (Rust) with web-based UI (React/Vue/Svelte or vanilla JS)
- **Inference Engine**: Python `verbalized_sampling` package (black box, no rewrite)
- **IPC Layer**: JSON contracts over Tauri commands (lightweight) or HTTP (streaming/long-running)
- **Secrets**: Stronghold vault (Tauri built-in, mandatory)
- **Storage**: SQLite for application state, filesystem for datasets/outputs
- **Build**: Rust toolchain (cargo), Python packaging (pip/poetry), Tauri CLI

### Separation of Concerns

- **Tauri Rust Layer**:
  - Sidecar process orchestration (start/stop Python service)
  - UI rendering and window management
  - Settings management and Stronghold integration
  - Filesystem access and result visualization
  - **NO business logic, NO inference logic, NO ML code**

- **Python `verbalized_sampling` Package**:
  - All ML/optimization logic (black box)
  - Model API calls and backend management
  - Feedback loop processing
  - Sampling distribution generation
  - Prompt optimization algorithms

- **Shared Contract**:
  - JSON-based IPC protocol with versioned schemas
  - Schema registry for contract validation
  - Backward compatibility guarantees via semantic versioning

### JSON Contract Requirements

- All Tauri ↔ Python communication MUST use JSON schemas
- Schema files MUST be versioned (e.g., `contract.v1.json`, `contract.v2.json`)
- Breaking schema changes MUST bump major version
- Backward compatibility MUST be maintained for at least one major version
- Contract violations MUST fail fast with clear error messages
- Schema validation MUST occur on both Tauri and Python sides

### Sidecar Orchestration Pattern

- Python `verbalized_sampling` runs as Tauri sidecar process
- Tauri manages sidecar lifecycle (start on app launch, stop on app close)
- Health checks MUST verify sidecar availability before sending commands
- Sidecar crashes MUST trigger graceful restart with user notification
- Sidecar logs MUST be captured and viewable in Tauri UI
- Long-running operations MUST use HTTP streaming, not blocking IPC

### Migration Path

- **Phase 1**: Wrap existing `verbalized_sampling` as Python service with JSON HTTP API
- **Phase 2**: Build Tauri shell calling Python service via localhost (validate sidecar pattern)
- **Phase 3**: Implement sampling distribution visualization UI (core UX)
- **Phase 4**: Bundle Python runtime with Tauri for single-binary distribution
- **Phase 5**: Optimize IPC for performance, add offline model management UI

## Security Requirements

**Data Privacy**:
- User prompts and feedback MUST NOT be transmitted to external services without explicit opt-in
- Local mode MUST guarantee no data leaves the machine
- API mode MUST document which data is sent to which providers
- Desktop app MUST display clear indicators when network requests occur
- Stronghold vault MUST be encrypted with user-provided master password

**Dependency Security**:
- All Python dependencies MUST be pinned to specific versions in `requirements.txt`
- All Rust dependencies MUST be pinned in `Cargo.toml`
- Critical vulnerabilities in dependencies MUST be addressed within 30 days of disclosure
- New dependencies MUST be justified and security-reviewed before addition
- Tauri security audits MUST be reviewed before upgrading major versions

**Access Control**:
- Multi-user desktop deployments MUST support per-user Stronghold vaults
- File-based secrets MUST use restrictive permissions (chmod 600 or equivalent)
- IPC between Tauri and Python MUST validate message schemas to prevent injection

**Sandboxing**:
- Python sidecar process MUST run with minimal filesystem permissions
- Tauri capabilities MUST follow principle of least privilege
- User-uploaded datasets MUST be scanned for malicious content before processing
- Sidecar communication MUST use localhost-only binding (no external exposure)

## Development Workflow

**Contribution Process**:
- All changes via feature branches and pull requests
- PRs MUST include tests for new functionality
- PRs MUST pass existing test suite before merge
- Breaking changes MUST update major version and include migration guide
- UI changes MUST include screenshots or video in PR description
- JSON contract changes MUST include schema diff and migration notes

**Code Review Requirements**:
- Security-related changes (secrets handling, auth, IPC) require two approvals
- New backends require validation across at least two model providers
- Performance-critical changes require benchmarking before/after
- Tauri-Python integration changes require testing on all three platforms (Win/Mac/Linux)
- JSON contract changes require compatibility testing with previous schema version

**Release Process**:
- Semantic versioning: MAJOR.MINOR.PATCH
- Release notes MUST document breaking changes, new features, and deprecations
- PyPI releases MUST include verified GPG signatures (Python SDK)
- Desktop releases MUST include signed binaries (Windows/macOS code signing)
- Linux releases via AppImage, Flatpak, or .deb/.rpm packages
- JSON schema versions MUST be published alongside releases

**Platform Testing**:
- CI MUST test on Windows, macOS, and Linux for desktop builds
- Python components MUST test on Python 3.9+ (match Tauri compatibility)
- UI components MUST test in Tauri webview, not just browser
- Sidecar orchestration MUST test process lifecycle on all platforms

## Governance

**Constitution Authority**: This constitution supersedes informal practices and verbal
agreements. When conflict arises between this document and implementation, the constitution
governs.

**Amendment Procedure**:
1. Propose change via PR with updated constitution and rationale
2. Document impact on existing code, templates, and workflows
3. Require approval from at least two maintainers
4. Include migration plan for breaking governance changes

**Compliance Review**:
- All PRs MUST verify alignment with core principles (offline-first, JSON contracts, sidecar pattern, module independence)
- Quarterly audits verify: secrets use Stronghold, Python remains black box, JSON contracts validated, modules independently maintainable
- Violations require documented justification or remediation plan

**Complexity Justification**: Any addition of complexity (new abstraction layer, design pattern,
dependency) MUST include rationale explaining:
- Problem solved
- Simpler alternative considered and rejected
- Maintenance burden assessment
- Impact on one-person maintainability

**Version**: 1.2.0 | **Ratified**: 2025-10-16 | **Last Amended**: 2025-10-16
