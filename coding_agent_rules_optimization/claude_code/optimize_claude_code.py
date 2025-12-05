#!/usr/bin/env python3
"""
Optimize Claude Code using prompt learning on SWE-bench.

Usage:
    python optimize_claude_code.py
"""

import os
import sys
import subprocess
from pathlib import Path
import pandas as pd
import random
from phoenix.client import Client
import asyncio

from run_claude import run_claude
from swebench.harness.utils import load_swebench_dataset
from evals import evaluate_results

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from constants import CLAUDE_CODE_PROMPT


# Configuration
LOOPS = 5
TRAIN_SIZE = 150
TEST_SIZE = 150
WORKERS = 50

HOSTNAME = os.getenv("PHOENIX_HOSTNAME")


def load_split_swebench():
    """Load SWE-bench Lite and split by repository."""
    print("Loading SWE-bench Lite dataset...")
    dataset_name = "SWE-bench/SWE-bench_Lite"
    dataset = load_swebench_dataset(dataset_name, "test")
    print(f"Loaded {len(dataset)} instances")

    # Define train and test repos
    # By using certain repos for train and certain repos for test, we prevent overfitting
    train_repos = {
        "django/django",
        "pytest-dev/pytest",
        "sphinx-doc/sphinx",
        "astropy/astropy",
        "psf/requests",
        "pylint-dev/pylint",
    }

    test_repos = {
        "sympy/sympy",
        "matplotlib/matplotlib",
        "scikit-learn/scikit-learn",
        "pydata/xarray",
        "mwaskom/seaborn",
        "pallets/flask",
    }

    # Split by repository
    train_examples = [inst for inst in dataset if inst["repo"] in train_repos]
    test_examples = [inst for inst in dataset if inst["repo"] in test_repos]

    # Sample random subsets
    random.seed(42)  # For reproducibility
    train_dataset = random.sample(train_examples, min(TRAIN_SIZE, len(train_examples)))
    test_dataset = random.sample(test_examples, min(TEST_SIZE, len(test_examples)))

    # Extract IDs
    train_ids = [inst["instance_id"] for inst in train_dataset]
    test_ids = [inst["instance_id"] for inst in test_dataset]

    # Create DataFrames
    train_pd = pd.DataFrame(train_dataset)
    test_pd = pd.DataFrame(test_dataset)

    # Verify the split
    print(f"\nDataset split:")
    print(
        f"  Train: {len(train_dataset)} instances ({len(train_dataset)/len(dataset)*100:.1f}%)"
    )
    print(
        f"  Test: {len(test_dataset)} instances ({len(test_dataset)/len(dataset)*100:.1f}%)"
    )
    print(f"\n  Train repos: {sorted(train_repos)}")
    print(f"  Test repos: {sorted(test_repos)}")
    print(f"\n  Train repo distribution:")
    print(train_pd["repo"].value_counts())
    print(f"\n  Test repo distribution:")
    print(test_pd["repo"].value_counts())

    return dataset_name, train_ids, test_ids, train_pd, test_pd


def load_split_swebench_repo(repo, train_percentage=0.5):
    """Load SWE-bench Lite and split by date for a specific repo."""
    from datetime import datetime

    print(f"Loading SWE-bench Lite dataset for repo: {repo}...")
    dataset_name = "SWE-bench/SWE-bench_Lite"
    dataset = load_swebench_dataset(dataset_name, "test")

    # Filter by repo
    repo_examples = [inst for inst in dataset if inst["repo"] == repo]
    print(f"Found {len(repo_examples)} instances for {repo}")

    # Sort by created_at date (earliest first)
    repo_examples.sort(
        key=lambda x: datetime.fromisoformat(x["created_at"].replace("Z", "+00:00"))
    )

    # Split by train_percentage
    train_size = int(len(repo_examples) * train_percentage)
    train_dataset = repo_examples[:train_size]
    test_dataset = repo_examples[train_size:]

    # Extract IDs
    train_ids = [inst["instance_id"] for inst in train_dataset]
    test_ids = [inst["instance_id"] for inst in test_dataset]

    # Create DataFrames
    train_pd = pd.DataFrame(train_dataset)
    test_pd = pd.DataFrame(test_dataset)

    print(f"\nDataset split:")
    print(
        f"  Train: {len(train_dataset)} instances ({len(train_dataset)/len(repo_examples)*100:.1f}%)"
    )
    print(
        f"  Test: {len(test_dataset)} instances ({len(test_dataset)/len(repo_examples)*100:.1f}%)"
    )

    return dataset_name, train_ids, test_ids, train_pd, test_pd


