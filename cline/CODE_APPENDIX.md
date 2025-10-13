# Code Appendix

This document provides an overview of key functions in the Cline codebase to help navigate the implementation. For full details, refer to the source files.

## Core Functions

### `run_act()`
**Location:** `act_mode/run_act.py`

**Purpose:** Orchestrates Cline Act Mode evaluation on SWE-bench datasets.

**Key Responsibilities:**
- Loads SWE-bench dataset and filters instances based on configuration
- Manages parallel execution of Cline across multiple instances using ThreadPoolExecutor
- Collects predictions and invokes the SWE-bench evaluation harness
- Compiles results including instance metadata, patches, and pass/fail outcomes
- Returns a DataFrame with evaluation results for downstream analysis

**Parameters:**
- `run_id`: Unique identifier for the evaluation run (stored in logs directory)
- `dataset_name`: SWE-bench dataset to evaluate against (default: SWE-bench_Lite)
- `instance_ids`: Optional list of specific instances to run
- `ruleset`: Custom rules/instructions to append to Cline's system prompt
- `workers`: Parallelization level (default: 16)
- `count`: Number of random instances to run (if not using instance_ids)

---

### `act_one()`
**Location:** `act_mode/run_act.py`

**Purpose:** Processes a single SWE-bench instance with Cline in Act Mode.

**Key Responsibilities:**
- Allocates unique port numbers for the Cline server to avoid conflicts in parallel execution
- Retrieves Docker image tag for the instance's test environment
- Calls `run_cline_for_instance()` to execute Cline on the problem
- Returns the instance ID and path to the generated patch file

**Parameters:**
- `instance`: Dictionary containing SWE-bench instance data (problem statement, metadata, etc.)
- `idx`: Index used for port allocation to prevent collisions
- `ruleset`: Custom rules text to inject into Cline

---

### `run_cline_for_instance()`
**Location:** `cline_helpers.py`

**Purpose:** Low-level function to execute Cline on a single instance with full environment setup.

**Key Responsibilities:**
1. **Environment Setup:** Materializes repository from Docker image to host workspace
2. **Container Management:** Starts Docker container with bind-mounted workspace
3. **Server Initialization:** Starts Cline server on host, pointing to workspace
4. **Configuration:** Enables auto-approve mode, sets model, applies rulesets
5. **Task Execution:** Submits problem statement to Cline and waits for completion
6. **Result Collection:** Returns either final plan (Plan Mode) or predictions path (Act Mode)

**Parameters:**
- `instance_id`: SWE-bench instance identifier
- `image_tag`: Docker image containing the test environment
- `cline_repo`: Path to Cline repository on host
- `workspaces_root`: Root directory for instance workspaces
- `task_text`: Problem statement to submit to Cline
- `host`, `proto_port`, `hostbridge_port`: Network configuration for Cline server
- `mode`: Either "act" or "plan" mode
- `wait_seconds`: Timeout for Cline to complete (default: 600s)
- `ruleset_text`: Optional custom rules to inject

---

### `evaluate_results()`
**Location:** `act_mode/evals_act.py`

**Purpose:** Generates qualitative evaluations of Cline's outputs using LLM-as-judge.

**Key Responsibilities:**
- Filters out excessively large patches (>200k chars) to avoid API limits
- Constructs evaluation prompt with problem statement, ground truth, test patch, Cline's patch, and pass/fail status
- Uses Phoenix `llm_generate()` with GPT-4o to assess correctness and reasoning
- Parses JSON responses to extract correctness and explanation
- Augments results DataFrame with `correctness` and `explanation` columns

**Parameters:**
- `results`: DataFrame containing instance data, patches, and test outcomes

**Returns:**
- Augmented DataFrame with qualitative evaluation results

---

### `optimize()`
**Location:** `optimizer_sdk/prompt_learning_optimizer.py` (PromptLearningOptimizer class)

**Purpose:** Implements the Prompt Learning algorithm to iteratively improve prompts based on feedback.

**Key Responsibilities:**
1. **Data Processing:** Loads dataset and validates required columns
2. **Evaluation:** Runs user-provided evaluators to generate feedback
3. **Template Detection:** Auto-detects template variables in the prompt
4. **Batching:** Splits large datasets into token-budget-aware batches
5. **Meta-Prompting:** For each batch, constructs a meta-prompt that includes:
   - Current prompt to optimize
   - Dataset examples with outputs and feedback
   - Annotations and contextual information
6. **Optimization:** Calls LLM to generate improved prompt version
7. **Iteration:** Returns optimized prompt for next training loop

**Parameters:**
- `dataset`: DataFrame or path to JSON with requests, responses, and feedback
- `output_column`: Name of column containing LLM outputs to evaluate
- `evaluators`: List of Phoenix evaluator functions to run
- `feedback_columns`: Existing feedback columns (if not using new evaluators)
- `annotations`: Additional human annotations or context
- `ruleset`: Optional ruleset context for optimization
- `context_size_k`: LLM context window size in tokens (default: 128k)

**Returns:**
- Optimized prompt (PromptVersion object or string)

---

## Workflow Overview

**Typical Evaluation Pipeline:**
1. Call `run_act()` to evaluate Cline on SWE-bench instances
2. For each instance, `run_act()` spawns parallel `act_one()` calls
3. Each `act_one()` calls `run_cline_for_instance()` to execute Cline
4. Results are collected and SWE-bench evaluator runs tests
5. Call `evaluate_results()` to add qualitative LLM-based assessments

**Optimization Loop:**
1. Run evaluation to generate dataset with feedback
2. Call `optimize()` from PromptLearningOptimizer to improve ruleset/prompt
3. Use optimized prompt in next evaluation round
4. Repeat for configured number of loops (typically 3-5)

---

## File Organization

- `cline_helpers.py` - Low-level utilities for Cline execution and Docker management
- `act_mode/run_act.py` - High-level Act Mode evaluation orchestration
- `act_mode/evals_act.py` - LLM-based qualitative evaluation
- `plan_mode/` - Similar structure for Plan Mode (not detailed here)
- `optimizer_sdk/prompt_learning_optimizer.py` - Core Prompt Learning algorithm
- `act_mode/optimize_cline_act_*.ipynb` - End-to-end optimization notebooks

---

## Additional Resources

- See `README.md` for setup instructions and environment configuration
- See notebooks in `act_mode/` for complete usage examples
- Logs stored in `act_mode/logs/run_evaluation/<run_id>/` for debugging

