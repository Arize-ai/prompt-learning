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

| **Ruleset Size** | **Num Loops** | **Feedback Type**      | **Baseline Accuracy** | **Baseline Accuracy with Ruleset** | **Test Accuracy** | **Latency**
| ---------------- | ------------- | ---------------------- | --------------------- | ---------------------------------- | ----------------- | ------------ |
| 10               | 1             | Explanation            | 0%                    | 40.40%                             | 71%               | 
| 10               | 1             | Rule                   | 0%                    | 40.40%                             | 15.10%            |
| **10**           | **1**         | **Explanation + Rule** | **0%**                | **40.40%**                         | **84%**           |
| 10               | 5             | Explanation            | 0%                    | 40.40%                             | 100%              |
| 10               | 5             | Rule                   | 0%                    | 40.40%                             | 0%                |
| **10**           | **5**         | **Explanation + Rule** | **0%**                | **40.40%**                         | **100%**          | **1084.12s** |
| 50               | 1             | Explanation            | 0%                    | 14.70%                             | 64%               |
| 50               | 1             | Rule                   | 0%                    | 14.70%                             | 0%                |
| **50**           | **1**         | **Explanation + Rule** | **0%**                | **14.70%**                         | **66%**           |
| 50               | 5             | Explanation            | 0%                    | 14.70%                             | 69%               |
| 50               | 5             | Rule                   | 0%                    | 14.70%                             | 0%                |
| **50**           | **5**         | **Explanation + Rule** | **0%**                | **14.70%**                         | **82%**           | **1150.45s** |
| 100              | 1             | Explanation            | 0%                    | 5.80%                              | 0%                |
| 100              | 1             | Rule                   | 0%                    | 5.80%                              | 0%                |
| **100**          | **1**         | **Explanation + Rule** | **0%**                | **5.80%**                          | **0%**            |
| 100              | 5             | Explanation            | 0%                    | 5.80%                              | 38%               |
| 100              | 5             | Rule                   | 0%                    | 5.80%                              | 0%                |
| **100**          | **5**         | **Explanation + Rule** | **0%**                | **5.80%**                          | **67%**           | **1294.27s** |


This is over a dataset of 100 webpage JSON queries. Accuracy is measured by number of query outputs (using the system prompt) following the entire ruleset. 

### Key Findings

1. **Single Loop Optimization**: Strong improvements in accuracy in just one loop of prompt optimization
2. **Strong results with 5 loops**: In just 5 loops, we see strong results in prompt learning
3. **Dramatic Improvement**: Prompt learning drastically outperforms un-optimized cases (near-zero baseline accuracy)
4. **Cost Efficiency**: Low latency overall. Big ruleset size increases do not have big impacts on latency.
5. **Evals Thrive in Combination**: Explanation is clearly the most effective eval feedback on its own. But you can see that when using both explanation and rule evals, the test accuracy jumps up significantly. This shows that having good evals that you can trust, despite them being weak individually, can work well when they are provided to the optimizer LLM together. 


### Table 2: BIG-Bench Hard 

BIG-Bench Hard (BBH) is a diverse evaluation suite for language models. Here is how prompt learning performed.

| Task | Final GT | Init GT | GT Δ | Final LLM | Init LLM | LLM Δ | Type |
|------|----------|---------|------|-----------|----------|-------|------|
| boolean_expressions | 0.920 |   0.960  |   0.660   |  0.680  |    0.040  | 0.020  |  boolean |
| web_of_lies     |     0.540  |  0.640   |  0.200  |   0.640   |   0.100  | 0.440  |  general |
| word_sorting     |    0.840  |  0.880  |   0.760  |   0.780  |    0.040 |  0.020  |  sorting |
| sports_understanding | 0.860  |  0.960  |   0.900   |  0.960  |    0.100  | 0.060  |  general |
| object_counting   |   0.820  |  0.720   |  0.920   |  0.980     | -0.100 | 0.060 |   counting|
| disambiguation_qa | 0.580 | 0.740 | -0.160 | 0.800 | 0.640 | 0.160 | general |
| geometric_shapes | 0.560 | 0.500 | 0.060 | 0.560 | 0.560 | 0.000 | general |
| hyperbaton | 0.980 | 0.900 | 0.080 | 0.720 | 0.560 | 0.160 | general |
| logical_deduction_seven_objects | 0.760 | 0.780 | -0.020 | 0.880 | 0.920 | -0.040 | general |
| logical_deduction_three_objects | 0.960 | 0.960 | 0.000 | 1.000 | 1.000 | 0.000 | general |
| penguins_in_a_table | 0.700 | 0.700 | 0.000 | 0.000 | 0.820 | -0.820 | general |
| reasoning_about_colored_objects | 0.780 | 0.000 | 0.780 | 0.820 | 0.000 | 0.820 | general |
| salient_translation_error_detection | 0.760 | 0.660 | 0.100 | 0.660 | 0.680 | -0.020 | general |
| snarks | 0.540 | 0.420 | 0.120 | 0.820 | 0.000 | 0.820 | general |
| temporal_sequences | 1.000 | 0.980 | 0.020 | 0.940 | 0.940 | 0.000 | general |
| tracking_shuffled_objects_five_objects | 0.340 | 0.360 | -0.020 | 0.520 | 0.540 | -0.020 | general |
| tracking_shuffled_objects_seven_objects | 0.360 | 0.320 | 0.040 | 0.240 | 0.520 | -0.280 | general |
| **AVERAGE / Δ SUM** | **0.693** | **0.610** | **1.000** | **0.663** | **0.598** | **0.780** | general |


## Repository Structure

```
prompt-learning/
├── optimizer_sdk/         # Core prompt learning SDK
│   ├── meta_prompt.py         # Core meta-prompt implementation
│   ├── prompt_learning_optimizer.py # Prompt learning optimizer
│   ├── tiktoken_splitter.py   # Token counting utilities
│   ├── constants.py           # Configuration constants
│   └── utils.py              # Utility functions
├── big_bench_hard/
│   ├── evaluator_prompts/         # Evaluator prompt templates for BBH tasks
│   │   ├── evaluator-bool.txt
│   │   ├── evaluator-lies.txt
│   │   ├── evaluator-object.txt
│   │   ├── evaluator-sports.txt
│   │   └── evaluator-wordsort.txt
│   └── run_files/                # Scripts and experiment runners for BBH
│       ├── pl_multidataset.py
│       ├── run_bbh_experiments.py
│       └── ...
├── prompts/                      # Prompt templates for main (non-BBH) experiments
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


