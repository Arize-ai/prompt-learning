import pandas as pd
from phoenix.evals import llm_generate, OpenAIModel
import json
from typing import Dict


def evaluate_results(results: pd.DataFrame) -> pd.DataFrame:

    prompt = """
    You are an expert software engineer, tasked with reviewing a coding agent. 

    You are given a problem statement and a plan from a coding agent. You are also given a ground truth solution to the problem. 

    Your task is to review the the plan from the coding agent and determine if it is correct. Evaluate correctness based on the following factors:

    - Whether plan matches ground truth patch
    - Whether the output of the plan would pass the test in test_patch 

    Note that simply passing the test in test_patch does not necessarily mean the output is correct. The output must match the ground truth patch in functionality.

    problem_statement: {problem_statement}
    coding agent plan: {final_plan}
    ground_truth_patch: {patch}
    test_patch: {test_patch}

    Return in the following JSON format:
    "correctness": "correct" or "incorrect"
    "explanation": "brief explanation of your reasoning"
    """

    def output_parser(response: str, row_index = int) -> Dict[str, str]:
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                return {"__error__": str(e)}

    evals = llm_generate(
        dataframe = results,
        template = prompt,
        model=OpenAIModel(
            model_name="gpt-5",
            model_kwargs={
                "response_format": {"type": "json_object"},
                "temperature": 1
            }
        ),
        output_parser = output_parser
    )

    for idx, row in evals.iterrows():
        problem_statement = results.iloc[idx]["problem_statement"]
        output = results.iloc[idx]["final_plan"]
        evals.loc[idx, "problem_statement"] = problem_statement
        evals.loc[idx, "final_plan"] = output
        evals.loc[idx, "test_patch"] = results.iloc[idx]["test_patch"]
        evals.loc[idx, "patch"] = results.iloc[idx]["patch"]
        evals.loc[idx, "instance_id"] = results.iloc[idx]["instance_id"]


    evals.to_csv("training_evals.csv", index=False)

    return evals

