import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from swebench.harness.utils import load_swebench_dataset

# Add optimizer_sdk to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from constants import CLINE_PROMPT
from evals import evaluate_results
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from run_cline import run_cline


def main():

    # Build Train and Test datasets
    dataset = load_swebench_dataset("SWE-bench/SWE-bench_Lite", "test")
    random.seed(42)
    random.shuffle(dataset)
    train_dataset = dataset[:1]
    test_dataset = dataset[150:]
    train_pd = pd.DataFrame.from_dict(train_dataset)
    test_pd = pd.DataFrame.from_dict(test_dataset)
    train_pd.to_csv("train_dataset.csv")
    test_pd.to_csv("test_dataset.csv")

    max_workers = 75
    ruleset = "do NOT use resume_task tool. Do NOT ask for user input/confirmation at any step of the process."

    for idx in range(1):

        print(f"Running for idx: {idx}")
        all_results = []

        with ThreadPoolExecutor(max_workers=max_workers) as ex:
            futs = {ex.submit(run_cline, inst, i, ruleset): inst["instance_id"] for i, inst in enumerate(train_dataset)}
            for fut in as_completed(futs):
                r = fut.result()
                all_results.append(r)
                print(f"[{r['instance_id']}] done")
        
        # Create dataset with the requested columns
        dataset_rows = []
        for result in all_results:
            instance_id = result["instance_id"]
            # Find the corresponding problem statement from train_dataset
            problem_statement = next(inst["problem_statement"] for inst in train_dataset if inst["instance_id"] == instance_id)
            patch = next(inst["patch"] for inst in train_dataset if inst["instance_id"] == instance_id)
            test_patch = next(inst["test_patch"] for inst in train_dataset if inst["instance_id"] == instance_id)
            if result["final_plan"]:
                dataset_rows.append({
                    "instance_id": instance_id,
                    "problem_statement": problem_statement,
                    "final_plan": result["final_plan"],
                    "test_patch": test_patch,
                    "patch": patch,
                })
        
        # Create DataFrame and save to CSV
        train_df = pd.DataFrame(dataset_rows)

        evaluated_train_results = evaluate_results(train_df)

        evaluated_train_results.to_csv(f"results/results_{idx}.csv")

        accuracy = sum(evaluated_train_results["correctness"] == "correct") / len(evaluated_train_results)
        pl_optimizer = PromptLearningOptimizer(
            prompt=CLINE_PROMPT,
            model_choice="gpt-4o",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )
        ruleset = pl_optimizer.optimize(
            dataset=evaluated_train_results,
            output_column="final_plan",
            feedback_columns=["correctness", "explanation"],
            ruleset = ruleset,
            context_size_k=100000
        )

        with open(f"rulesets/ruleset_{idx}.txt", "w") as f:
            f.write(f"train_accuracy: {accuracy}")
            f.write(f"generated ruleset_{idx}: {ruleset}")
            f.write(ruleset)
            

if __name__ == "__main__":
    main()