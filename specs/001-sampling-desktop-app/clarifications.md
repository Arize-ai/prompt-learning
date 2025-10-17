# Clarification Session: Verbalized Sampling Desktop App

**Date**: 2025-10-16
**Feature Branch**: `001-sampling-desktop-app`
**Session Type**: Pre-Implementation Clarification

## Questions Addressed

### Q1: Token-Level Probability Detail

**Question**: Should the results table include token-level probabilities or only summary p-values?

**Decision**: **Option C** - Summary p-values by default, with optional "Show Token Details" toggle

**Rationale**: Balances simplicity and power. Default view is clean for quick exploration, advanced users can drill down when needed. Adds UI toggle complexity but preserves both casual and research use cases.

**Specification Updates**:
- Updated **FR-005**: Added "Show Token Details" toggle requirement
- Added **User Story 1, Scenario 6**: Acceptance criteria for token details expansion
- Updated **Completion entity**: Added optional token-level probabilities field
- Added **SC-013**: Performance criterion for token details rendering

---

### Q2: Export Metadata Inclusion

**Question**: Should export formats (JSONL/CSV) include trace metadata like model name, API latency, and token count?

**Decision**: **Option A** - Include comprehensive trace metadata

**Rationale**: Enables full reproducibility and performance analysis. Export files are ~2x larger but self-documenting. Critical for research workflows requiring audit trails and debugging.

**Specification Updates**:
- Updated **FR-006**: Added comprehensive metadata fields (model, latency, token_count, all parameters, API version/endpoint)
- Updated **User Story 4, Scenario 1**: Expanded export field list in CSV example
- Updated **Export Record entity**: Documented trace metadata inclusion

---

### Q3: Maximum k Value Limit

**Question**: What is the expected maximum limit for k (number of samples to generate)?

**Decision**: **Option B** - Model-dependent limits (100 for API, 500 for local vLLM)

**Rationale**: Leverages local compute power for advanced analysis while respecting API rate limits. Local users get flexibility for research, API users stay within provider constraints.

**Specification Updates**:
- Updated **FR-002**: Changed from "k (1-100)" to "k (model-dependent: 1-100 for API providers, 1-500 for local vLLM)"
- Updated **Edge Case**: Modified k validation to specify provider-type-specific limits
- No changes needed to success criteria (SC-001 already uses k=10 as typical example)

---

### Q4: UI Refresh Behavior

**Question**: Should the UI auto-refresh results on new model runs or stay static until manual refresh?

**Decision**: **Option C** - Auto-refresh with "Pin Current View" toggle

**Rationale**: Best of both worlds - auto-update by default for rapid experimentation, users can pin current distribution to prevent changes during comparison work. Maximizes flexibility for different workflows.

**Specification Updates**:
- Added **FR-019**: Auto-refresh requirement with "Pin Current View" toggle functionality
- Updated **User Story 1, Scenario 4**: Clarified auto-refresh behavior on parameter change
- Added **User Story 1, Scenario 7**: Acceptance criteria for pin toggle behavior
- Added **SC-014**: Success criterion for pin toggle reliability (100% prevention when active)

---

## Summary of Changes

### Requirements Added/Modified
- **FR-002**: Model-dependent k limits (API: 100, local: 500)
- **FR-005**: Token details toggle added
- **FR-006**: Comprehensive export metadata specified
- **FR-019**: Auto-refresh + pin toggle (NEW requirement)

### User Stories Enhanced
- **User Story 1**: Added 2 new acceptance scenarios (token details, pin view)
- **User Story 4**: Updated export field examples with trace metadata

### Entities Updated
- **Completion**: Added optional token-level probabilities
- **Export Record**: Specified comprehensive trace metadata

### Success Criteria Added
- **SC-013**: Token details rendering performance
- **SC-014**: Pin toggle reliability

### Edge Cases Modified
- Updated k limit validation to reflect provider-specific constraints

## Impact Assessment

**Scope Impact**: Minor additions, no reduction in planned features
- Token details is optional UI enhancement (toggle)
- Export metadata increases file size ~2x but critical for reproducibility
- Model-dependent k limits expand local capability without changing API behavior
- Pin toggle is small UX refinement for power users

**Implementation Complexity**: Low to moderate
- Token details: Expandable table rows (standard UI pattern)
- Export metadata: Additional fields in serialization (straightforward)
- k validation: Provider-type check before submission (simple)
- Pin toggle: State management + auto-refresh disable (low complexity)

**Risk**: Minimal
- All additions are well-scoped and testable
- No architectural changes required
- Compatible with existing JSON contract design
- No security or performance concerns introduced

## Readiness for Planning

✅ **All clarifications resolved**
✅ **No ambiguous requirements remaining**
✅ **Specification updated and validated**
✅ **Ready to proceed to `/speckit.plan` phase**

## Next Steps

1. Run `/speckit.plan` to create implementation plan
2. Design JSON schemas for token-level data in IPC contracts
3. Plan UI component structure (table with expand/collapse, pin toggle button)
4. Define export file format examples with metadata fields
5. Establish k validation logic for provider detection
