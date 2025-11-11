import sys, json
import pandas as pd
from phoenix.evals import OpenAIModel, llm_generate
import os
import numpy as np

EVAL_PROMPT = """
You are evaluating a **multi-hop claim verification system** designed for the HoVer dataset. 
The system determines whether a factual claim is **SUPPORTED**, **REFUTED**, or **NOT ENOUGH INFO** based on evidence retrieved from Wikipedia.

=====================
🟩 INPUT CLAIM
{claim}

=====================
🟦 STEP 1 — FIRST QUERY & PASSAGES
Query #1:
{query_1}

Retrieved Passages (Hop 1):
{passages_1}

Summary #1 (based on the claim and the first set of passages):
{summary_1}

=====================
🟪 STEP 2 — SECOND QUERY & PASSAGES
Query #2:
{query_2}

Retrieved Passages (Hop 2):
{passages_2}

Summary #2 (based on the claim, previous summaries, and passages):
{summary_2}

=====================
🟫 STEP 3 — THIRD QUERY & PASSAGES
Query #3:
{query_3}

Retrieved Passages (Hop 3):
{passages_3}

Summary #3 (based on the claim, previous summaries, and passages):
{summary_3}

=====================
🟨 FINAL VERDICT
{final_answer}

=====================
🟥 GROUND TRUTH
Ground Truth Wikipedia titles: {ground_truth_wikipedia_titles}
Ground Truth Label (SUPPORTED / NOT_SUPPORTED / NOT_ENOUGH_INFO): {ground_truth_label}
Correctness of the final verdict: {correctness}

=====================
🧠 EVALUATION TASK

Your task is to analyze the **entire reasoning and retrieval chain** to assess the reasoning quality, and faithfulness of the model’s decision. 
Provide **structured, diagnostic feedback** that helps improve the system’s prompts and reasoning.

Please:

1. **Assess Correctness**
   - Does the final answer (SUPPORTED / NOT_SUPPORTED / NOT_ENOUGH_INFO) match the ground truth label?
   - Were the correct supporting documents retrieved and used?

2. **Evaluate Reasoning Quality**
   - Did the model logically connect the retrieved evidence across all hops?
   - Did the summaries faithfully reflect the passages and support the correct verdict?

3. **Identify Failure Points**
   - If the system is incorrect or uncertain, determine *which stage* caused the issue:
     - **Query Generation:** missing entities, ambiguous phrasing, irrelevant focus
     - **Retrieval:** lack of recall or precision (even though retrieval itself is static)
     - **Summarization:** omitted critical facts, introduced hallucinations, or distorted relationships
     - **Final Answer Generation:** misinterpreted summaries, ignored key evidence, or over/under-stated confidence

4. **Propose Actionable Improvements**
   - Provide concise, constructive suggestions for each component to improve future performance.
   - Focus especially on improving query precision/recall and reasoning faithfulness across hops.

=====================
🧾 OUTPUT FORMAT

Return your evaluation strictly in this JSON-like format (no markdown, no extra text):

"explanation": "<a detailed, structured analysis of why the system was correct or incorrect, highlighting reasoning quality and factual grounding>",
"suggestions": "<specific, actionable improvement ideas for each component—query generation, retrieval, summaries, and verdict synthesis>"
"""

def compute_attach_correctness(df: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    accuracy = (df["final_answer"] == df["ground_truth_label"]).mean()
    df["correctness"] = np.where(df["final_answer"] == df["ground_truth_label"], "correct", "incorrect")
    return df, accuracy

def attach_evals(df: pd.DataFrame) -> pd.DataFrame:
    model = OpenAIModel(
        model="gpt-4.1",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    evals = llm_generate(
        dataframe=df,
        template=EVAL_PROMPT,
        model=model
    )
    df["evaluation"] = evals["output"]
    return df


