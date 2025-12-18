# Prompt Learning: Using English Feedback to Optimize LLM Systems

This repository contains research on **Prompt Learning (PL)**, a novel approach to optimizing LLM prompts using natural language feedback instead of numerical scores.

## Research Overview

### Problem Statement
As more AI agents get deployed, a critical question emerges: can reinforcement learning control systems be built only in prompts? Traditional reinforcement learning relies on numerical scores and gradient updates, but prompts are the primary interface for guiding large language models. Can we apply RL-style methods to prompt refinement using natural language feedback?

### Key Contributions
- **English Error Terms**: Natural language feedback instead of numerical scores
- **Online Prompt Management**: Continuous improvement system designed for production
- **Single-Loop Success**: Powerful prompt improvements in just one optimization loop
- **Cost Efficiency**: low latency, achieving strong results in minutes rather than hours
- **SOTA Results**: Successful results on popular benchmarks like Big Bench Hard

## What Is Prompt Learning?

Prompt learning builds on meta prompting—a technique introduced by [Suzgun & Kalai (2024)](https://arxiv.org/abs/2401.12954) where LLMs automatically optimize prompts by breaking tasks into components. While traditional meta prompting relies on scalar feedback (e.g., pass/fail, reward scores), prompt learning enhances this loop using expressive textual feedback such as annotations, rule reminders, and explanations.

Instead of tuning model weights, prompt learning continuously improves agent behavior by refining the prompt itself—steering the system through feedback-driven edits that are low-cost, interpretable, and effective even post-deployment.

### How It Works

Prompt learning uses a three-model loop:
1. **Agent**: Executes the task using the current prompt
2. **Evaluator**: Identifies failures and generates textual feedback
3. **Optimizer**: Revises the prompt based on that feedback
This loop enables agents to **self-improve** through failure, learning in the same way humans do—by adjusting instructions rather than rewiring behavior.

### English Error Terms

Rather than numeric metrics, prompt learning relies on English critiques:

*“Missing ‘updatedAt’ field; section types must use the allowed vocabulary; top-level key should be ‘page’.”*

This feedback helps optimize prompts more precisely than a 2/5 rating ever could.

## Key Differences

| Aspect           | Prompt Learning                | Reinforcement Learning | Prompt Optimization          |
| ---------------- | ------------------------------ | ---------------------- | ---------------------------- |
| **Feedback**     | Annotation, Rule, Explanation  | Numeric rewards        | Correctness or scalar scores |
| **Optimization** | Feedback-driven meta prompting | Weight updates         | One-shot or search-based     |
| **Control**      | Targeted prompt edits          | Full model tuning      | Whole prompt updates         |
| **Deployment**   | Post-deployment & always-on    | Online or batch        | Typically offline            |




## Repository Structure

```
prompt-learning/
├── optimizer_sdk/              # Core prompt learning SDK
│   ├── meta_prompt.py              # Core meta-prompt implementation
│   ├── prompt_learning_optimizer.py # Prompt learning optimizer
│   ├── tiktoken_splitter.py        # Token counting utilities
│   ├── annotator.py                # Feedback annotation utilities
│   ├── constants.py                # Configuration constants
│   └── utils.py                    # Utility functions
│
├── big_bench_hard/             # Big Bench Hard benchmark experiments
│   ├── evaluator_prompts/          # Task-specific evaluator prompts (24 tasks)
│   │   ├── evaluator-bool.txt
│   │   ├── evaluator-lies.txt
│   │   ├── evaluator-sports.txt
│   │   └── ... (21+ more task evaluators)
│   └── run_files/                  # BBH experiment runners and datasets
│       ├── bbh-download/               # Downloaded BBH task data (27 JSON files)
│       ├── pl_multidataset.py          # Multi-dataset optimizer
│       ├── run_bbh_experiments.py      # Main BBH experiment runner
│       └── ...
│
├── cline/                      # Agent-based coding experiments (Cline/SWE-bench)
│   ├── act_mode/                   # Action-based agent experiments
│   │   ├── logs/                       # Evaluation logs and results
│   │   ├── ui_messages/                # Agent conversation traces
│   │   ├── evals_act.py                # Action mode evaluator
│   │   ├── run_act.py                  # Action mode runner
│   │   ├── optimize_cline_act_AX.ipynb # ArizeAI Phoenix optimization
│   │   └── optimize_cline_act_PX.ipynb # ArizeAI Phoenix experiments
│   ├── plan_mode/                  # Planning-based agent experiments
│   │   ├── evals_plan.py               # Planning mode evaluator
│   │   └── run_cline_plan.py           # Planning mode runner
│   ├── cline_helpers.py            # Shared utilities for Cline experiments
│   ├── container_helpers.py        # Docker container management
│   └── constants.py                # Configuration constants
│
├── prompts/                    # Experiment-specific prompt templates
│   ├── JSON_webpage_generation/    # Webpage JSON generation prompts
│   │   ├── evaluator-prompt-*.txt
│   │   └── rule-checker-prompt-*.txt
│   └── support_query_classification/ # Support query classification prompts
│       ├── evaluator_prompt.txt
│       └── annotations_prompt.txt
│
├── datasets/                   # Experiment datasets
│   ├── BizNorm-100.csv             # Business normalization dataset
│   ├── BizNorm-ruleset.md          # Ruleset for BizNorm task
│   └── support_queries.csv         # Support query examples
│
├── notebooks/                  # Jupyter notebooks for experiments
│   ├── BizNorm-100_evaluator_optimization.ipynb
│   ├── support_query_classification.ipynb
│   ├── arizeax_support_query_classification.ipynb
│   ├── phoenix_support_query_classification.ipynb
│   └── JSON_webpage_generation.ipynb
│
├── requirements.txt            # Python dependencies
├── LICENSE.txt                 # Apache 2.0 License
├── IP_NOTICE                   # Intellectual property notice
└── README.md                   # This file
```

## Quick Start

### Installation

Install the `prompt-learning` package via pip:

```bash
pip install prompt-learning
```

Or install from source for development:

```bash
git clone https://github.com/priyanjindal/prompt-learning.git
cd prompt-learning
pip install -e .
```

### Environment Setup

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

```python
import pandas as pd
from prompt_learning import PromptLearningOptimizer

# Create dataset with English feedback
dataset = pd.DataFrame({
    'query': [
        "I can't log in to my account anymore",
        "My password reset email never arrived",
        "I was charged twice for the same order",
    ],
    'output': [
        "Login Issues",
        "Password Reset",
        "Billing Inquiry",
    ],
    'feedback': [
        "correct",
        "correct",
        "correct",
    ]
})

# Define your prompt with template variables
prompt = """You are a customer support classifier.
Classify the query into a category.

Query: {query}

Category:"""

# Initialize optimizer
optimizer = PromptLearningOptimizer(
    prompt=prompt,
    model_choice="gpt-4o"
)

# Optimize the prompt using feedback
optimized_prompt = optimizer.optimize(
    dataset=dataset,
    output_column='output',
    feedback_columns=['feedback']
)

print(optimized_prompt)
```

### Advanced Usage

#### Using Custom Evaluators

You can run evaluators on your dataset before optimization:

```python
from prompt_learning import PromptLearningOptimizer

optimizer = PromptLearningOptimizer(
    prompt="Your prompt with {variables}",
    model_choice="gpt-4o"
)

# Run evaluators first
dataset, feedback_columns = optimizer.run_evaluators(
    dataset=dataset,
    evaluators=[your_custom_evaluator],
    feedback_columns=["existing_feedback"]
)

# Then optimize
optimized_prompt = optimizer.optimize(
    dataset=dataset,
    output_column='output',
    feedback_columns=feedback_columns
)
```

#### Using Annotations

Generate detailed annotations to guide optimization:

```python
annotations = optimizer.create_annotation(
    prompt=prompt,
    template_variables=["query"],
    dataset=dataset,
    feedback_columns=["feedback"],
    annotator_prompts=["Analyze why the model made errors and suggest improvements."],
    output_column="output"
)

optimized_prompt = optimizer.optimize(
    dataset=dataset,
    output_column='output',
    feedback_columns=['feedback'],
    annotations=annotations
)
```

#### Optimizing Rulesets

For coding agents or complex systems, optimize dynamic rulesets instead of the full prompt:

```python
optimized_ruleset = optimizer.optimize(
    dataset=dataset,
    output_column='output',
    feedback_columns=['feedback'],
    ruleset="- Rule 1: Always check for edge cases\n- Rule 2: Validate inputs"
)
```

### API Reference

#### `PromptLearningOptimizer`

**Constructor:**
```python
PromptLearningOptimizer(
    prompt: Union[PromptVersion, str, List[Dict[str, str]]],
    model_choice: str = "gpt-4",
    openai_api_key: Optional[str] = None,
    meta_prompt: Optional[str] = None,
    rules_meta_prompt: Optional[str] = None,
)
```

- `prompt`: The prompt to optimize. Can be a string, list of messages, or Phoenix PromptVersion.
- `model_choice`: OpenAI model to use (default: "gpt-4")
- `openai_api_key`: API key (or set via `OPENAI_API_KEY` env var)
- `meta_prompt`: Custom meta-prompt template (optional)
- `rules_meta_prompt`: Custom meta-prompt for ruleset optimization (optional)

**Methods:**

- `optimize(dataset, output_column, feedback_columns, ...)`: Optimize the prompt using feedback data
- `run_evaluators(dataset, evaluators, feedback_columns)`: Run evaluators on the dataset
- `create_annotation(...)`: Generate annotations for optimization guidance

## Contributing

You can contribute to the optimizer sdk itself within the optimizer_sdk notebook. You can also add notebooks, datasets, or other additional material. 

1. Create a new branch for your experiment
2. Submit a pull request

## License

See LICENSE.txt

## Contact

For questions about the research, contact: pjindal@arize.com