def cleanup_docker():
    """Clean up Docker resources to free space."""
    print("  Cleaning up Docker resources...")

    # Remove all stopped containers
    subprocess.run(
        ["docker", "container", "prune", "-f"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    # Remove dangling images (most important!)
    subprocess.run(
        ["docker", "image", "prune", "-f"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    # Remove build cache
    subprocess.run(
        ["docker", "builder", "prune", "-f"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )

    print("  ✓ Docker cleanup complete")


def setup_phoenix(train_pd, test_pd, train_name, test_name, model_name):
    """Upload datasets to Phoenix."""
    print("\nUploading datasets to Phoenix...")
    from phoenix.client import Client

    phoenix_client = Client(base_url=HOSTNAME, api_key=os.getenv("PHOENIX_API_KEY"))

    train_dataset = phoenix_client.datasets.create_dataset(
        name=f"{train_name} {len(train_pd)} {model_name}",
        dataset_description="Claude Code: SWE-bench Train",
        dataframe=train_pd,
        input_keys=["problem_statement"],
        metadata_keys=["instance_id", "test_patch"],
        output_keys=[],
    )

    test_dataset = phoenix_client.datasets.create_dataset(
        name=f"{test_name} {len(test_pd)} {model_name}",
        dataset_description="Claude Code: SWE-bench Test",
        dataframe=test_pd,
        input_keys=["problem_statement"],
        metadata_keys=["instance_id", "test_patch"],
        output_keys=[],
    )
    # train_dataset = phoenix_client.datasets.get_dataset(dataset=f"Claude Code: SWE-bench Train ({TRAIN_SIZE})")
    # test_dataset = phoenix_client.datasets.get_dataset(dataset=f"Claude Code: SWE-bench Test ({TEST_SIZE})")

    print("✓ Datasets uploaded to Phoenix")
    return train_dataset, test_dataset


def run_optimization_loop(
    dataset_name,
    train_ids,
    test_ids,
    train_dataset_obj,
    ruleset,
    repo,
    model_name="claude-sonnet-4-5",
):
    """Run the optimization loop."""
    # Create output directories
    Path("claude_code_results").mkdir(exist_ok=True)
    Path("act_rulesets").mkdir(exist_ok=True)

    for loop in range(LOOPS):
        print("\n" + "=" * 80)
        print(f"LOOP {loop}")
        print("=" * 80)

        train_run_id = f"{repo}_train_{loop}_{model_name}"
        test_run_id = f"{repo}_test_{loop}_{model_name}"

        # Run on train set
        print(f"\nRunning Claude Code on train set ({len(train_ids)} instances)...")
        train_df = run_claude(
            dataset_name=dataset_name,
            instance_ids=train_ids,
            run_id=train_run_id,
            ruleset=ruleset,
            workers=WORKERS,
            wait_seconds=600,
            model_name=model_name,
        )
        cleanup_docker()

        train_df.to_csv(
            f"claude_code_results/{model_name}/{repo}_train_results_{loop}.csv",
            index=False,
        )

        # Run on test set
        print(f"\nRunning Claude Code on test set ({len(test_ids)} instances)...")
        test_df = run_claude(
            dataset_name=dataset_name,
            instance_ids=test_ids,
            run_id=test_run_id,
            ruleset=ruleset,
            workers=WORKERS,
            wait_seconds=600,
            model_name=model_name,
        )
        cleanup_docker()

        # # Save test results
        test_df.to_csv(
            f"claude_code_results/{model_name}/{repo}_test_results_{loop}.csv",
            index=False,
        )

        # Calculate accuracy
        train_acc = sum(train_df["pass_or_fail"] == "pass") / len(train_df)
        test_acc = sum(test_df["pass_or_fail"] == "pass") / len(test_df)

        print(f"\nResults for loop {loop}:")
        print(f"  Train Accuracy: {train_acc:.2%}")
        print(f"  Test Accuracy: {test_acc:.2%}")

        # Ensure phoenix package is up to date (swebench might have messed with it)
        print("\nReinstalling Phoenix...")
        subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "-qq",
                "--upgrade",
                "arize-phoenix",
                "wrapt",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        # Evaluate results
        print("\nEvaluating train results...")
        evaluated_train_results = asyncio.run(
            evaluate_results(train_df, model="gpt-4.1")
        )
        evaluated_train_results.to_csv(
            f"claude_code_results/{model_name}/{repo}_evaluated_train_results_{loop}.csv",
            index=False,
        )

        # Log to Phoenix
        print("Logging experiment to Phoenix...")
        try:
            from phoenix_experiments import log_experiment_to_phoenix

            log_experiment_to_phoenix(
                hostname=HOSTNAME,
                api_key=os.getenv("PHOENIX_API_KEY"),
                dataset_obj=train_dataset_obj,
                experiment_name=f"{repo} Train {loop}",
                experiment_df=evaluated_train_results,
                metadata={
                    "loop": loop,
                    "train_accuracy": train_acc,
                    "test_accuracy": test_acc,
                },
            )
            print("✓ Logged to Phoenix")
        except Exception as e:
            print(f"⚠ Warning: Failed to log to Phoenix: {e}")

        # Optimize ruleset (commented out for now, uncomment when ready)
        print("\nOptimizing ruleset...")
        pl_optimizer = PromptLearningOptimizer(
            prompt=CLAUDE_CODE_PROMPT,
            model_choice="gpt-5",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        ruleset = pl_optimizer.optimize(
            dataset=evaluated_train_results,
            output_column="coding_agent_patch",
            feedback_columns=[
                "problem_statement",
                "ground_truth_patch",
                "test_patch",
                "pass_or_fail",
                "explanation",
            ],
            ruleset=ruleset,
            context_size_k=400000,
        )

        # Save ruleset
        with open(f"act_rulesets/{model_name}/{repo}_ruleset_{loop}.txt", "w") as f:
            f.write(f"train_accuracy: {train_acc}\n")
            f.write(f"test_accuracy: {test_acc}\n")
            f.write(f"optimized ruleset_{loop}:\n{ruleset}\n")
        print(f"✓ Saved ruleset to act_rulesets/{model_name}/{repo}_ruleset_{loop}.txt")

        print(f"\n{'='*80}")
        print(f"Completed loop {loop}")
        print(f"{'='*80}\n")


def main():
    """Main entry point."""
    print("=" * 80)
    print("Claude Code Optimization")
    print("=" * 80)
    # model_names = ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"]
    model_name = "claude-sonnet-4-5-20250929"

    train_name = "Claude Code: Django Train"
    test_name = "Claude Code: Django Test"

    dataset_name, train_ids, test_ids, train_pd, test_pd = load_split_swebench_repo(
        repo="django/django", train_percentage=0.6
    )

    train_dataset_obj, test_dataset_obj = setup_phoenix(
        train_pd, test_pd, train_name, test_name, model_name=model_name
    )

    # Run optimization loop
    run_optimization_loop(
        dataset_name=dataset_name,
        train_ids=train_ids,
        test_ids=test_ids,
        train_dataset_obj=train_dataset_obj,
        ruleset=" ",
        repo="django",
        model_name=model_name,
    )

    print("\n" + "=" * 80)
    print("✓ Optimization complete!")
    print("=" * 80)
    # cleanup_docker()


if __name__ == "__main__":
    main()
