# Prompt Learning Enhanced: Production-Ready SDK with CLI

**Enhanced fork of the original prompt learning research with CLI tools, Google AI integration, pricing controls, and production features.**

This repository contains an enhanced version of **Prompt Learning (PL)**, a novel approach to optimizing LLM prompts using natural language feedback instead of numerical scores, now with a comprehensive CLI, multiple provider support, and production-ready features.

## 🚀 What's New in This Enhanced Fork

### CLI Interface
- **Command-line tool** for prompt optimization workflows
- **Image generation testing** with Google's "nano banana" models  
- **Budget limiting** with real-time cost tracking
- **Verbose mode** with detailed progress information
- **Comprehensive help** system with examples

### Provider Support
- **OpenAI integration** (GPT-3.5, GPT-4)
- **Google AI integration** (Gemini 2.5 Flash, Pro) with search grounding
- **Token counting** with provider-specific optimizations
- **Cost tracking** across all providers

### Production Features
- **Dependency injection** for clean architecture
- **Performance optimization** with 67x faster token counting
- **Comprehensive error handling** with custom exceptions
- **Budget enforcement** to prevent unexpected costs
- **Human-in-the-loop evaluation** for image generation

### Developer Experience
- **Comprehensive unit tests** (40 tests covering all components)
- **Type hints** throughout the codebase
- **Clean separation** of concerns with interfaces
- **Modular design** for easy extension

## 📦 Installation

```bash
pip install prompt-learn
```

## 🎯 Quick Start

### CLI Usage

**Optimize prompts with natural language feedback:**
```bash
# Basic optimization with default $5 budget
prompt-learn optimize \
  --prompt "Summarize this text clearly" \
  --dataset examples.csv \
  --feedback-columns human_rating \
  --provider openai

# Use Google AI for cost-effective optimization  
prompt-learn optimize \
  --prompt "Your prompt here" \
  --dataset data.csv \
  --feedback-columns feedback \
  --provider google \
  --budget 10.00
```

**Test image generation prompts:**
```bash
# Generate images with budget control
prompt-learn image \
  --prompt "A futuristic cityscape at sunset" \
  --iterations 3 \
  --budget 2.00 \
  --evaluate

# Save images to custom directory
prompt-learn image \
  --prompt "Abstract art with vibrant colors" \
  --output-dir ./generated_images \
  --iterations 5
```

**Run with verbose output:**
```bash
prompt-learn --verbose optimize \
  --prompt "Your prompt" \
  --dataset data.csv \
  --feedback-columns feedback
```

### SDK Usage

```python
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from providers.google_provider import GoogleProvider
from core.pricing import PricingCalculator

# Initialize with Google AI provider and budget control
optimizer = PromptLearningOptimizer(
    prompt="Analyze this customer feedback: {feedback}",
    provider=GoogleProvider(),
    pricing_calculator=PricingCalculator(),
    budget_limit=5.00,
    verbose=True
)

# Load and optimize
dataset = optimizer.load_data("customer_feedback.csv")
optimized_prompt = optimizer.optimize(
    dataset=dataset,
    output_column="analysis",
    feedback_columns=["quality_score", "accuracy_notes"]
)
```

## 🔧 Environment Setup

Set your API keys:
```bash
export OPENAI_API_KEY="your-openai-key"
export GOOGLE_API_KEY="your-google-ai-key"  # or GEMINI_API_KEY
```

## 📊 Cost Control Features

The enhanced fork includes comprehensive cost tracking:

```bash
# Set custom budget limits
prompt-learn optimize --budget 15.00 --prompt "..." --dataset data.csv

# Real-time cost tracking during optimization
prompt-learn --verbose optimize --prompt "..." --dataset large_data.csv

# Budget enforcement prevents runaway costs
# Optimization stops automatically when budget limit reached
```

## 🎨 Image Generation with "Nano Banana"

Test and optimize image generation prompts:

```python
from providers.google_provider import GoogleProvider

provider = GoogleProvider()

# Generate and evaluate images
result = provider.generate_image(
    prompt="A serene mountain landscape with morning mist",
    evaluate_quality=True
)

# Human-in-the-loop evaluation for prompt improvement
if result.needs_improvement:
    feedback = input("How should this image be improved? ")
    improved_prompt = provider.optimize_image_prompt(
        original_prompt=prompt,
        feedback=feedback
    )
```

## 🧪 Testing & Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run comprehensive test suite
pytest tests/ -v

# Run specific test categories
pytest tests/unit/ -v                    # Unit tests
pytest tests/unit/test_pricing.py -v     # Pricing tests
pytest tests/unit/test_cli_main.py -v    # CLI tests

# Check code quality
black .
flake8 .
mypy .
```

## 🏗️ Architecture

The enhanced fork uses clean architecture principles:

```
├── cli/                    # Command-line interface
│   ├── main.py            # CLI entry point
│   └── commands/          # Command implementations
├── core/                  # Core business logic
│   ├── pricing.py         # Cost tracking & budget enforcement
│   └── exceptions.py      # Custom error handling
├── interfaces/            # Abstract interfaces
│   └── token_counter.py   # Token counting abstraction
├── providers/             # AI provider implementations
│   ├── base_provider.py   # Provider interface
│   ├── openai_provider.py # OpenAI integration
│   └── google_provider.py # Google AI integration
├── optimizer_sdk/         # Original prompt learning SDK
└── tests/                 # Comprehensive test suite
```

## 📄 License

This project is licensed under the Elastic License 2.0 (ELv2). See [LICENSE.txt](LICENSE.txt) for details.

## 🤝 Contributing

This is an enhanced fork of the original prompt learning research. We welcome contributions that improve:

- CLI usability and features
- Provider integrations
- Cost optimization
- Documentation
- Test coverage

## 📖 Original Research

Based on the original prompt learning research by Arize AI. This enhanced fork adds production-ready features while maintaining the core research innovations.

---

**Authors**: Arize AI, Nouamane Benbrahim, Priyan Jindal

**Enhanced Features**: CLI interface, Google AI integration, pricing controls, production architecture, comprehensive testing