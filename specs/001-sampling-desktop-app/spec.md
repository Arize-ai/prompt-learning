# Feature Specification: Verbalized Sampling Desktop App

**Feature Branch**: `001-sampling-desktop-app`
**Created**: 2025-10-16
**Status**: Draft
**Input**: User description: "Feature: Verbalized Sampling Desktop App - Provide a GUI for exploring and exporting LLM output distributions."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic Distribution Exploration (Priority: P1)

A researcher wants to understand how an LLM responds to a given prompt by visualizing the probability distribution of multiple possible completions, enabling them to see not just one answer but the model's uncertainty and alternative responses.

**Why this priority**: This is the core value proposition - transforming invisible sampling distributions into visible, explorable data. Without this, the app has no purpose.

**Independent Test**: Can be fully tested by entering a prompt, clicking "Verbalize", and seeing a table + chart of weighted completions. Delivers immediate value for understanding model behavior.

**Acceptance Scenarios**:

1. **Given** app is open with no session loaded, **When** user enters prompt "Explain quantum entanglement" and sets k=5, temperature=0.8, **Then** system displays 5 completions with probability values summing to ~1.0
2. **Given** distribution is displayed, **When** user clicks column header "Probability", **Then** table sorts by probability (descending by default)
3. **Given** distribution is displayed, **When** user hovers over a bar in the chart, **Then** tooltip shows exact p-value and completion text preview
4. **Given** user adjusts temperature slider from 0.8 to 1.2, **When** user clicks "Verbalize" again, **Then** new distribution reflects higher randomness (more even probabilities) and display auto-refreshes to show new results
5. **Given** offline mode is active (no internet), **When** user selects local vLLM endpoint and runs verbalize, **Then** distribution generates successfully without network calls
6. **Given** distribution is displayed with summary p-values, **When** user clicks "Show Token Details" toggle, **Then** table rows expand to reveal token-level probabilities for each completion with per-token breakdown
7. **Given** user is analyzing current distribution, **When** user activates "Pin Current View" toggle and then runs new verbalize, **Then** display remains frozen showing pinned distribution (no auto-refresh) until user unpins or manually loads new results

---

### User Story 2 - Weighted Sampling Execution (Priority: P2)

A user wants to sample one completion from the distribution based on the calculated probabilities, simulating the actual sampling process that LLMs use internally, to see which response would be chosen in practice.

**Why this priority**: Complements distribution exploration by showing the probabilistic selection process in action. Bridges theory (distributions) and practice (actual sampling).

**Independent Test**: Can be tested by loading a pre-generated distribution, clicking "Sample", and verifying one completion is selected according to weights. Works without needing to verbalize first if a session is loaded.

**Acceptance Scenarios**:

1. **Given** a distribution with 5 completions is displayed, **When** user clicks "Sample" button, **Then** exactly one completion is highlighted/selected based on probability weights
2. **Given** seed value is set to 42, **When** user clicks "Sample" multiple times with same distribution and seed, **Then** same completion is selected each time (deterministic)
3. **Given** seed value is set to "random" (no seed), **When** user clicks "Sample" 100 times, **Then** selections approximately match the probability distribution (e.g., 30% probability item selected ~30 times)
4. **Given** user has sampled a completion, **When** user clicks "Export Sample", **Then** selected completion saves to file with metadata (prompt, parameters, p-value, timestamp)

---

### User Story 3 - Session Persistence & Replay (Priority: P2)

A researcher wants to save their exploration session (prompts, parameters, distributions) and reload it later to reproduce results or share findings with colleagues, ensuring reproducibility of probabilistic experiments.

**Why this priority**: Scientific reproducibility is critical for research tools. Enables collaboration, debugging, and building on previous work.

**Independent Test**: Can be tested by creating a distribution, saving session, closing app, reopening app, loading session, and verifying exact reproduction of distributions and parameters.

**Acceptance Scenarios**:

1. **Given** user has generated 3 distributions with different prompts, **When** user clicks "Save Session", **Then** all prompts, parameters, distributions, and timestamps save to .json file
2. **Given** saved session file exists, **When** user clicks "Load Session" and selects file, **Then** all previous distributions restore with exact p-values and parameters
3. **Given** loaded session contains seed values, **When** user clicks "Replay" on a specific distribution, **Then** system re-runs verbalize/sample with saved parameters and produces identical results
4. **Given** user wants to share findings, **When** user exports session to JSONL format, **Then** file contains one JSON object per distribution in chronological order

