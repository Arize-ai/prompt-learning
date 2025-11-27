# Verbalized Sampling - Feature Gaps & Improvements

## Critical Gaps (Blocking MVP)

### 1. ❌ API Key Management UI
**Status**: Missing
**Current**: Requires environment variables
**Needed**:
- Settings panel to enter/save API keys
- Secure storage using Tauri Stronghold plugin
- Per-provider key validation
- Visual feedback when keys are missing/invalid

### 2. ❌ Missing Tauri Commands
**Status**: Only `verbalize` command implemented
**Defined but not implemented**:
- `sample` - Sample from existing distribution
- `export` - Export distributions to CSV/JSONL
- `session_save` - Save session to file
- `session_load` - Load session from file

### 3. ❌ Session Management UI
**Status**: Types defined, backend implemented, no UI
**Needed**:
- Save current session button
- Load previous session
- Session browser/history
- Auto-save functionality

### 4. ❌ Export Functionality UI
**Status**: Backend implemented, no UI
**Needed**:
- Export button per distribution
- Batch export multiple distributions
- Format selection (CSV/JSONL)
- Metadata inclusion toggle

### 5. ❌ Sampling from Distribution UI
**Status**: Backend implemented, no UI
**Needed**:
- "Sample" button on each distribution
- Optional seed input
- Display sampled completion
- Show probability of selected item

## Important Features (Missing UI)

### 6. ❌ Distribution History
**Status**: App.tsx shows only current distribution
**Needed**:
- Sidebar with list of past distributions
- Click to view any distribution
- Delete distributions
- Search/filter distributions

### 7. ❌ Token Probabilities Visualization
**Status**: Checkbox exists but no visualization
**Needed**:
- Token-by-token probability display
- Color-coded tokens by probability
- Expandable/collapsible view
- Export token data

### 8. ❌ Error Handling & Validation
**Status**: Basic errors, no user-friendly UI
**Needed**:
- Clear error messages for missing API keys
- Provider/model compatibility validation
- Network error handling
- Retry mechanisms

### 9. ❌ Settings/Preferences Panel
**Status**: Types defined, no UI
**Needed**:
- Theme selection (light/dark)
- Default provider/model
- Default k, tau, temperature
- Auto-save session toggle
- Export format preferences

## Nice-to-Have Features

### 10. 📋 Prompt Templates
**Status**: Not implemented
**Value**: Common prompts for testing/experimentation
**Features**:
- Pre-defined prompt library
- Custom template creation
- Template categories (coding, writing, analysis)

### 11. 📊 Comparison View
**Status**: Not implemented
**Value**: Compare distributions side-by-side
**Features**:
- Select 2+ distributions
- Side-by-side visualization
- Highlight differences
- Compare probabilities

### 12. 📈 Analytics Dashboard
**Status**: Not implemented
**Value**: Track usage and costs
**Features**:
- API call count per provider
- Token usage statistics
- Estimated costs
- Model performance metrics

### 13. 🎨 Visualization Improvements
**Current**: Basic probability bars
**Could add**:
- Probability distribution chart
- Entropy/diversity metrics
- Interactive probability adjustment
- 3D visualization for multi-dimensional analysis

### 14. 🔄 Batch Processing
**Status**: Not implemented
**Value**: Process multiple prompts
**Features**:
- CSV/JSONL input with prompts
- Batch generation
- Progress tracking
- Batch export results

### 15. 🔌 Provider Configuration UI
**Status**: Models hardcoded in UI
**Needed**:
- Dynamic model list from provider
- Base URL configuration for local_vllm
- Custom model addition
- Provider health check

## Technical Debt

### 16. ⚙️ Testing
**Status**: No tests
**Needed**:
- Unit tests for providers (Python)
- Integration tests for IPC
- UI component tests (React)
- E2E tests (Playwright/Tauri)

### 17. 📚 Documentation
**Status**: Minimal
**Needed**:
- Architecture documentation
- API documentation
- User guide with screenshots
- Developer setup guide

### 18. 🏗️ Build & Distribution
**Status**: DMG bundling fails
**Issues**:
- Fix DMG creation script
- Code signing setup
- Auto-update mechanism
- Linux/Windows builds

### 19. 🔒 Security Improvements
**Status**: Basic security
**Needed**:
- Implement Tauri Stronghold for keys
- Rate limiting on API calls
- Input sanitization
- Secure session storage

### 20. ♿ Accessibility
**Status**: Not addressed
**Needed**:
- Keyboard navigation
- Screen reader support
- ARIA labels
- High contrast mode

## Priority Recommendations

### Phase 1 (Critical - Next Sprint)
1. API Key Management UI + Stronghold integration
2. Implement missing Tauri commands (sample, export, session)
3. Session Management UI
4. Distribution History sidebar

### Phase 2 (Important - Following Sprint)
5. Export UI
6. Token probabilities visualization
7. Settings/Preferences panel
8. Error handling improvements

### Phase 3 (Nice-to-Have - Future)
9. Prompt templates
10. Comparison view
11. Analytics dashboard
12. Batch processing

### Phase 4 (Polish - Before Release)
13. Testing suite
14. Documentation
15. Fix DMG bundling
16. Security hardening
17. Accessibility improvements
