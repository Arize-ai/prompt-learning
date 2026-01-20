# Prompt Learning: Optimize LLM Prompts with Natural Language Feedback

A production-ready SDK and CLI for optimizing LLM prompts using natural language feedback instead of numerical scores. Supports OpenAI and Google AI providers with built-in cost management.

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

> *"Missing 'updatedAt' field; section types must use the allowed vocabulary; top-level key should be 'page'."*

This feedback helps optimize prompts more precisely than a 2/5 rating ever could.

### Key Contributions

- **English Error Terms**: Natural language feedback instead of numerical scores
- **Online Prompt Management**: Continuous improvement system designed for production
- **Single-Loop Success**: Powerful prompt improvements in just one optimization loop
- **Cost Efficiency**: Low latency, achieving strong results in minutes rather than hours
- **SOTA Results**: Successful results on popular benchmarks like Big Bench Hard

## Installation

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

## Environment Setup

Set your API keys based on which provider you want to use:

```bash
# For OpenAI (default provider)
export OPENAI_API_KEY="your-openai-key"

# For Google AI / Gemini
export GOOGLE_API_KEY="your-google-key"
# or
export GEMINI_API_KEY="your-google-key"
```

## Providers

Prompt Learning supports two AI providers:

### OpenAI (Default)

The default provider uses OpenAI's GPT models with accurate tiktoken-based token counting.

| Model | Best For |
|-------|----------|
| `gpt-4` | Highest quality optimization |
| `gpt-4-turbo` | Balance of quality and cost |
| `gpt-3.5-turbo` | Fast, cost-effective optimization |

### Google AI

Google's Gemini models offer competitive performance at lower costs, with additional features like search grounding.

| Model | Best For |
|-------|----------|
| `gemini-2.5-flash` | Fast, cost-effective optimization |
| `gemini-2.5-pro` | Higher quality responses |
| `gemini-2.5-flash-image` | Image generation |

**Google-specific features:**
- Google Search grounding for fact-based responses
- Image generation via "nano banana" models

## CLI Reference

### Global Options

```bash
prompt-learn [OPTIONS] COMMAND [ARGS]
```

| Option | Description |
|--------|-------------|
| `--verbose`, `-v` | Enable detailed output with progress information |
| `--version` | Show version and exit |
| `--help` | Show help message |

### `prompt-learn optimize`

The core command for optimizing prompts using natural language feedback.

```bash
prompt-learn optimize [OPTIONS]
```

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--prompt` | `-p` | **Yes** | - | The baseline prompt to optimize |
| `--dataset` | `-d` | **Yes** | - | Path to CSV or JSON dataset |
| `--feedback-columns` | `-f` | **Yes** | - | Column name(s) containing feedback (comma-separated, or use -f multiple times) |
| `--output-column` | `-o` | **Yes** | `output` | Column name containing LLM outputs |
| `--model` | `-m` | No | `gpt-4` | Model to use for optimization |
| `--provider` | - | No | `openai` | Provider: `openai` or `google` |
| `--context-size` | `-c` | No | `128000` | Context window size in tokens |
| `--budget` | `-b` | No | `5.00` | Maximum budget in USD |
| `--save` | `-s` | No | - | Path to save optimized prompt |

**Examples:**

```bash
# Basic optimization with OpenAI
prompt-learn optimize \
  --prompt "Summarize this text clearly: {text}" \
  --dataset examples.csv \
  --output-column response \
  --feedback-columns feedback

# Multiple feedback columns (comma-separated)
prompt-learn optimize \
  --prompt "Generate JSON for: {input}" \
  --dataset data.csv \
  --output-column generated_json \
  --feedback-columns quality_notes,error_messages,style_feedback

# Multiple feedback columns (alternative: use -f multiple times)
prompt-learn optimize \
  --prompt "Generate JSON for: {input}" \
  --dataset data.csv \
  --output-column generated_json \
  -f quality_notes -f error_messages

# Use Google AI with custom budget
prompt-learn optimize \
  --prompt "Your prompt here" \
  --dataset data.csv \
  --output-column output \
  --feedback-columns feedback \
  --provider google \
  --model gemini-2.5-flash \
  --budget 10.00

# Save optimized prompt to file
prompt-learn optimize \
  --prompt "Original prompt" \
  --dataset data.csv \
  --output-column result \
  --feedback-columns feedback \
  --save optimized_prompt.txt

# Verbose mode for cost tracking
prompt-learn --verbose optimize \
  --prompt "Your prompt" \
  --dataset data.csv \
  --output-column output \
  --feedback-columns feedback
```

### `prompt-learn image`

Test and iterate on image generation prompts using Google's image models.

```bash
prompt-learn image [OPTIONS]
```

| Option | Short | Required | Default | Description |
|--------|-------|----------|---------|-------------|
| `--prompt` | `-p` | **Yes** | - | Image generation prompt |
| `--iterations` | `-i` | No | `5` | Number of images to generate |
| `--output-dir` | `-o` | No | `./image_outputs` | Directory to save images |
| `--evaluate` | `-e` | No | `false` | Enable human-in-the-loop feedback |
| `--budget` | `-b` | No | `2.00` | Maximum budget in USD |

**Examples:**

```bash
# Generate 5 images
prompt-learn image --prompt "A futuristic cityscape at sunset"

# Generate more images with evaluation
prompt-learn image \
  --prompt "Abstract art with vibrant colors" \
  --iterations 10 \
  --evaluate \
  --budget 5.00

# Save to custom directory
prompt-learn image \
  --prompt "A serene mountain landscape" \
  --output-dir ./my_images