---

### User Story 4 - Export & Analysis (Priority: P3)

A data scientist wants to export distribution data to CSV/JSONL format for further analysis in external tools (Excel, Python, R), enabling integration with existing research pipelines.

**Why this priority**: Interoperability with research workflows. Unlocks advanced analysis not built into the app.

**Independent Test**: Can be tested by generating a distribution, clicking "Export to CSV/JSONL", and verifying the exported file contains all distribution data in correct format.

**Acceptance Scenarios**:

1. **Given** a distribution is displayed, **When** user selects "Export to CSV" and chooses file location, **Then** CSV file contains: completion_text, probability, rank, prompt, model, temperature, seed, k, tau, token_count, api_latency_ms, api_version, timestamp
2. **Given** user selects JSONL format, **When** export completes, **Then** each line is valid JSON with schema: {"prompt": str, "completion": str, "probability": float, "parameters": {...}}
3. **Given** user has multiple distributions in session, **When** user clicks "Export All", **Then** single file contains all distributions with clear delimiters/identifiers
4. **Given** exported CSV/JSONL file, **When** user opens in Excel/Python, **Then** data loads without errors and maintains precision (probability values to 6 decimal places)

---

### User Story 5 - Provider Configuration & Security (Priority: P2)

A user needs to configure API keys for different LLM providers (OpenAI, Anthropic, Cohere) and local endpoints securely, ensuring credentials are encrypted and never exposed in logs or UI.

**Why this priority**: Security is non-negotiable for professional tools. Multi-provider support enables flexibility. P2 because app works offline without this, but API access is a core feature.

**Independent Test**: Can be tested by opening Settings, entering API key, saving, restarting app, and verifying: (1) key persists, (2) key works for API calls, (3) key never appears in logs/UI after save.

**Acceptance Scenarios**:

1. **Given** user opens Settings panel, **When** user enters OpenAI API key in masked field and clicks "Save", **Then** key encrypts via Stronghold and saves to secure vault
2. **Given** API key is saved, **When** user reopens Settings, **Then** key field shows "●●●●●●●●" (masked) with "Change" button, never showing plaintext
3. **Given** user enters local vLLM endpoint "http://localhost:8000", **When** user clicks "Test Connection", **Then** system verifies endpoint is reachable and displays model list or error
4. **Given** user enables diagnostic logs, **When** system logs API calls, **Then** logs show "Authorization: Bearer [REDACTED]" not actual key
5. **Given** multiple providers configured, **When** user selects provider dropdown in main panel, **Then** only providers with valid keys/endpoints appear as enabled options

---

### User Story 6 - Advanced Analysis (Optional) (Priority: P4)

An advanced user wants to run comparative experiments (same prompt, different models/temperatures) and visualize entropy/diversity metrics to quantify distribution characteristics.

**Why this priority**: Power user feature, not critical for MVP. Adds research depth for users who need it.

**Independent Test**: Can be tested independently by creating 2+ distributions with same prompt but different parameters, clicking "Compare", and seeing side-by-side visualization.

**Acceptance Scenarios**:

1. **Given** user has generated 2 distributions (same prompt, different temperatures), **When** user selects both and clicks "Compare", **Then** side-by-side bar charts display with difference highlighting
2. **Given** comparative view is active, **When** user hovers over completion present in both distributions, **Then** tooltip shows probability delta (e.g., "Model A: 0.35, Model B: 0.12, Δ: -0.23")
3. **Given** distribution is displayed, **When** user clicks "Show Entropy", **Then** system calculates Shannon entropy H = -Σ(p*log(p)) and displays value with interpretation (low/medium/high uncertainty)
4. **Given** entropy is shown for multiple distributions, **When** user sorts by entropy, **Then** distributions rank from most certain (low H) to most uncertain (high H)

---

### Edge Cases

