import json
import os
import random
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
from swebench.harness.utils import load_swebench_dataset

# Add optimizer_sdk to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))

from constants import CLINE_PROMPT
from evals import evaluate_results
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer
from run_cline import run_cline

OPTIMIZATION_LOOPS = 5
TRAIN_SIZE = 150 ## Lower this based on your Claude rate limits.
TEST_SIZE = 150 ## Lower this based on your Claude rate limits.
MAX_WORKERS = 50 ## Lower this based on your Claude rate limits + your machine's memory.
RULES = "do NOT use resume_task tool. Do NOT ask for user input/confirmation at any step of the process."

dataset = load_swebench_dataset("SWE-bench/SWE-bench_Lite", "test")

def collect_swebench_results(all_results):
    dataset_rows = []
    for result in all_results:
        instance_id = result["instance_id"]
    # Find the corresponding problem statement from dataset
    problem_statement = next(inst["problem_statement"] for inst in dataset if inst["instance_id"] == instance_id)
    patch = next(inst["patch"] for inst in dataset if inst["instance_id"] == instance_id)
    test_patch = next(inst["test_patch"] for inst in dataset if inst["instance_id"] == instance_id)
    if result["final_plan"]:
        dataset_rows.append({
            "instance_id": instance_id,
            "problem_statement": problem_statement,
            "final_plan": result["final_plan"],
            "test_patch": test_patch,
            "patch": patch,
        })
    train_df = pd.DataFrame(dataset_rows)
    return train_df

def run_cline_dataset(dataset):
    all_results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        futs = {ex.submit(run_cline, inst, i, RULES): inst["instance_id"] for i, inst in enumerate(dataset)}
        for fut in as_completed(futs):
            r = fut.result()
            all_results.append(r)
            print(f"[{r['instance_id']}] done")
    
    df = collect_swebench_results(all_results)
    evaluated_results = evaluate_results(df)

    accuracy = sum(evaluated_results["correctness"] == "correct") / len(evaluated_results)
    return evaluated_results, accuracy


def main():

    # Build Train and Test datasets
    random.seed(42)
    random.shuffle(dataset)
    train_dataset = dataset[:TRAIN_SIZE]
    test_dataset = dataset[len(dataset)-TEST_SIZE:]
    train_pd = pd.DataFrame.from_dict(train_dataset)
    test_pd = pd.DataFrame.from_dict(test_dataset)
    train_pd.to_csv("train_dataset.csv")
    test_pd.to_csv("test_dataset.csv")

    ruleset = "do NOT use resume_task tool. Do NOT ask for user input/confirmation at any step of the process."
    for idx in range(OPTIMIZATION_LOOPS):
        print(f"Running for idx: {idx}")

        evaluated_train_results, train_accuracy = run_cline_dataset(train_dataset)
        evaluated_train_results.to_csv(f"results/train_{idx}.csv")
        evaluated_test_results, test_accuracy = run_cline_dataset(test_dataset)
        evaluated_test_results.to_csv(f"results/test_{idx}.csv")
        
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
            f.write(f"train_accuracy: {train_accuracy}")
            f.write(f"test_accuracy: {test_accuracy}")
            f.write(f"optimized_ruleset_{idx}: {ruleset}")
            f.write(ruleset)
            

if __name__ == "__main__":
    main()