```

## How Feedback Columns Work

Feedback columns are the core mechanism that drives prompt optimization. They contain **natural language descriptions** of what went wrong or could be improved in each output.

### Dataset Structure

Your dataset must include:
1. **Input columns**: Variables used in your prompt template (e.g., `{text}`, `{input}`)
2. **Output column**: The LLM's response for each input
3. **Feedback column(s)**: Natural language critique of each output

**Example CSV:**

```csv
input,output,feedback
"Generate a tech company career page","{ ""sections"": [...] }","Missing 'updatedAt' field; top-level key should be 'page' not 'sections'"
"Generate a restaurant menu page","{ ""menu"": [...] }","Good structure but missing required 'metadata' section; date format should be ISO 8601"
"Generate a product landing page","{ ""hero"": [...] }","Correct format; consider adding 'testimonials' section for completeness"
```

### Why Feedback Columns Are Required

The optimizer needs feedback to understand:
- What patterns lead to failures
- What rules or guidelines are being violated
- How outputs should be improved

Without feedback, the optimizer has no signal to improve the prompt.

### Multiple Feedback Columns

You can provide multiple types of feedback using comma-separated values:

```bash
prompt-learn optimize \
  --prompt "Your prompt" \
  --dataset data.csv \
  --output-column output \
  --feedback-columns structural_errors,style_feedback,rule_violations
```

Or by specifying `-f` multiple times:

```bash
prompt-learn optimize \
  --prompt "Your prompt" \
  --dataset data.csv \
  --output-column output \
  -f structural_errors -f style_feedback -f rule_violations
```

All feedback columns are combined to provide richer context for optimization.

## Built-in Evaluators

### SDK Evaluators

The SDK supports running evaluators programmatically to generate feedback columns:

```python
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer

optimizer = PromptLearningOptimizer(
    prompt="Your prompt: {input}",
    model_choice="gpt-4"
)

# Run evaluators to generate feedback
dataset, feedback_columns = optimizer.run_evaluators(
    dataset=your_dataframe,
    evaluators=[your_evaluator_function],
    feedback_columns=[]  # New columns will be added
)
```

### Image Evaluator

For image generation workflows, use the `ImagePromptEvaluator`:

```python
from evaluators.image_evaluator import ImagePromptEvaluator

evaluator = ImagePromptEvaluator()

# Evaluate generated images
results = evaluator.evaluate_images(
    images_dir="./generated_images",
    original_prompt="A serene mountain landscape"
)

print(f"Quality Score: {results['quality_score']}")
print(f"Adherence Score: {results['adherence_score']}")
print(f"Improvements: {results['improvements']}")
```

The image evaluator uses Gemini vision to assess:
- **Prompt adherence**: How well the image matches the prompt
- **Visual quality**: Composition, lighting, detail
- **Artistic appeal**: Aesthetic value, creativity
- **Consistency**: Similarity across multiple generations

## Token Estimation and Cost Management

### Token Counting

Prompt Learning uses intelligent token counting based on your provider:

| Provider | Counter | Method |
|----------|---------|--------|
| OpenAI | `TiktokenCounter` | Accurate encoding-based counting |
| Google | `ApproximateCounter` | Fast estimation (~characters/4) |

### Budget Enforcement

Set a maximum budget to prevent unexpected costs:

```bash
# Default $5 budget
prompt-learn optimize -p "..." -d data.csv -f feedback

# Custom $15 budget for large datasets
prompt-learn optimize -p "..." -d large_data.csv -f feedback --budget 15.00
```

The optimizer will automatically stop before exceeding your budget limit.

### Cost Tracking

Use verbose mode to see real-time cost information:

```bash
prompt-learn --verbose optimize -p "..." -d data.csv -f feedback
```

Output includes:
- Per-batch cost estimates
- Running total cost
- Budget remaining

### Pricing Reference

Built-in pricing for supported models (per 1,000 tokens):

| Model | Input Cost | Output Cost |
|-------|------------|-------------|
| gpt-4 | $0.030 | $0.060 |
| gpt-4-turbo | $0.010 | $0.030 |
| gpt-3.5-turbo | $0.0015 | $0.002 |
| gemini-2.5-flash | $0.0003 | $0.0025 |
| gemini-2.5-pro | $0.00125 | $0.010 |

## SDK Usage

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

Contributions are welcome! Please open an issue or submit a pull request.

## Architecture

```
prompt-learning/
├── cli/                       # Command-line interface
│   ├── main.py               # CLI entry point
│   └── commands/             # Command implementations
│       ├── optimize.py       # Main optimization command
│       └── image.py          # Image generation command
├── core/                     # Core business logic
│   ├── pricing.py            # Cost tracking & budget enforcement
│   ├── dataset_splitter.py   # Token-aware batch splitting
│   └── exceptions.py         # Custom error handling
├── interfaces/               # Abstract interfaces
│   └── token_counter.py      # Token counting abstraction
├── providers/                # AI provider implementations
│   ├── base_provider.py      # Provider interface
│   └── google_provider.py    # Google AI integration
├── optimizer_sdk/            # Core prompt learning SDK
│   ├── prompt_learning_optimizer.py  # Main optimizer
│   ├── meta_prompt.py        # Meta-prompt templates
│   └── annotator.py          # Feedback annotation
├── evaluators/               # Built-in evaluators
│   └── image_evaluator.py    # Image quality assessment
└── tests/                    # Test suite
```

## Development

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format code
black .
```

## License

This project is licensed under the Elastic License 2.0 (ELv2). See [LICENSE.txt](LICENSE.txt) for details.

## Contact

For questions about the research or SDK, contact: pjindal@arize.com

---

**Authors**: Arize AI, Nouamane Benbrahim, Priyan Jindal
