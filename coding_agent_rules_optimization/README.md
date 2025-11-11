## Cline SWE-bench Harness (Getting Started)

This folder contains a lightweight harness to run Cline (in PLAN/ACT modes) against SWE-bench instances inside Docker containers and record outcomes.

### What it does
- Materializes each SWE-bench repo from a prebuilt image to a host workspace directory
- Starts a container with that workspace bind-mounted to `/testbed`
- Starts the Cline standalone gRPC server pointing at that workspace
- Submits the instance's problem statement to Cline and collects outputs

---

### Prerequisites
- Node.js 
- npx + tsx available (`npx tsx`)
- grpcurl on PATH (macOS: `brew install grpcurl`)
- ripgrep on PATH (macOS: `brew install ripgrep`) and symlinked for Cline core:
  - From the Cline repo root: `ln -sf "$(command -v rg)" dist-standalone/rg`
- Python 3.10+ environment with:
  - `pip install swebench pandas datasets`
  - set `OPENAI_API_KEY` for optimizer_sdk and Cline

---

### Important Note on Cost and Scale

**Warning**: Running Cline on multiple rows of SWE-bench is very expensive, as each Cline call utilizes multiple LLM API calls. It is strongly recommended to drastically reduce the number of rows in both the training and test sets from 150 to a much smaller number to manage costs effectively.

---

### Clone + Build Cline

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

### Clone, Install, Build SWE-Bench Dataset

#### Install and verify
```bash
git clone https://github.com/princeton-nlp/SWE-bench.git
cd SWE-bench
pip install -e .
```

#### Build all images for SWE-bench Lite (300 rows from test split)
- On Apple Silicon/M-series, keep `--namespace ''` to build locally for your arch.
- Adjust `--max_workers` to your resources.
```bash
python -m swebench.harness.prepare_images \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --split test \
  --max_workers 4 \
  --namespace '' \
  --tag latest
```

#### Verify images
```bash
docker images | grep '^sweb.env'
docker images | grep '^sweb.eval'
```

Notes:
- Ensure Docker Desktop is running; allocate sufficient memory (12–16+ GB) and disk (~120 GB free).

### Configure paths in the harness
Edit `constants.py` and set:
- `CLINE_REPO_PATH = Path("/absolute/path/to/cline_repo")`
- `workspaces_root = Path("/absolute/path/to/materialized_repos_root")`

Optional (for predictable state/log paths): set `CLINE_DIR_BASE` before running to control where the Cline server writes task state.

---

### Running the harness
From `cline` folder

```bash
python main.py
```

Notes:
- The script samples SWE-bench Lite, runs jobs in parallel, and writes:
  - Per-instance UI transcripts under `ui_messages/`
  - A JSONL of results (plans/completions) next to the script
  - CSV artifacts under `results/`
- Concurrency is configured inside `main.py` (`max_workers`). Adjust to suit your machine.

---

### What the helpers expect
Key functions live in `cline_helpers.py` and `container_helpers.py`:
- Materialize `/testbed` from the image to a host workspace (first run only)
- Start bound container (code changes persist via bind mount)
- Launch Cline server with `npx tsx scripts/test-standalone-core-api-server.ts`
- Enable auto-approve and set model config
- Toggle PLAN mode, submit task, poll for outputs

---



