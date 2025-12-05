"""
Evaluate command - Run evaluations without optimization.
"""

import click
import pandas as pd

from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer


@click.command()
@click.option(
    "--dataset",
    "-d",
    required=True,
    type=click.Path(exists=True),
    help="Path to CSV/JSON dataset",
)
@click.option("--evaluators", "-e", multiple=True, help="Evaluator functions to run")
@click.option(
    "--output", "-o", type=click.Path(), help="Path to save evaluation results"
)
def evaluate(dataset, evaluators, output):
    """
    Run evaluations on a dataset without optimization.
    """

    print(f"Running evaluation on dataset: {dataset}")

    # Load dataset
    try:
        if dataset.endswith(".csv"):
            df = pd.read_csv(dataset)
        else:
            df = pd.read_json(dataset)

        print(f"Loaded {len(df)} examples")

    except Exception as e:
        print(f"Error loading dataset: {e}")
        return

    # TODO: Implement evaluation logic
    print("Evaluation functionality coming soon...")

    if output:
        print(f"Results would be saved to: {output}")
