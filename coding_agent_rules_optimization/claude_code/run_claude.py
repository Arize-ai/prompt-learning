import argparse
import json
import os
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import pandas as pd
from swebench.harness.utils import load_swebench_dataset
from swebench.harness.test_spec.test_spec import make_test_spec
import random

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from claude_code_helpers import run_claude_for_instance
from constants import MATERIALIZED_REPOS_PATH

workspaces_root = Path(MATERIALIZED_REPOS_PATH)


def claude_one(
    instance: dict,
    idx: int,
    ruleset: str,
    wait_seconds: int = 300,
    model_name: str = "claude-sonnet-4-5",
) -> tuple[str, Path | None, dict]:
    """
    Runs Claude Code for one instance of SWE-bench and returns the path to the patch Claude generated.

    Args:
        instance: SWE-bench instance dictionary
        idx: Index for unique workspace naming
        ruleset: Ruleset text to append to system prompt
        wait_seconds: Maximum time to wait for Claude to complete

    Returns:
        Tuple of (instance_id, predictions_path, metadata_dict)
    """
    import time

    instance_id = instance["instance_id"]
    image_tag = make_test_spec(instance).instance_image_key

    # Create unique workspace for this instance
    workspace = workspaces_root / instance_id.lower()

    start_time = time.time()
    res = run_claude_for_instance(
        instance_id=instance_id,
        image_tag=image_tag,
        workspace=workspace,
        task_text=instance["problem_statement"],
        wait_seconds=wait_seconds,
        ruleset_text=ruleset,
        model_name=model_name,
    )
    elapsed_time = time.time() - start_time

    predictions_path = res.get("predictions_path", "")
    metadata = {
        "timeout": res.get("timeout", False),
        "failure": res.get("failure", False),
        "error": res.get("error", ""),
        "stdout": res.get("stdout", ""),
        "stderr": res.get("stderr", ""),
        "time_taken_seconds": elapsed_time,
    }

    if not predictions_path or res.get("failure"):
        # Return empty path if failed
        print(f"⚠ Warning: {instance_id} failed - {res.get('error', 'Unknown error')}")

    return instance_id, Path(predictions_path) if predictions_path else None, metadata


