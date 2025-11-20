# Optimizer SDK

A prompt optimization toolkit that uses meta-prompting to iteratively improve LLM prompts based on evaluation feedback.

## Public API

### `PromptLearningOptimizer`

The main class for prompt optimization. Supports optimizing prompts in three formats: string, list of messages, or Phoenix `PromptVersion` objects.

**Key Methods:**

- `optimize()` - Optimizes a prompt using evaluation feedback and returns an improved version
- `run_evaluators()` - Runs Phoenix evaluators on a dataset and adds feedback columns
- `create_annotation()` - Generates human-like annotations from evaluation results

**Quick Example:**

```python
from optimizer_sdk import PromptLearningOptimizer

optimizer = PromptLearningOptimizer(
    prompt="You are a helpful assistant. {question}",
    model_choice="gpt-4o"
)

optimized_prompt = optimizer.optimize(
    dataset=df,  # DataFrame with inputs, outputs, and feedback
    output_column="answer",
    feedback_columns=["correctness", "clarity"]
)
```

## Internal Components

These files support the main optimizer but are not intended for direct use:

- **`meta_prompt.py`** - Constructs meta-prompts that guide the optimization process. Handles both general prompt optimization and coding agent ruleset optimization.

- **`annotator.py`** - Generates high-level annotations from evaluation data to provide additional context for optimization.

- **`tiktoken_splitter.py`** - Splits datasets into batches that fit within LLM context windows using accurate token counting.

- **`utils.py`** - Utility functions for API key management and validation.

- **`constants.py`** - Default meta-prompt templates, supported models, and configuration constants.

## How It Works

1. Takes your baseline prompt and evaluation dataset
2. Splits data into batches that fit in context window
3. Uses a meta-prompt to analyze failures and suggest improvements
4. Iteratively refines the prompt across batches
5. Returns optimized prompt in the same format as input