- **What happens when API rate limit is hit?** System displays clear error "Rate limit exceeded for [provider]. Retry in [X] seconds" and disables "Verbalize" button temporarily with countdown timer.
- **What happens when local vLLM endpoint crashes mid-request?** System detects timeout/connection error, displays "Local endpoint unresponsive. Check that vLLM server is running at [endpoint]", and offers to retry or switch to API mode.
- **What happens when k (number of samples) exceeds model capacity?** System validates k against model-specific limits (k ≤ 100 for API providers, k ≤ 500 for local vLLM) and shows error "k must be ≤ [limit] for [provider type]. Adjusted to maximum." and auto-corrects value.
- **What happens when user tries to load a session file from incompatible app version?** System detects schema version mismatch, displays "Session created with v[X], current version is v[Y]. Attempting migration..." and either succeeds with warnings or fails gracefully with actionable message.
- **What happens when probability values don't sum to 1.0 due to sampling artifacts?** System normalizes probabilities by dividing each by sum(all_probs) and displays warning icon with tooltip "Probabilities normalized (original sum: [X])" for transparency.
- **What happens when user enters malformed prompt (e.g., SQL injection attempt)?** System sanitizes input by escaping special characters, passes safe version to Python backend, and logs security event (prompt hash, not content) for audit.
- **What happens when disk is full during session save?** System detects write failure, displays "Insufficient disk space. Free up [X] MB and try again", and preserves in-memory session without data loss.
- **What happens when user switches provider mid-session without saving?** System displays confirmation dialog "Unsaved changes will be lost. Save session before switching?" with options: Save & Switch, Discard & Switch, Cancel.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept prompt text input with minimum 1 character, maximum 10,000 characters
- **FR-002**: System MUST provide adjustable controls for: k (model-dependent: 1-100 for API providers, 1-500 for local vLLM), τ/top-p (0.0-1.0), temperature (0.0-2.0), model selection, provider selection, seed (integer or null)
- **FR-003**: System MUST execute "Verbalize" operation that generates k completions with associated probability values via Python backend
- **FR-004**: System MUST execute "Sample" operation that selects exactly one completion based on probability weights using specified seed (deterministic) or random seed
- **FR-005**: System MUST display distribution results in both sortable table format (columns: rank, completion, probability, actions) and probability bar chart with hover tooltips; table MUST show summary p-values by default with optional "Show Token Details" toggle to expand rows and reveal token-level probabilities
- **FR-006**: System MUST support export to JSONL format (one JSON object per line) and CSV format (standard comma-separated with headers); exports MUST include comprehensive trace metadata: model name, API latency, token count, all generation parameters (k, τ, temperature, seed), API version/endpoint, and timestamp
- **FR-007**: System MUST save session state to JSON file including: all distributions, prompts, parameters, timestamps, app version, and metadata
- **FR-008**: System MUST load previously saved sessions and restore all distributions with exact parameter fidelity
- **FR-009**: System MUST replay saved distributions with same seed to reproduce identical results (deterministic replay)
- **FR-010**: System MUST provide Settings panel for configuring: provider API keys (OpenAI, Anthropic, Cohere, custom), local vLLM endpoint URL, theme (light/dark/system), diagnostic logging level
- **FR-011**: System MUST encrypt all API keys using Tauri Stronghold vault with user master password
- **FR-012**: System MUST support both online mode (API providers) and offline mode (local vLLM) with feature parity
- **FR-013**: System MUST communicate with Python `verbalized_sampling` backend via JSON contracts over IPC or HTTP
- **FR-014**: System MUST validate endpoint connectivity via "Test Connection" feature before enabling provider
- **FR-015**: System MUST mask API keys in UI (display as "●●●●●●●●") and redact from logs ([REDACTED])
- **FR-016**: System MUST normalize probability distributions that don't sum to 1.0 and display normalization warning
- **FR-017**: System MUST handle API errors gracefully with user-friendly messages and suggested actions
- **FR-018**: System MUST persist user preferences (theme, default provider, diagnostic settings) across sessions
- **FR-019**: System MUST auto-refresh distribution display when new results are generated; MUST provide "Pin Current View" toggle to prevent auto-refresh and preserve current distribution for comparison/analysis
- **FR-020** (Optional): System SHOULD support comparative analysis of 2+ distributions with side-by-side visualization
- **FR-021** (Optional): System SHOULD calculate and display Shannon entropy for distribution uncertainty quantification

