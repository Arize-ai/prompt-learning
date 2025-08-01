import os, getpass
import openai
import pandas as pd
from phoenix.evals import OpenAIModel, llm_generate
import re
import nest_asyncio
nest_asyncio.apply()

os.environ['OPENAI_API_KEY'] = os.environ['OPENAI_API_KEY'] or getpass.getpass('OpenAI API Key:')

df = pd.read_csv("support_query_classification/hard_queries.csv")
train_set = df.sample(frac=0.8, random_state=42)
test_set = df.drop(train_set.index)

system_prompt = """You are given a support query:
support query: {query}

Classify the support query into one of the following categories:
Account Creation
Login Issues
Password Reset
Two-Factor Authentication
Profile Updates
Billing Inquiry
Refund Request
Subscription Upgrade/Downgrade
Payment Method Update
Invoice Request
Order Status
Shipping Delay
Product Return
Warranty Claim
Technical Bug Report
Feature Request
Integration Help
Data Export
Security Concern
Terms of Service Question
Privacy Policy Question
Compliance Inquiry
Accessibility Support
Language Support
Mobile App Issue
Desktop App Issue
Email Notifications
Marketing Preferences
Beta Program Enrollment
General Feedback

Return just the category, no other text.
"""

def generate_output(dataset, system_prompt):
    output_model = OpenAIModel(
        model="gpt-4.1-2025-04-14",
        model_kwargs={
            "temperature": 0
        }
    )
    outputs = llm_generate(
        dataframe=dataset,
        template=system_prompt,
        model=output_model,
        concurrency=40,
        verbose=True
    )
    return outputs["output"]

# Runtime evaluator functions
def find_attributes(output):
    """Extract fields from evaluator output"""
    correctness_pattern = r'"correctness":\s*"([^"]*)"'
    explanation_pattern = r'"explanation":\s*"([^"]*)"'
    confusion_reason_pattern = r'"confusion_reason":\s*"([^"]*)"'
    error_type_pattern = r'"error_type":\s*"([^"]*)"'
    top_3_classes_pattern = r'"top_3_classes":\s*\[(.*?)\]'
    evidence_span_pattern = r'"evidence_span":\s*"([^"]*)"'
    
    match_correctness = re.search(correctness_pattern, output, re.IGNORECASE)
    match_explanation = re.search(explanation_pattern, output, re.IGNORECASE)
    match_confusion_reason = re.search(confusion_reason_pattern, output, re.IGNORECASE)
    match_error_type = re.search(error_type_pattern, output, re.IGNORECASE)
    match_top_3_classes = re.search(top_3_classes_pattern, output, re.IGNORECASE)
    match_evidence_span = re.search(evidence_span_pattern, output, re.IGNORECASE)
    
    correctness = match_correctness.group(1) if match_correctness else None
    explanation = match_explanation.group(1) if match_explanation else None
    confusion_reason = match_confusion_reason.group(1) if match_confusion_reason else None
    error_type = match_error_type.group(1) if match_error_type else None
    top_3_classes = match_top_3_classes.group(1) if match_top_3_classes else None
    evidence_span = match_evidence_span.group(1) if match_evidence_span else None
    
    return correctness, explanation, confusion_reason, error_type, top_3_classes, evidence_span

def output_parser(response: str, row_index: int) -> dict:
    correctness, explanation, confusion_reason, error_type, top_3_classes, evidence_span = find_attributes(response)
    return {
        "correctness": correctness,
        "explanation": explanation,
        "confusion_reason": confusion_reason,
        "error_type": error_type,
        "top_3_classes": top_3_classes,
        "evidence_span": evidence_span
    }

def output_evaluator(dataset):
    with open("support_query_classification/evaluator.txt", "r") as file:
        evaluator_prompt = file.read()

    eval_model = OpenAIModel(
        model="gpt-4.1-2025-04-14",
        model_kwargs={
            "response_format": {"type": "json_object"},
            "temperature": 0
        }
    )

    evaluation_results = llm_generate(
        dataframe=dataset,
        template=evaluator_prompt,
        model=eval_model,
        output_parser=output_parser,
        concurrency=40,
        verbose=True
    )

    dataset = dataset.copy()
    feedback_columns = ["correctness", "explanation", "confusion_reason", "error_type", "top_3_classes", "evidence_span"]
    for col in feedback_columns:
        if col in evaluation_results.columns:
            dataset[col] = evaluation_results[col]

    return dataset, feedback_columns



