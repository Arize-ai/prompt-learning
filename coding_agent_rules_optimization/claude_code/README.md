# Claude Code Optimization for SWE-bench

This directory contains tools for optimizing Claude Code CLI on SWE-bench using prompt learning.

## Main Script

**`optimize_claude_code.py`** - Automated optimization loop that:
- Runs Claude Code on train/test splits of SWE-bench
- Evaluates results using GPT-4
- Optimizes rulesets using prompt learning
- Logs experiments to Phoenix for tracking

## Other Files

- **`run_claude.py`** - Parallel execution of Claude Code on SWE-bench datasets
- **`claude_code_helpers.py`** - Core helper functions for running Claude Code
- **`test_claude_code.py`** - Test suite for validating the integration
- **`evals.py`** - Evaluation functions for assessing Claude Code outputs

## Setup

### 1. Install Claude Code CLI

```bash
# Download from: https://claude.ai/download
# Or install via package manager
```

### 2. Install Docker

Docker is required for SWE-bench evaluation harness:

```bash
# macOS
brew install --cask docker

# Linux
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Start Docker daemon
open -a Docker  # macOS
# OR
sudo systemctl start docker  # Linux
```

### 3. Install Python Dependencies

```bash
# Activate your environment
conda activate your-env  # or your preferred environment

# Install core dependencies
pip install swebench pandas phoenix-client arize-phoenix wrapt

# Install from requirements if available
pip install -r requirements.txt
```

### 4. Set Environment Variables

```bash
# Required: Anthropic API key for Claude Code
export ANTHROPIC_API_KEY="your-anthropic-key"

# Required: OpenAI API key for GPT-4 evaluation and optimization
export OPENAI_API_KEY="your-openai-key"

# Required: Phoenix for experiment tracking
export PHOENIX_HOSTNAME="https://your-phoenix-instance.com"
export PHOENIX_API_KEY="your-phoenix-key"
```

Add these to your `~/.zshrc` or `~/.bashrc` to persist them:

```bash
echo 'export ANTHROPIC_API_KEY="your-key"' >> ~/.zshrc
echo 'export OPENAI_API_KEY="your-key"' >> ~/.zshrc
echo 'export PHOENIX_HOSTNAME="https://your-phoenix-instance.com"' >> ~/.zshrc
echo 'export PHOENIX_API_KEY="your-key"' >> ~/.zshrc
source ~/.zshrc
```

### 5. Authenticate Claude Code

```bash
claude login
# OR use the ANTHROPIC_API_KEY set above
```

## Usage

### Running Optimization (Main Script)

The main script runs an automated optimization loop:

```bash
python optimize_claude_code.py
```

This will:
1. Load and split SWE-bench dataset
2. Run Claude Code on train/test sets
3. Evaluate results using GPT-4
4. Optimize rulesets using prompt learning
5. Repeat for multiple loops
6. Save all results and rulesets

### Configuration

Edit the constants at the top of `optimize_claude_code.py`:

```python
# Number of optimization loops
LOOPS = 5

# Dataset sizes (not used with load_split_swebench_repo)
TRAIN_SIZE = 150
TEST_SIZE = 150

# Number of parallel workers
WORKERS = 50
```

Edit the `main()` function to configure your run:

```python
def main():
    # Choose model
    model_name = "claude-sonnet-4-5-20250929"
    # OR
    model_name = "claude-haiku-4-5-20251001"
    
    # Phoenix dataset names
    train_name = "Claude Code: Django Train"
    test_name = "Claude Code: Django Test"
    
    # Load dataset - Option 1: Single repo with temporal split
    dataset_name, train_ids, test_ids, train_pd, test_pd = \
        load_split_swebench_repo(repo="django/django", train_percentage=0.6)
    
    # Load dataset - Option 2: Multi-repo split (prevents overfitting)
    # dataset_name, train_ids, test_ids, train_pd, test_pd = load_split_swebench()
    
    # Setup Phoenix tracking
    train_dataset_obj, test_dataset_obj = \
        setup_phoenix(train_pd, test_pd, train_name, test_name, model_name=model_name)
    
    # Run optimization loop
    run_optimization_loop(
        dataset_name=dataset_name,
        train_ids=train_ids,
        test_ids=test_ids,
        train_dataset_obj=train_dataset_obj,
        ruleset=" ",  # Start with empty ruleset
        repo="django",  # For file naming
        model_name=model_name
    )
```

