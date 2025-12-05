from run_act import run_act
from swebench.harness.utils import load_swebench_dataset
import random
from evals_act import evaluate_results
import os
import sys
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from constants import CLINE_PROMPT

import pandas as pd


LOOPS = 5
TRAIN_SIZE = 1
TEST_SIZE = 1
WORKERS = 52

os.environ["CLINE_DISABLE_TERMINAL_REUSE"] = "1"
os.environ["CLINE_DEFAULT_TERMINAL_PROFILE"] = "bash"
os.environ["CLINE_SHELL_INTEGRATION_TIMEOUT_SEC"] = "10"
os.environ["CLINE_STANDALONE_CAPTURE_STDIO"] = "1"
os.environ["CLINE_SKIP_RESUME_CONFIRMATION"] = "1"
os.environ["CLINE_AUTO_FOLLOWUP"] = "1"
os.environ["CLINE_ENVIRONMENT"] = "local"


def main():

    dataset_name = "SWE-bench/SWE-bench_Lite"
    ds = load_swebench_dataset(dataset_name, "test")
    ids = [inst["instance_id"] for inst in ds]
    random.shuffle(ids)
    train_ids = ids[:TRAIN_SIZE]
    test_ids = ids[len(ids) - TEST_SIZE :]

    ruleset = ""

    for loop in range(LOOPS):
        print(f"Running for loop: {loop}")

        train_run_id = f"claude_150_train_{loop}"
        test_run_id = f"150_act_test_{loop}"

        train_df = run_act(
            dataset_name=dataset_name,
            instance_ids=train_ids,
            run_id=train_run_id,
            ruleset=ruleset,
            workers=WORKERS,
        )
        test_df = run_act(
            dataset_name=dataset_name,
            instance_ids=test_ids,
            run_id=test_run_id,
            ruleset=ruleset,
            workers=WORKERS,
        )

        test_df.to_csv(f"act_results/test_results_{loop}.csv", index=False)

        train_acc = sum(train_df["pass_or_fail"] == "pass") / len(train_df)
        test_acc = sum(test_df["pass_or_fail"] == "pass") / len(test_df)
        print(f"Train Accuracy: {train_acc}")
        print(f"Test Accuracy: {test_acc}")

        subprocess.run(
            [
                "/opt/anaconda3/envs/cline/bin/python3",
                "-m",
                "pip",
                "install",
                "--upgrade",
                "arize-phoenix",
                "wrapt",
            ]
        )
        evaluated_train_results = evaluate_results(train_df)
        evaluated_train_results.to_csv(
            f"act_results/train_results_{loop}.csv", index=False
        )

        pl_optimizer = PromptLearningOptimizer(
            prompt=CLINE_PROMPT,
            model_choice="gpt-5",
            openai_api_key=os.getenv("OPENAI_API_KEY"),
        )
        ruleset = pl_optimizer.optimize(
            dataset=evaluated_train_results,
            output_column="cline_patch",
            feedback_columns=["correctness", "explanation"],
            ruleset=ruleset,
            context_size_k=400000,
        )
        with open(f"act_rulesets/ruleset_{loop}.txt", "w") as f:
            f.write(f"train_accuracy: {train_acc}")
            f.write(f"training_examples_used: {len(evaluated_train_results)}")
            f.write(f"test_accuracy: {test_acc}")
            f.write(f"optimized ruleset_{loop}: {ruleset}")
            f.write(ruleset)


if __name__ == "__main__":
    main()
