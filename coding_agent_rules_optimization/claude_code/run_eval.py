import sys
import pandas as pd
import subprocess
from swebench.harness.utils import load_swebench_dataset
from pathlib import Path
import json


dataset_name = "SWE-bench/SWE-bench_Lite"
combined_preds = "/var/folders/_w/glgvmwgs3s5g81607b0x435c0000gn/T/claude_preds_test_2.jsonl"
print(f"\nRunning SWE-bench evaluator...")
cmd = [
    sys.executable,
    "-m",
    "swebench.harness.run_evaluation",
    "--dataset_name",
    dataset_name,
    "--split",
    "test",
    "--predictions_path",
    str(combined_preds),
    "--run_id",
    "test_2",
    "--namespace", "none",
    "--max_workers",
    "50",
]

test_df = pd.read_csv("claude_code_results/test_results_2.csv")
selected_ids = [instance_id for instance_id in test_df["instance_id"]]
dataset = load_swebench_dataset(dataset_name, "test", selected_ids)
dataset = [inst for inst in dataset if inst["instance_id"] in selected_ids]

# Restrict evaluation strictly to the selected subset
if selected_ids:
    cmd += ["--instance_ids", *selected_ids]

try:
    subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print(f"Warning: Evaluation failed with error: {e}")

# Build results DataFrame
by_id = {inst["instance_id"]: inst for inst in dataset}
rows: list[dict] = []
for iid in selected_ids:
    coding_agent_patch = test_df.loc[test_df['instance_id'] == iid, 'coding_agent_patch'].iloc[0]

    # Look for evaluation report (uses namespace)
    report_path = Path("logs").joinpath("run_evaluation", "test_2", "claude-code", iid, "report.json")
    pass_or_fail = "fail"
    if report_path.exists():
        try:
            data = json.loads(report_path.read_text(encoding="utf-8"))
            resolved = bool((data.get(iid) or {}).get("resolved"))
            pass_or_fail = "pass" if resolved else "fail"
        except Exception:
            pass_or_fail = "fail"
    
    inst = by_id[iid]
    rows.append({
        "instance_id": iid,
        "problem_statement": inst.get("problem_statement", ""),
        "ground_truth_patch": inst.get("patch", ""),
        "test_patch": inst.get("test_patch", ""),
        "coding_agent_patch": coding_agent_patch,
        "pass_or_fail": pass_or_fail,
    })

df = pd.DataFrame(rows)

df.to_csv("claude_code_results/test_results_2_corrected.csv", index=False)