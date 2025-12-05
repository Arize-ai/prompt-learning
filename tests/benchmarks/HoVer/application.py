import os
import json
import pandas as pd
from pathlib import Path

# Reuse the HotpotQA search utility if available at sibling level
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hotpotQA"))
from search import search

from phoenix.evals import OpenAIModel, llm_generate


def generate_output(df: pd.DataFrame, template: str) -> pd.Series:
    output_model = OpenAIModel(model="gpt-4.1-mini", temperature=1)
    outputs = llm_generate(
        dataframe=df,
        template=template,
        model=output_model,
        concurrency=40,
        verbose=True,
    )
    return outputs["output"]


def _format_passages(docs):
    if isinstance(docs, list):
        return "\n\n".join(
            [
                f"{d.get('title','')}\n{d.get('content','')}"
                for d in docs
                if isinstance(d, dict)
            ]
        )
    return str(docs)


def run_pipeline(prompts: dict, dataset: pd.DataFrame) -> pd.DataFrame:
    # Expect dataset to have a column 'claim'
    df = pd.DataFrame(
        {
            "claim": dataset["claim"],
            "uid": dataset["uid"],
            "ground_truth_label": dataset["label"],
            "ground_truth_wikipedia_titles": dataset["supporting_facts"],
        }
    )
    df.set_index("uid", inplace=True, drop=False)

    # Hop 1
    df["query_1"] = generate_output(df, prompts["create_query_1_prompt"])
    df["passages_1"] = df["query_1"].apply(lambda q: search(q, 5))
    # Format passages for summarize1: expects {passages}

    df["passages_1"] = df["passages_1"].apply(_format_passages)
    df["summary_1"] = generate_output(df, prompts["summarize_1_prompt"])

    # Hop 2
    df["query_2"] = generate_output(df, prompts["create_query_2_prompt"])
    df["passages_2"] = df["query_2"].apply(lambda q: search(q, 5))
    # summarize2 expects {claim}, {context}, {passages}
    df["passages_2"] = df["passages_2"].apply(_format_passages)
    df["summary_2"] = generate_output(df, prompts["summarize_2_prompt"])

    # Hop 3 (optional retrieve; keep minimal without summarize3)
    df["query_3"] = generate_output(df, prompts["create_query_3_prompt"])
    df["passages_3"] = df["query_3"].apply(lambda q: search(q, 5))
    df["passages_3"] = df["passages_3"].apply(_format_passages)
    df["summary_3"] = generate_output(df, prompts["summarize_3_prompt"])

    # Final label
    df["final_answer"] = generate_output(df, prompts["final_answer_prompt"])

    return df


# def main():
#     # Placeholder: load your HoVer dataset JSONL/JSON with a 'claim' field
#     # Minimal example expects a file with a list of {"id": ..., "claim": ...}
#     input_path = os.environ.get("HOVER_INPUT", "hover_dev_release_v1.1.json")
#     data = json.load(open(input_path))
#     df = pd.DataFrame(data)

#     # Sample 300 from dev set
#     df_sample = df.sample(300, random_state=42)

#     results = run_pipeline(df_sample)

#     # Only final labels required; include uid as a column in the artifact
#     preds_records = [
#         {"uid": uid, "answer_label": label}
#         for uid, label in results[["uid", "answer_label"]].itertuples(index=False)
#     ]
#     output_path = os.environ.get("HOVER_PREDICTIONS", "predictions_hover.json")
#     with open(output_path, "w") as f:
#         json.dump(preds_records, f, indent=2)

#     results.to_csv("hover_predictions_dev_300.csv", index=False)

#     print(f"Saved predictions to {output_path}")


# if __name__ == "__main__":
#     main()
