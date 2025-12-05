"""
Optimize command - Core prompt optimization functionality.
"""

import click
import pandas as pd

from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from providers.google_provider import GoogleProvider
from core.exceptions import DatasetError, ProviderError, OptimizationError

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
def optimize(prompt, dataset, output_column, feedback_columns, model, provider, context_size, save):
    """
    Optimize a prompt using natural language feedback.
    
    Takes a baseline prompt and dataset with feedback to generate
    an improved version using meta-prompt optimization.
    """
    
    print(f"Starting prompt optimization...")
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
        print(f"Dataset columns: {list(df.columns)}")
        
    except (DatasetError, FileNotFoundError, pd.errors.EmptyDataError) as e:
        print(f"❌ Dataset error: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error loading dataset: {e}")
        return
    
    # Initialize optimizer
    try:
        provider_instance = None
        
        if provider == "google":
            # Use GoogleProvider
            provider_instance = GoogleProvider()
            print("✅ Google provider initialized")
        
        optimizer = PromptLearningOptimizer(
            prompt=prompt,
            model_choice=model,
            provider=provider_instance
        )
        
        print("✅ Optimizer initialized")
        
    except (ProviderError, ValueError) as e:
        print(f"❌ Provider error: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error initializing optimizer: {e}")
        return
    
    # Run optimization
    try:
        print("🚀 Running optimization...")
        
        optimized_prompt = optimizer.optimize(
            dataset=df,
            output_column=output_column,
            feedback_columns=list(feedback_columns),
            context_size_k=context_size
        )
        
        print("✅ Optimization complete!")
        
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
            print(f"💾 Saved optimized prompt to {save}")
            
    except (DatasetError, OptimizationError, ProviderError) as e:
        print(f"❌ Optimization error: {e}")
        return
    except Exception as e:
        print(f"❌ Unexpected error during optimization: {e}")
        return