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

Prompt learning builds on meta prompting—a technique introduced by [Suzgun & Kalai (2024)](https://arxiv.org/abs/2403.07491) where LLMs automatically optimize prompts by breaking tasks into components. While traditional meta prompting relies on scalar feedback (e.g., pass/fail, reward scores), prompt learning enhances this loop using expressive textual feedback such as annotations, rule reminders, and explanations.

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

## Experimental Design

### Task: Webpage JSON Generation

We task agents with generating structured JSON from user descriptions, then evaluate based on latent task rules (e.g., required fields, key vocab, style). These rules are not shown to the agent—only learned through failure and feedback.

#### Example latent rules:
Always return valid JSON—no trailing commas, unmatched braces, or comments.
Numeric values stay numeric—do not quote prices, ratings, or quantities.
Images need "src" and "alt"; omit "alt" only for decorative imagery.
Use HTTPS URLs for all external assets; flag non-secure links in a "warnings" array.
Every section object requires a "type" field drawn from a fixed vocabulary (header, text, image, productGrid, gallery, form, button, footer, embed).

Initial prompts violate all the rules, creating clear failure cases for optimization. 

### Evaluation Setup

[LLM-as-a-Judge](https://arize.com/llm-as-a-judge/) (GPT-4) is used to evaluate outputs and generate feedback. These are the 2 forms of feedback we feed into the Optimizer LLM's Meta Prompt so that it can generate an optimized prompt.
- **Explanation**: An explanation from the evaluator (i.e. human, or LLM-as-a-Judge) for why the agent output is correct or incorrect, focusing on the input query.
- **Rule**: A specific evaluation focused on compliance with the ruleset.

## Performance Results

### Table 1: Prompt Learning Performance

| Ruleset Size | Test Accuracy - Unoptimized Prompt | Test Accuracy - 1 loop Optimization| Test Accuracy - 5 loops Optimization | Latency |
|--------------|----------------|---------------|---------------|---------------|
| 10 | 0% | 84% | 100% | 1084.12s |
| 50 | 0% | 66% | 82% | 1150.45s |
| 100 | 0% | 42% | 67% | 1294.27s |

This is over a dataset of 100 webpage JSON queries. Accuracy is measured by number of query outputs (using the system prompt) following the entire ruleset. 

### Key Findings

1. **Single Loop Optimization**: Strong improvements in accuracy in just one loop of prompt optimization
2. **Strong results with 5 loops**: In just 5 loops, we see strong results in prompt learning
3. **Dramatic Improvement**: Prompt learning drastically outperforms un-optimized cases (near-zero baseline accuracy)
4. **Cost Efficiency**: Low latency overall. Big ruleset size increases do not have big impacts on latency.

## Repository Structure

```
prompt-learning/
├── optimizer_sdk/         # Core prompt learning SDK
│   ├── meta_prompt.py         # Core meta-prompt implementation
│   ├── prompt_learning_optimizer.py # Prompt learning optimizer
│   ├── tiktoken_splitter.py   # Token counting utilities
│   ├── constants.py           # Configuration constants
│   └── utils.py              # Utility functions
├── prompts/               # Prompt templates for different rule counts
│   ├── evaluator-prompt-10.txt
│   ├── evaluator-prompt-50.txt
│   ├── evaluator-prompt-100.txt
│   ├── rule-checker-prompt-10.txt
│   ├── rule-checker-prompt-50.txt
│   └── rule-checker-prompt-100.txt
├── notebooks/             # Jupyter notebooks for experiments      
│   └── prompt_learning_cookbook.ipynb
├── prompt_learning_run.py # Main experiment runner
├── requirements.txt       # Python dependencies
├── LICENSE.txt           # License file
└── README.md             # This file
```

## Quick Start

### Installation

```bash
pip install -r requirements.txt
```

### Environment Setup

```bash
export OPENAI_API_KEY="your-api-key-here"
```

### Basic Usage

```python
import pandas as pd
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer

# Create dataset with English feedback
dataset = pd.DataFrame({
    'input': ["Generate a tech company's career page"],
    'output': ["{incorrect JSON output}"],
    'feedback': ["The generated JSON breaks several rules: missing 'updatedAt' field, top-level key should be 'page'"]
})

# Initialize optimizer
optimizer = PromptLearningOptimizer(
    prompt="You are an expert in JSON webpage creation. Generate: {input}",
    model_choice="gpt-4"
)

# Optimize the prompt using English feedback
optimized_prompt = optimizer.optimize(
    dataset=dataset,
    output_column='output',
    feedback_columns=['feedback']
)
```

### Running Experiments

```python
# Single experiment
python prompt_learning_run.py

# Multi-rule experiments (10, 50, 100 rules)
# Edit RUN_MULTI_RULE_EXPERIMENTS = True in prompt_learning_run.py
```

## Contributing

You can contribute to the optimizer sdk itself within the optimizer_sdk notebook. You can also add notebooks, datasets, or other additional material. 

1. Create a new branch for your experiment
2. Submit a pull request

## License

See LICENSE.txt

## Contact

For questions about the research, contact: pjindal@arize.com


