from phoenix.evals import create_evaluator
from phoenix.evals.llm import LLM
import re
import string
from collections import Counter


def normalize_answer(s):
    """Normalize answer string: lowercase, remove articles, remove punctuation, fix whitespace."""
    # Remove articles
    s = re.sub(r"\b(a|an|the)\b", " ", s)
    # Remove punctuation
    s = "".join(ch if ch not in string.punctuation else " " for ch in s)
    # Fix whitespace and lowercase
    return " ".join(s.lower().split())


def exact_match(prediction, gold):
    """Returns 1.0 if answers match exactly (after normalization), else 0.0."""
    return 1.0 if normalize_answer(prediction) == normalize_answer(gold) else 0.0


def compute_f1(prediction, gold):
    """Compute F1, precision, recall at token level."""
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()

    # Count common tokens
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_common = sum(common.values())

    # Edge cases
    if num_common == 0:
        return 0.0, 0.0, 0.0
    if len(pred_tokens) == 0 or len(gold_tokens) == 0:
        return 0.0, 0.0, 0.0

    # Compute metrics
    precision = num_common / len(pred_tokens)
    recall = num_common / len(gold_tokens)
    f1 = (2 * precision * recall) / (precision + recall)

    return f1, precision, recall


# Initialize the LLM once (reused across evaluations)
llm = LLM(provider="openai", model="gpt-4.1-mini")

EVALUATION_PROMPT = """You are an expert at analyzing question-answering system outputs. Given a question, the gold (correct) answer, and a predicted answer, analyze what went wrong and explain it in terms of precision and recall.

## Definitions:
- **Precision**: What percentage of the predicted answer is correct/relevant
- **Recall**: What percentage of the gold answer was captured in the prediction
- **High Precision, High Recall**: Perfect answer
- **Low Precision, High Recall**: Answer is too verbose - includes correct info plus lots of extra/wrong text
- **High Precision, Low Recall**: Answer is too brief - what's there is correct but incomplete
- **Low Precision, Low Recall**: Answer is mostly wrong

## Input:
**Question**: {question}

**Context**: 
{summary_1}
{summary_2}

**Gold Answer**: {gold_answer}

**Predicted Answer**: {predicted_answer}

**Metrics**:
- Exact Match: {exact_match} (1.0 = perfect, 0.0 = wrong)
- F1 Score: {f1_score}
- Precision: {precision}
- Recall: {recall}

## Task:
Analyze this prediction and provide:

1. **What went wrong**: Describe the error in plain language
2. **Precision/Recall analysis**: 
   - Is precision higher or lower? What does this mean?
   - Is recall higher or lower? What does this mean?
3. **Token-level breakdown**: 
   - What tokens/words were correct?
   - What tokens/words were extra (hurt precision)?
   - What tokens/words were missing (hurt recall)?
4. **Root cause**: Why did the model make this error?
5. **Fix suggestion**: How to improve this specific type of error

Be specific and actionable. Focus on helping improve the system.

## Analysis:"""


@create_evaluator(name="final_answer_analysis", source="llm")
def evaluator(input, output, expected):
    gold_answer = expected["gold_answer"]
    exact_match_score = exact_match(output, gold_answer)
    f1_score, precision, recall = compute_f1(output, gold_answer)

    prompt = (
        EVALUATION_PROMPT.replace("{question}", input["question"])
        .replace("{summary_1}", input["summary_1"])
        .replace("{summary_2}", input["summary_2"])
        .replace("{gold_answer}", gold_answer)
        .replace("{predicted_answer}", output)
        .replace("{exact_match}", str(exact_match_score))
        .replace("{f1_score}", str(f1_score))
        .replace("{precision}", str(precision))
        .replace("{recall}", str(recall))
    )

    explanation = llm.generate_text(prompt=prompt)
    explanation = (
        f"""
    f1_score: {f1_score}
    precision: {precision}
    recall: {recall}
    exact_match: {exact_match_score}
    """
        + explanation
    )

    return {"score": f1_score, "explanation": explanation}
