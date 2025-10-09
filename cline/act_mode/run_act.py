import argparse
import json
import os
import socket
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd
from swebench.harness.utils import load_swebench_dataset
from swebench.harness.test_spec.test_spec import make_test_spec
from swebench.harness.docker_build import build_env_images, build_container, setup_logger, close_logger
from swebench.harness.docker_utils import cleanup_container
import docker

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from cline_helpers import run_cline_for_instance
from constants import CLINE_REPO_PATH, MATERIALIZED_REPOS_PATH

cline_repo = Path(CLINE_REPO_PATH)
workspaces_root = Path(MATERIALIZED_REPOS_PATH)

def act_one(instance: dict, idx: int, ruleset: str) -> tuple[str, Path]:
    instance_id = instance["instance_id"]
    image_tag = make_test_spec(instance).instance_image_key

    # unique ports per job (avoid clashes)
    base = 27000 + idx * 10
    proto_port = base + 1
    hostbridge_port = base + 2
    
    ruleset += """\nApply changes directly to repository files. Do not create fix/ or patch files; modify code in place.
    """
    
    res = run_cline_for_instance(
        instance_id=instance_id,
        image_tag=image_tag,
        cline_repo=cline_repo,
        workspaces_root=workspaces_root,
        task_text=instance["problem_statement"],
        host="127.0.0.1",
        proto_port=proto_port,
        hostbridge_port=hostbridge_port,
        mode="act",
        wait_seconds=100,
        ruleset_text=ruleset,
    )
    return instance_id, Path(res["predictions_path"])  # type: ignore

def run_act(
    dataset_name: str = "SWE-bench/SWE-bench_Lite",
    instance_ids: list[str] | None = None,
    run_id: str = "",
    ruleset: str = "",
    workers: int = 16,
    count: int | None = None, # number of instances to run
) -> pd.DataFrame:
    assert run_id, "run_id is required"
    dataset = load_swebench_dataset(dataset_name, "test", instance_ids)
    if not dataset:
        print("No instances found.")
        return

    import random
    # Run Cline ACT across instances in parallel -> collect predictions
    predictions_by_id: dict[str, Path] = {}
    if count:
        dataset = random.sample(dataset, count)
        selected_ids = [inst["instance_id"] for inst in dataset]
    elif instance_ids:
        dataset = [inst for inst in dataset if inst["instance_id"] in instance_ids]
        selected_ids = instance_ids
    else:
        selected_ids = [inst["instance_id"] for inst in dataset]

    
    
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(act_one, inst, i, ruleset): inst for i, inst in enumerate(dataset)}
        for f in as_completed(futures):
            iid, p = f.result()
            predictions_by_id[iid] = p

    for key, item in predictions_by_id.items():
        print(key, item)

    # Combine predictions into one JSONL
    combined_preds = Path(os.getenv("TMPDIR", "/tmp")).joinpath(f"cline_preds_{run_id}.jsonl")
    with combined_preds.open("w", encoding="utf-8") as out:
        for p in predictions_by_id.values():
            content = Path(p).read_text(encoding="utf-8")
            out.write(content)
            if not content.endswith("\n"):
                out.write("\n")

    subprocess.run([
        "/opt/anaconda3/envs/cline/bin/python3",
        "-m",
        "pip",
        "install",
        "--upgrade",
        "swebench",
        "requests",
    ])

    # Run official evaluator
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
        run_id,
        "--namespace", "none",
        "--max_workers",
        str(workers),
    ]
    # Restrict evaluation strictly to the selected subset
    if selected_ids:
        cmd += ["--instance_ids", *selected_ids]
    subprocess.run(cmd, check=True)

    by_id = {inst["instance_id"]: inst for inst in dataset}
    rows: list[dict] = []
    for iid in selected_ids:
        inst = by_id[iid]
        cline_patch = ""
        pred_path = predictions_by_id.get(iid)
        if pred_path and pred_path.exists():
            try:
                line = pred_path.read_text(encoding="utf-8").splitlines()[0]
                obj = json.loads(line)
                cline_patch = obj.get("model_patch", "")
            except Exception:
                cline_patch = ""
        report_path = Path("logs").joinpath("run_evaluation", run_id, "cline", iid, "report.json")
        result = "fail"
        if report_path.exists():
            data = json.loads(report_path.read_text(encoding="utf-8"))
            resolved = bool((data.get(iid) or {}).get("resolved"))
            result = "pass" if resolved else "fail"
        rows.append({
            "instance_id": iid,
            "problem_statement": inst.get("problem_statement", ""),
            "patch": inst.get("patch", ""),
            "test_patch": inst.get("test_patch", ""),
            "cline_patch": cline_patch,
            "pass_or_fail": result,
        })
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    rows = run_act(
        run_id="act_sympy_14308",
        # count=1,
        instance_ids=["sympy__sympy-14308"],
    )
    rows.to_csv("14308.csv", index=False)
    