def run_claude(
    run_id: str,
    dataset_name: str = "SWE-bench/SWE-bench_Lite",
    instance_ids: list[str] | None = None,
    ruleset: str = "",
    workers: int = 4,  # Lower default than Cline since Claude Code is simpler
    count: int | None = None,
    wait_seconds: int = 600,
    model_name: str = "claude-sonnet-4-5",
) -> pd.DataFrame:
    """
    Runs Claude Code on a SWE-bench dataset.

    Args:
        run_id: The ID of the run. Make sure it's unique to avoid reusing previous results.
        dataset_name: The name of the dataset to run Claude on.
        instance_ids: The IDs of the instances to run Claude on. None means all instances.
        ruleset: The ruleset to append to Claude's system prompt.
        workers: The level of concurrency. Configure based on your machine and API rate limits.
        count: Number of instances to run (random subset if specified).
        wait_seconds: Maximum seconds to wait per instance (timeout).

    This function triggers Claude Code runs in parallel, then uses the SWE-bench evaluator
    to run unit tests for each instance, testing Claude's generated patches.

    Returns:
        A pandas DataFrame with the results of the run.
    """
    dataset = load_swebench_dataset(dataset_name, "test", instance_ids)
    if not dataset:
        print("No instances found.")
        return pd.DataFrame()

    # Select the instances to run Claude on
    predictions_by_id: dict[str, Path] = {}
    if count:
        dataset = random.sample(dataset, count)
        selected_ids = [inst["instance_id"] for inst in dataset]
    elif instance_ids:
        dataset = [inst for inst in dataset if inst["instance_id"] in instance_ids]
        selected_ids = instance_ids
    else:
        selected_ids = [inst["instance_id"] for inst in dataset]

    print(
        f"Running Claude Code on {len(selected_ids)} instances with {workers} workers..."
    )

    # Run Claude Code across instances in parallel -> collect predictions
    # Also track metadata about each run
    run_metadata: dict[str, dict] = {}

    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {
            ex.submit(claude_one, inst, i, ruleset, wait_seconds, model_name): inst
            for i, inst in enumerate(dataset)
        }
        for f in as_completed(futures):
            try:
                result = f.result()
                if result is None:
                    inst = futures[f]
                    print(f"✗ Failed: {inst['instance_id']} - returned None")
                    continue

                iid, p, metadata = result  # type: ignore

                # Store metadata for later analysis
                run_metadata[iid] = metadata

                if p is not None:
                    predictions_by_id[iid] = p
                    if metadata["timeout"]:
                        print(f"⏱ Timeout: {iid}")
                    else:
                        print(
                            f"✓ Completed: {iid} (took {metadata.get('time_taken_seconds', 0):.1f}s)"
                        )
                else:
                    print(f"✗ Failed: {iid}")
                    if metadata.get("error"):
                        print(f"  Error: {metadata['error']}")
            except Exception as e:
                inst = futures[f]
                print(f"✗ Exception for {inst['instance_id']}: {e}")

    # Combine predictions into one JSONL
    combined_preds = Path(os.getenv("TMPDIR", "/tmp")).joinpath(
        f"claude_preds_{run_id}.jsonl"
    )
    with combined_preds.open("w", encoding="utf-8") as out:
        for iid in selected_ids:
            p = predictions_by_id.get(iid)
            if p and p.exists():
                content = Path(p).read_text(encoding="utf-8")
                out.write(content)
                if not content.endswith("\n"):
                    out.write("\n")
            else:
                # Write empty prediction for failed instances
                empty_pred = {
                    "instance_id": iid,
                    "model_name_or_path": "claude-code",
                    "model_patch": "",
                }
                out.write(json.dumps(empty_pred) + "\n")

    print(f"\nCombined predictions written to: {combined_preds}")

    # Run official SWE-bench evaluator
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
        run_id,
        "--namespace",
        "none",
        "--max_workers",
        str(workers),
    ]
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
        inst = by_id[iid]
        claude_patch = ""
        pred_path = predictions_by_id.get(iid)
        if pred_path and pred_path.exists():
            try:
                line = pred_path.read_text(encoding="utf-8").splitlines()[0]
                obj = json.loads(line)
                claude_patch = obj.get("model_patch", "")
            except Exception:
                claude_patch = ""

        # Look for evaluation report (uses namespace)
        report_path = Path("logs").joinpath(
            "run_evaluation", run_id, "claude-code", iid, "report.json"
        )
        pass_or_fail = "fail"
        if report_path.exists():
            try:
                data = json.loads(report_path.read_text(encoding="utf-8"))
                resolved = bool((data.get(iid) or {}).get("resolved"))
                pass_or_fail = "pass" if resolved else "fail"
            except Exception:
                pass_or_fail = "fail"

        # Get timing from metadata
        meta = run_metadata.get(iid, {})
        time_taken = meta.get("time_taken_seconds", 0)

        rows.append(
            {
                "instance_id": iid,
                "problem_statement": inst.get("problem_statement", ""),
                "ground_truth_patch": inst.get("patch", ""),
                "test_patch": inst.get("test_patch", ""),
                "coding_agent_patch": claude_patch,
                "pass_or_fail": pass_or_fail,
                "time_taken_seconds": time_taken,
            }
        )

    df = pd.DataFrame(rows)

    # Print summary
    if not df.empty:
        total = len(df)
        passed = len(df[df["pass_or_fail"] == "pass"])
        print(f"\n{'='*60}")
        print(f"Results Summary:")
        print(f"  Total instances: {total}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {total - passed}")
        print(f"  Pass rate: {passed/total*100:.1f}%")

        # Show timeout information
        timeouts = [iid for iid, meta in run_metadata.items() if meta.get("timeout")]
        if timeouts:
            print(f"\n  Timeouts: {len(timeouts)}")
            for iid in timeouts:
                patch_len = (
                    len(str(df[df["instance_id"] == iid]["coding_agent_patch"].iloc[0]))
                    if iid in df["instance_id"].values
                    else 0
                )
                print(f"    ⏱ {iid} (patch: {patch_len} chars)")

        # Show instances with empty patches
        empty_patches = df[
            df["coding_agent_patch"].apply(lambda x: len(str(x).strip()) == 0)
        ]
        if not empty_patches.empty:
            print(f"\n  Empty patches: {len(empty_patches)}")
            for _, row in empty_patches.iterrows():
                iid = row["instance_id"]
                meta = run_metadata.get(iid, {})
                time_taken = meta.get("time_taken_seconds", 0)
                reason = "timeout" if meta.get("timeout") else "no changes made"
                print(f"    ∅ {iid} ({reason}, took {time_taken:.1f}s)")

                # If it completed very quickly (< 10s), show debug info
                if time_taken < 10 and not meta.get("timeout"):
                    print(f"      [Quick completion - possible issue]")
                    if meta.get("stdout"):
                        preview = meta["stdout"][:200].replace("\n", " ")
                        print(f"      Stdout: {preview}...")
                    if meta.get("stderr"):
                        preview = meta["stderr"][:200].replace("\n", " ")
                        print(f"      Stderr: {preview}...")
                    if meta.get("returncode") != 0:
                        print(f"      Exit code: {meta.get('returncode')}")

        print(f"{'='*60}\n")

    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Claude Code on SWE-bench")
    parser.add_argument("--run_id", type=str, required=True, help="Unique run ID")
    parser.add_argument(
        "--dataset", type=str, default="SWE-bench/SWE-bench_Lite", help="Dataset name"
    )
    parser.add_argument(
        "--instance_ids", nargs="+", help="Specific instance IDs to run"
    )
    parser.add_argument(
        "--ruleset", type=str, default="", help="Ruleset text file path"
    )
    parser.add_argument(
        "--workers", type=int, default=4, help="Number of parallel workers"
    )
    parser.add_argument("--count", type=int, help="Number of random instances to run")
    parser.add_argument(
        "--wait_seconds", type=int, default=300, help="Timeout per instance"
    )
    parser.add_argument("--output", type=str, help="Output CSV file path")

    args = parser.parse_args()

    # Load ruleset if provided
    ruleset_text = ""
    if args.ruleset and Path(args.ruleset).exists():
        ruleset_text = Path(args.ruleset).read_text()
        print(f"Loaded ruleset from: {args.ruleset}")

    # Run Claude
    df = run_claude(
        run_id=args.run_id,
        dataset_name=args.dataset,
        instance_ids=args.instance_ids,
        ruleset=ruleset_text,
        workers=args.workers,
        count=args.count,
        wait_seconds=args.wait_seconds,
    )

    # Save results
    output_path = args.output or f"claude_results_{args.run_id}.csv"
    df.to_csv(output_path, index=False)
    print(f"Results saved to: {output_path}")