### Key Entities

- **Prompt**: User-provided text input for generation; includes text content, creation timestamp, optional description/label
- **Distribution**: Set of k completions with probabilities; tied to specific prompt, model, and parameters; includes normalized p-values, raw p-values, generation timestamp
- **Completion**: Single generated text output; includes completion text, summary probability value, rank within distribution, selection count (if sampled), optional token-level probabilities (array of {token: str, p_value: float})
- **Session**: Collection of distributions with metadata; includes session ID, creation timestamp, app version, all associated distributions, user notes
- **Parameter Set**: Configuration for generation; includes k, τ, temperature, seed, model identifier, provider identifier
- **Provider Config**: Connection settings for LLM service; includes provider name (OpenAI/Anthropic/Cohere/local), encrypted API key or endpoint URL, connection status (active/inactive/error), last tested timestamp
- **Export Record**: Serialized distribution data; includes format (JSONL/CSV), file path, export timestamp, comprehensive trace metadata (model name, API latency, token count, all generation parameters, API version/endpoint)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can generate and visualize a probability distribution in under 10 seconds for API calls, under 5 seconds for local inference (k=10, typical prompt length)
- **SC-002**: System maintains accuracy with probability values precise to 6 decimal places and normalized sums within 0.001 of 1.0
- **SC-003**: Deterministic replay produces identical distributions 100% of the time when using same seed, model, and parameters
- **SC-004**: Session save/load operations complete in under 2 seconds for sessions containing up to 100 distributions
- **SC-005**: Exported files (CSV/JSONL) are immediately compatible with Excel, Python pandas, and R without preprocessing (validated by opening in each tool)
- **SC-006**: API key security maintains zero exposure: keys never appear in logs, UI after save, error messages, or network traffic outside encrypted channels
- **SC-007**: Offline mode operates with full feature parity to API mode (verbalize, sample, export, session management) without network connectivity
- **SC-008**: System handles API errors gracefully with 95% of errors resulting in actionable user messages (not generic "Error occurred")
- **SC-009**: Users can complete core workflow (enter prompt → verbalize → review distribution → export) in under 30 seconds after initial setup
- **SC-010**: Comparative analysis (optional feature) renders side-by-side distributions for up to 10 comparisons in under 3 seconds
- **SC-011**: App startup time is under 3 seconds on standard hardware (Python sidecar initialization included)
- **SC-012**: System supports sessions with up to 1000 distributions without performance degradation (UI remains responsive <100ms for interactions)
- **SC-013**: Token details view renders expandable rows with per-token probabilities in under 1 second for distributions with k ≤ 100
- **SC-014**: Pin Current View toggle prevents auto-refresh 100% of the time when active; unpinning immediately enables auto-refresh for next generation

## Assumptions

- **Model Access**: Users have either (1) valid API keys for at least one supported provider, or (2) local vLLM server running and accessible
- **Python Environment**: Python 3.9+ with `verbalized_sampling` package is installed and accessible to Tauri sidecar
- **Display Requirements**: Users have minimum 1280x720 resolution display for optimal table/chart visibility
- **Network Reliability**: API mode users have stable internet connection with <5% packet loss for consistent results
- **Disk Space**: Users have at least 100MB free disk space for session files, exports, and application data
- **Supported Providers**: Initial release supports OpenAI, Anthropic, Cohere, and generic OpenAI-compatible endpoints (including local vLLM)
- **Entropy Calculation**: Shannon entropy formula H = -Σ(p*log₂(p)) is sufficient for uncertainty quantification (no Jensen-Shannon divergence or KL-divergence needed initially)
- **Export Formats**: CSV and JSONL are sufficient for 90% of user workflows; additional formats (Parquet, Excel) are not priority
- **Session Schema**: JSON session format is stable and includes versioning to support backward compatibility across app updates
- **Security Model**: Stronghold vault provides adequate encryption for API keys; hardware security modules (HSM) not required for initial release
- **Comparative Analysis**: Side-by-side comparison of up to 10 distributions is sufficient; matrix comparisons of 10+ distributions are advanced use case for future versions
