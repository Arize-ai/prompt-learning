"""
Phoenix Experiments Module

This module provides functions to log experiments and runs to Phoenix using the REST API.
"""

import requests
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd


def clean_for_json(obj: Any) -> Any:
    """
    Recursively clean an object to make it JSON-serializable.
    Converts NaN, Infinity, and -Infinity to None.
    """
    if isinstance(obj, dict):
        return {k: clean_for_json(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, float):
        if pd.isna(obj) or obj == float("inf") or obj == float("-inf"):
            return None
        return obj
    elif pd.isna(obj):
        return None
    return obj


def log_experiment_to_phoenix(
    hostname: str,
    api_key: str,
    dataset_obj: Any,
    experiment_name: str,
    experiment_df: pd.DataFrame,
    metadata: Optional[Dict[str, Any]] = None,
) -> Optional[Dict[str, Any]]:
    """
    Log experiment results to Phoenix using the REST API

    Args:
        hostname: Phoenix hostname (base URL)
        api_key: Phoenix API key for authentication
        dataset_obj: Phoenix dataset object (with .id and examples)
        experiment_name: Name of the experiment
        experiment_df: DataFrame containing experiment results with columns:
                      - instance_id
                      - cline_patch (output)
                      - correctness (evaluation label)
                      - explanation (evaluation explanation)
                      - score (evaluation score)
        metadata: Optional dict of metadata for the experiment

    Returns:
        Response from Phoenix API containing experiment details, or None if failed
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    # Step 1: Create the experiment
    exp_url = f"{hostname}/v1/datasets/{dataset_obj.id}/experiments"
    exp_body = {
        "name": experiment_name,
        "description": f"Cline Act Mode optimization - {experiment_name}",
        "metadata": clean_for_json(metadata or {}),
        "repetitions": 1,
    }

    exp_response = requests.post(exp_url, headers=headers, json=exp_body)

    if exp_response.status_code != 200:
        print(f"✗ Failed to create experiment: {exp_response.status_code}")
        print(f"Response: {exp_response.text}")
        exp_response.raise_for_status()
        return None

    experiment_data = exp_response.json()
    experiment_id = experiment_data["data"]["id"]
    print(f"✓ Created experiment '{experiment_name}' (ID: {experiment_id})")

    # Step 2: Fetch dataset examples from Phoenix API to get example IDs
    examples_url = f"{hostname}/v1/datasets/{dataset_obj.id}/examples"
    examples_response = requests.get(examples_url, headers=headers)

    if examples_response.status_code != 200:
        print(f"✗ Failed to fetch dataset examples: {examples_response.status_code}")
        print(f"Response: {examples_response.text}")
        return experiment_data

    examples_data = examples_response.json()
    examples = examples_data["data"]["examples"]

    # Create a mapping from instance_id to example_id
    example_id_map = {}
    for example in examples:
        metadata = example.get("metadata", {})
        if not metadata:
            raise ValueError(f"Metadata not found for example {example['id']}")
        instance_id = metadata.get("instance_id")
        if instance_id:
            example_id_map[instance_id] = example["id"]

    print(f"✓ Mapped {len(example_id_map)} examples from dataset")

    print("example_id_map")
    print(example_id_map)

    # Step 3: Create experiment runs for each result
    run_url = f"{hostname}/v1/experiments/{experiment_id}/runs"
    eval_url = f"{hostname}/v1/experiment_evaluations"
    successful_runs = 0
    failed_runs = 0
    successful_evals = 0
    failed_evals = 0

    for idx, row in experiment_df.iterrows():

        instance_id = row.get("instance_id")
        if not instance_id:
            raise ValueError(f"Instance ID not found for row {idx}")
        if instance_id not in example_id_map:
            print(f"⚠ Skipping instance {instance_id}: not found in dataset")
            failed_runs += 1
            continue

        dataset_example_id = example_id_map[instance_id]

        # Prepare the run data
        current_time = datetime.utcnow().isoformat() + "Z"

        # Get output and handle NaN values
        cline_patch = row.get("cline_patch", "")
        if pd.isna(cline_patch):
            cline_patch = ""

        run_body = clean_for_json(
            {
                "dataset_example_id": dataset_example_id,
                "output": str(cline_patch),
                "repetition_number": 1,
                "start_time": current_time,
                "end_time": current_time,
            }
        )

        run_response = requests.post(run_url, headers=headers, json=run_body)

        if run_response.status_code == 200:
            successful_runs += 1
            run_data = run_response.json()
            run_id = run_data["data"]["id"]

            # Step 4: Create evaluation for this run
            correctness = row.get("correctness", "")
            explanation = row.get("explanation", "")
            score = 1.0 if correctness == "correct" else 0.0

            # Handle NaN values in evaluation data
            if pd.isna(correctness):
                correctness = ""
            if pd.isna(explanation):
                explanation = ""
            if pd.isna(score):
                score = 0.0

            eval_body = clean_for_json(
                {
                    "experiment_run_id": run_id,
                    "name": "correctness",
                    "annotator_kind": "LLM",
                    "start_time": current_time,
                    "end_time": current_time,
                    "result": {
                        "label": str(correctness),
                        "score": float(score),
                        "explanation": str(explanation),
                    },
                }
            )

            eval_response = requests.post(eval_url, headers=headers, json=eval_body)

            if eval_response.status_code == 200:
                successful_evals += 1
            else:
                failed_evals += 1
                if failed_evals <= 3:  # Only print first 3 errors to avoid spam
                    print(
                        f"⚠ Failed to create evaluation for {instance_id}: {eval_response.status_code}"
                    )
                    print(f"Response: {eval_response.text}")
        else:
            failed_runs += 1
            if failed_runs <= 3:  # Only print first 3 errors to avoid spam
                print(
                    f"⚠ Failed to create run for {instance_id}: {run_response.status_code}"
                )

    print(f"✓ Created {successful_runs} experiment runs ({failed_runs} failed)")
    print(f"✓ Created {successful_evals} evaluations ({failed_evals} failed)")

    return experiment_data
