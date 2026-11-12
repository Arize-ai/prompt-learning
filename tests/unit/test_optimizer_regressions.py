"""
Regression tests for optimizer_sdk bugs fixed alongside the phoenix-evals 3.x import fix.
"""

import os

import pandas as pd
from unittest.mock import patch

from optimizer_sdk.annotator import Annotator
from optimizer_sdk.meta_prompt import MetaPrompt
from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer


def _dataset():
    return pd.DataFrame(
        {
            "question": ["What is 2+2?", "Capital of France?"],
            "output": ["4", "Paris"],
            "expected": ["4", "Paris"],
            "correctness": ["correct", "correct"],
        }
    )


def _evaluator(dataset):
    dataset = dataset.copy()
    dataset["score"] = ["good", "good"]
    return dataset, ["score"]


def test_run_evaluators_does_not_mutate_caller_list():
    optimizer = PromptLearningOptimizer(prompt="Q: {question}", openai_api_key="k")
    caller_columns = ["correctness"]

    _, columns = optimizer.run_evaluators(_dataset(), [_evaluator], caller_columns)
    _, columns_again = optimizer.run_evaluators(
        _dataset(), [_evaluator], caller_columns
    )

    assert caller_columns == ["correctness"]
    assert columns == ["correctness", "score"]
    assert columns_again == ["correctness", "score"]


def test_run_evaluators_default_list_is_not_shared():
    optimizer = PromptLearningOptimizer(prompt="Q: {question}", openai_api_key="k")

    _, first = optimizer.run_evaluators(_dataset(), [_evaluator])
    _, second = optimizer.run_evaluators(_dataset(), [_evaluator])

    assert first == ["score"]
    assert second == ["score"]


def test_meta_prompt_clears_annotations_placeholder_and_writes_no_file(tmp_path):
    cwd = os.getcwd()
    os.chdir(tmp_path)
    try:
        content = MetaPrompt().construct_content(
            batch_df=_dataset(),
            prompt_to_optimize_content="Q: {question}",
            template_variables=["question"],
            feedback_columns=["correctness"],
            output_column="output",
        )
    finally:
        os.chdir(cwd)

    assert "{annotations}" not in content
    assert not (tmp_path / "metaprompt.txt").exists()


def test_meta_prompt_tolerates_variables_missing_from_dataset():
    content = MetaPrompt().construct_content(
        batch_df=_dataset(),
        prompt_to_optimize_content="Q: {question} {not_a_column}",
        template_variables=["question", "not_a_column"],
        feedback_columns=["correctness"],
        output_column="output",
    )

    assert "What is 2+2?" in content


def test_annotator_uses_ground_truth_column():
    content = Annotator("{baseline prompt}\n{examples}").construct_content(
        _dataset(),
        "Q: {question}",
        ["question"],
        ["correctness"],
        "output",
        ground_truth_column="expected",
    )

    assert "Ground Truth: Paris" in content


def test_create_annotation_gives_each_annotator_the_original_prompt():
    optimizer = PromptLearningOptimizer(prompt="Q: {question}", openai_api_key="k")
    sent = []

    with patch.object(
        Annotator,
        "generate_annotation",
        side_effect=lambda content: sent.append(content) or "note",
    ):
        annotations = optimizer.create_annotation(
            prompt="BASELINE",
            template_variables=["question"],
            dataset=_dataset(),
            feedback_columns=["correctness"],
            annotator_prompts=["first: {baseline prompt}", "second: {baseline prompt}"],
            output_column="output",
        )

    assert annotations == ["note", "note"]
    assert sent == ["first: BASELINE", "second: BASELINE"]
