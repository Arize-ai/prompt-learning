"""
Optimize command - Core prompt optimization functionality.
"""

import click
import pandas as pd

from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from providers.google_provider import GoogleProvider
from core.exceptions import DatasetError, ProviderError, OptimizationError
from core.pricing import PricingCalculator

@click.command()
@click.option(
    "--prompt", 
    "-p",
    required=True,
    help="The baseline prompt to optimize"
)
@click.option(
    "--dataset",
    "-d", 
    required=True,
    type=click.Path(exists=True),
    help="Path to CSV/JSON dataset with examples and feedback"
)
@click.option(
    "--output-column",
    "-o",
    default="output",
    help="Column name containing LLM outputs"
)
@click.option(
    "--feedback-columns",
    "-f",
    multiple=True,
    help="Column names containing feedback (can specify multiple)"
)
@click.option(
    "--model",
    "-m",
    default="gpt-4",
    help="Model to use for optimization"
)
@click.option(
    "--provider",
    default="openai",
    type=click.Choice(["openai", "google"]),
    help="Model provider to use"
)
@click.option(
    "--context-size",
    "-c",
    default=128000,
    type=int,
    help="Context window size in tokens"
)
@click.option(
    "--save",
    "-s",
    type=click.Path(),
    help="Path to save optimized prompt"
)
@click.option(
    "--budget",
    "-b",
    default=5.0,
    type=float,
    help="Maximum budget in USD to spend on optimization (default: $5.00)"
)
@click.pass_context
def optimize(ctx, prompt, dataset, output_column, feedback_columns, model, provider, context_size, save, budget):
    """
    Optimize a prompt using natural language feedback.
    
    Takes a baseline prompt and dataset with feedback to generate
    an improved version using meta-prompt optimization. Budget limiting
    prevents unexpected costs by stopping optimization before the limit.
    
    Examples:
        # Basic optimization with default $5 budget
        prompt-learn optimize -p "Your prompt" -d data.csv -f feedback
        
        # Custom budget for longer optimization
        prompt-learn optimize -p "Complex prompt" -d large_data.csv -f feedback --budget 20.00
        
        # Use cheaper Gemini for cost-effective optimization  
        prompt-learn optimize -p "Your prompt" -d data.csv -f feedback --provider google
    """
    verbose = ctx.obj.get('verbose', False) if ctx.obj else False
    
    # Initialize pricing calculator
    pricing_calculator = PricingCalculator()
    
    print("Starting prompt optimization...")
    print(f"Budget limit: ${budget:.2f}")
    if verbose:
        print(f"Baseline prompt: {prompt[:100]}...")
        print(f"Dataset: {dataset}")
        print(f"Model: {model} ({provider})")
    
    # Load dataset
    try:
        if dataset.endswith('.csv'):
            df = pd.read_csv(dataset)
        else:
            df = pd.read_json(dataset)
        
        print(f"Loaded {len(df)} examples")
        if verbose:
            print(f"Dataset columns: {list(df.columns)}")
        
    except (DatasetError, FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"Dataset error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error loading dataset: {e}")
        return
    
    # Initialize optimizer
    try:
        provider_instance = None
        
        if provider == "google":
            # Use GoogleProvider
            provider_instance = GoogleProvider()
            if verbose:
                print("Google provider initialized")
        
        optimizer = PromptLearningOptimizer(
            prompt=prompt,
            model_choice=model,
            provider=provider_instance,
            verbose=verbose,
            pricing_calculator=pricing_calculator,
            budget_limit=budget
        )
        
        if verbose:
            print("Optimizer initialized")
        
    except (ProviderError, ValueError) as e:
        print(f"Provider error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error initializing optimizer: {e}")
        return
    
    # Run optimization
    try:
        print("Running optimization...")
        
        optimized_prompt = optimizer.optimize(
            dataset=df,
            output_column=output_column,
            feedback_columns=list(feedback_columns),
            context_size_k=context_size
        )
        
        print("Optimization complete!")
        
        # Display cost summary
        usage = pricing_calculator.get_usage_summary()
        print(f"\nCost Summary:")
        print(f"Total cost: ${usage['total_cost']:.4f}")
        print(f"Total tokens: {usage['total_tokens']:,} ({usage['total_input_tokens']:,} input + {usage['total_output_tokens']:,} output)")
        if verbose:
            print(f"Budget remaining: ${budget - usage['total_cost']:.4f}")
        
        # Display results
        print("\nOriginal Prompt:")
        print("-" * 50)
        print(prompt)
        
        print("\nOptimized Prompt:")
        print("-" * 50)
        print(str(optimized_prompt))
        
        # Save if requested
        if save:
            with open(save, 'w') as f:
                f.write(str(optimized_prompt))
            print(f"Saved optimized prompt to {save}")
            
    except (DatasetError, OptimizationError, ProviderError) as e:
        print(f"Optimization error: {e}")
        return
    except Exception as e:
        print(f"Unexpected error during optimization: {e}")
        return