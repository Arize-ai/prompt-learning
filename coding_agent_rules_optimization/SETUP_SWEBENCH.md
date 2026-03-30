# SWE-bench Setup

This folder contains harnesses for running coding agents (Cline, Claude Code) against SWE-bench instances inside Docker containers and recording outcomes.

## What it does
- Materializes each SWE-bench repo from a prebuilt image to a host workspace directory
- Starts a container with that workspace bind-mounted to `/testbed`
- Runs a coding agent on the problem statement
- Collects outputs (patches or plans) and evaluates them

---

## Prerequisites
- Python 3.10+ environment with:
  - `pip install swebench pandas datasets`
  - set `OPENAI_API_KEY` for optimizer_sdk and evaluation

---

## Clone, Install, Build SWE-Bench Dataset

### Install and verify
```bash
git clone https://github.com/princeton-nlp/SWE-bench.git
cd SWE-bench
pip install -e .
```

### Build all images for SWE-bench Lite (300 rows from test split)
- On Apple Silicon/M-series, keep `--namespace ''` to build locally for your arch.
- Adjust `--max_workers` to your resources.
```bash
python -m swebench.harness.prepare_images \
  --dataset_name SWE-bench/SWE-bench_Lite \
  --split test \
  --max_workers 4 \
  --namespace swebench-images \
  --tag latest \
  --env_image_tag latest
```

### Verify images
```bash
docker images | grep '^sweb.env'
docker images | grep '^sweb.eval'
```

Notes:
- Ensure Docker Desktop is running; allocate sufficient memory (12-16+ GB) and disk (~120 GB free).

---

## Configure paths

Edit `constants.py` and set:
- `CLINE_REPO_PATH = Path("/absolute/path/to/cline_repo")`
- `MATERIALIZED_REPOS_PATH = Path("/absolute/path/to/materialized_repos_root")`

---

## Important Note on Cost and Scale

**Warning**: Running coding agents on multiple rows of SWE-bench is very expensive, as each run utilizes multiple LLM API calls. It is strongly recommended to drastically reduce the number of rows in both the training and test sets to manage costs effectively.

---

## Shared Files

| File | Description |
|---|---|
| `constants.py` | Paths, prompts, and model configuration |
| `container_helpers.py` | Docker container lifecycle management |
| `evals.py` | LLM-as-judge evaluation (shared across agents) |
| `phoenix_experiments.py` | Phoenix experiment logging via REST API |

---

## Agent-Specific Instructions

- **Cline**: See [`cline/README.md`](cline/README.md)
- **Claude Code**: See [`claude_code/README.md`](claude_code/README.md)