### Output

The optimization produces:

1. **Results CSVs** in `claude_code_results/{model_name}/`:
   - `{repo}_train_results_{loop}.csv` - Raw train results
   - `{repo}_test_results_{loop}.csv` - Raw test results  
   - `{repo}_evaluated_train_results_{loop}.csv` - GPT-4 evaluated results

2. **Optimized Rulesets** in `act_rulesets/{model_name}/`:
   - `{repo}_ruleset_{loop}.txt` - Optimized ruleset for each loop

3. **Phoenix Experiments** - Logged to Phoenix for tracking and analysis

### Available Functions

**`load_split_swebench()`** - Split by repository
- Train repos: django, pytest, sphinx, astropy, requests, pylint
- Test repos: sympy, matplotlib, scikit-learn, xarray, seaborn, flask
- Prevents overfitting across different codebases

**`load_split_swebench_repo(repo, train_percentage=0.5)`** - Single repo temporal split
- Filters dataset by specific repo
- Splits chronologically by `created_at` date
- Earlier issues for training, later issues for testing
- Example: `load_split_swebench_repo("django/django", train_percentage=0.6)`

### Running Individual Components

**Test Claude Code integration:**
```bash
python test_claude_code.py --swebench
```

**Run Claude Code on specific instances:**
```bash
python run_claude.py \
  --run_id test_run \
  --instance_ids sympy__sympy-13177 django__django-11422 \
  --workers 2 \
  --wait_seconds 600
```

**With a custom ruleset:**
```bash
python run_claude.py \
  --run_id with_rules \
  --count 10 \
  --ruleset act_rulesets/claude-sonnet-4-5/ruleset_0.txt \
  --workers 4
```

## Docker Management

The optimization script includes automatic Docker cleanup between runs to prevent disk space issues:

```python
cleanup_docker()  # Called automatically
```

Manual cleanup if needed:
```bash
docker container prune -f
docker image prune -f
docker builder prune -f
```

## Monitoring Progress

- **Live logs**: Check terminal output for progress
- **Phoenix**: View experiments at your Phoenix URL
- **Results files**: Monitor `claude_code_results/` directory
- **Docker stats**: `docker stats` to check resource usage
- **Disk space**: `df -h` to ensure sufficient space

## Troubleshooting

**"Docker space issues"**
- Run `cleanup_docker()` or manual cleanup commands above
- Increase Docker disk allocation in Docker Desktop settings

**"Rate limits"**
- Reduce `WORKERS` constant (try 10-20 instead of 50)
- Increase `wait_seconds` parameter

**"Phoenix connection errors"**
- Verify `PHOENIX_HOSTNAME` and `PHOENIX_API_KEY` are set
- Check Phoenix instance is accessible

**"SWE-bench evaluation failures"**
- Ensure Docker is running
- Check Docker has sufficient memory (8GB+ recommended)
- Verify swebench package is installed: `pip install swebench`

**"Claude Code authentication"**
- Run `claude login` again
- Or ensure `ANTHROPIC_API_KEY` is set correctly

## Tips

- **First run**: Start with `LOOPS=1` and small dataset to test setup
- **Workers**: 50 works well for Claude Code; reduce if hitting rate limits
- **Timeout**: 600s (10 min) recommended for complex issues
- **Repo choice**: Django has ~23 instances in SWE-bench Lite
- **Phoenix**: Essential for tracking experiments across loops
- **GPT-4 costs**: Evaluation uses GPT-4, monitor OpenAI usage