from sklearn.metrics import f1_score, precision_score, recall_score, accuracy_score

def compute_metric(y_pred, y_true, scorer="accuracy", average="macro"):
    """
    Compute the requested metric for multiclass classification.
    """
    if scorer == "accuracy":
        return accuracy_score(y_true, y_pred)
    elif scorer == "f1":
        return f1_score(y_true, y_pred, zero_division=0, average=average)
    elif scorer == "precision":
        return precision_score(y_true, y_pred, zero_division=0, average=average)
    elif scorer == "recall":
        return recall_score(y_true, y_pred, zero_division=0, average=average)
    else:
        raise ValueError(f"Unknown scorer: {scorer}")

from optimizer_sdk.prompt_learning_optimizer import PromptLearningOptimizer

def optimize_loop(
    train_set,
    test_set,
    system_prompt,
    evaluators,
    threshold=1,
    loops=5,
    scorer="accuracy",
):
    """
    scorer: one of "accuracy", "f1", "precision", "recall"
    threshold: float, threshold for the selected metric
    """
    import copy
    curr_loop = 1
    train_metrics = []
    test_metrics = []
    prompts = []
    raw_dfs = []

    print(f"🚀 Starting prompt optimization with {loops} iterations (scorer: {scorer}, threshold: {threshold})")
    
    print(f"📊 Initial evaluation:")
    test_set["output"] = generate_output(test_set, system_prompt)
    initial_metric_value = compute_metric(test_set["output"], test_set["category"], scorer)
    print(f"✅ Initial {scorer}: {initial_metric_value}")

    test_metrics.append(initial_metric_value)
    prompts.append(system_prompt)
    raw_dfs.append(copy.deepcopy(test_set))

    if initial_metric_value >= threshold:
        print("🎉 Initial prompt already meets threshold!")
        return {
            "train": train_metrics,
            "test": test_metrics,
            "prompt": prompts,
            "raw": raw_dfs
        }
    
    # Initialize all feedback columns
    feedback_columns = ["correctness", "explanation", "confusion_reason", "error_type", "top_3_classes", "evidence_span"]
    for col in feedback_columns:
        train_set[col] = [None for _ in range(len(train_set))]
    
    while loops > 0:
        print(f"📊 Loop {curr_loop}: Optimizing prompt...")
        train_set["output"] = generate_output(train_set, system_prompt)

        optimizer = PromptLearningOptimizer(
            prompt=system_prompt,
            model_choice="gpt-4o",
            openai_api_key=os.getenv("OPENAI_API_KEY")
        )

        train_set, _ = optimizer.run_evaluators(
            train_set,
            evaluators,
            feedback_columns=feedback_columns
        )

        with open("annotations_prompt.txt", "r") as file:
            annotations_prompt = file.read()
            annotation = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": annotations_prompt},
                    {"role": "user", "content": system_prompt}
                ]
            )

        system_prompt = optimizer.optimize(
            train_set,
            "output",
            feedback_columns=feedback_columns,
            context_size_k=90000
        )

        train_metric_post_value = compute_metric(train_set["output"], train_set["category"], scorer)
        train_metrics.append(train_metric_post_value)
        print(f"✅ Train {scorer}: {train_metric_post_value}")

        test_set["output"] = generate_output(test_set, system_prompt)
        test_metric_post_value = compute_metric(test_set["output"], test_set["category"], scorer)
        test_metrics.append(test_metric_post_value)
        print(f"✅ Test {scorer}: {test_metric_post_value}")

        if test_metric_post_value >= threshold:
            print("🎉 Prompt optimization met threshold!")
            break

        loops -= 1
        curr_loop += 1

        with open(f"support_query_classification/system_prompts/system_prompt_{curr_loop}.txt", "w") as file:
            file.write(system_prompt)

    return train_metrics, test_metrics, prompts, raw_dfs


evaluators = [output_evaluator]
result = optimize_loop(train_set, test_set, system_prompt, evaluators, loops=5, scorer="accuracy")
print(result)
