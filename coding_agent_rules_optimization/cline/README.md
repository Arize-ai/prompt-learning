# Cline SWE-bench Harness

This folder contains the harness for running Cline (in Plan/Act modes) against SWE-bench instances.

## Prerequisites

In addition to the [shared setup](../SETUP_SWEBENCH.md):

- Node.js
- npx + tsx available (`npx tsx`)
- grpcurl on PATH (macOS: `brew install grpcurl`)
- ripgrep on PATH (macOS: `brew install ripgrep`) and symlinked for Cline core:
  - From the Cline repo root: `ln -sf "$(command -v rg)" dist-standalone/rg`

---

## Clone + Build Cline

```bash
git clone https://github.com/cline/cline.git
```

From the Cline repo root:

```bash
npm ci
npm run compile-standalone
```

This produces `dist-standalone/cline-core.js` and `dist-standalone/proto/descriptor_set.pb`.

---

## Running the harness

### Act Mode

From `cline/act_mode/`:

```bash
python main.py
```

- Runs Cline in Act mode on SWE-bench instances (parallel execution)
- Generates actual code patches and validates them with SWE-bench tests
- Results saved to `act_mode/act_results/`
- Rulesets saved to `act_mode/act_rulesets/`

### Plan Mode

From `cline/plan_mode/`:

```bash
python main.py
```

- Runs Cline in Plan mode (generates plans without editing code)
- Uses LLM-as-judge evaluation
- Results saved to `plan_mode/results/`
- Rulesets saved to `plan_mode/rulesets/`

---

## Optimization Notebooks

- **Act Mode (Arize)**: `act_mode/optimize_cline_act_AX.ipynb`
- **Act Mode (Phoenix)**: `act_mode/optimize_cline_act_PX.ipynb`
- **Plan Mode**: `plan_mode/optimize_cline_plan.ipynb`

---

## Key Files

| File | Description |
|---|---|
| `cline_helpers.py` | Low-level utilities for Cline server lifecycle, gRPC, task submission, and mode toggling |
| `act_mode/run_act.py` | Act mode orchestration: parallel Cline runs + SWE-bench evaluation |
| `act_mode/main.py` | Act mode optimization loop |
| `plan_mode/run_cline_plan.py` | Plan mode single-instance runner |
| `plan_mode/main.py` | Plan mode optimization loop |
| `plan_mode/evals_plan.py` | Plan-specific LLM evaluation |

---

## What the helpers expect

Key functions live in `cline_helpers.py` and `../container_helpers.py`:
- Materialize `/testbed` from the image to a host workspace (first run only)
- Start bound container (code changes persist via bind mount)
- Launch Cline server with `npx tsx scripts/test-standalone-core-api-server.ts`
- Enable auto-approve and set model config
- Toggle Plan/Act mode, submit task, poll for outputs

Optional: set `CLINE_DIR_BASE` before running to control where the Cline server writes task state.

---

## Notes

- Concurrency is configured inside `main.py` (`max_workers` / `WORKERS`). Adjust to suit your machine.
- Per-instance UI transcripts are saved under `ui_messages/`
