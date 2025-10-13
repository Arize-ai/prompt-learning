import json
import subprocess
import tempfile
from pathlib import Path
import shlex
import re

import pandas as pd

# pip install -e . from SWE-bench repo first
from swebench.harness.test_spec.test_spec import make_test_spec
from swebench.harness.utils import load_swebench_dataset
from swebench.harness.grading import get_eval_report



def sh(cmd: str, timeout=None) -> str:
    p = subprocess.run(
        cmd,
        shell=True,
        text=True,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )
    if p.returncode != 0:
        raise RuntimeError(f"{cmd}\n{p.stderr}\n{p.stdout}")
    return p.stdout


def container_name_for(instance_id: str) -> str:
    return f"sweb_{instance_id.lower()}"


def start_bound_container(image_tag: str, instance_id: str, workspace_dir: Path) -> None:
    name = container_name_for(instance_id)
    sh(
        f"docker run -d --rm --name {name} "
        f"-w /testbed -v {str(workspace_dir)}:/testbed {image_tag} tail -f /dev/null"
    )


def stop_container(instance_id: str) -> None:
    name = container_name_for(instance_id)
    subprocess.run(f"docker rm -f {name}", shell=True, check=False, capture_output=True)


def materialize_repo_from_image(image_tag: str, workspace_dir: Path, force: bool = True) -> None:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    if any(workspace_dir.iterdir()) and not force:
        return
    if force:
        for p in workspace_dir.iterdir():
            if p.is_file():
                p.unlink(missing_ok=True)
            else:
                import shutil
                shutil.rmtree(p, ignore_errors=True)
    cid = sh(f"docker create {image_tag}").strip()
    try:
        sh(f"docker cp {cid}:/testbed/. {str(workspace_dir)}")
    finally:
        subprocess.run(f"docker rm {cid}", shell=True, check=False, capture_output=True)


def ensure_git_baseline(workspace_dir: Path) -> None:
    print(f"[DEBUG] ensure_git_baseline: ws={workspace_dir}")
    try:
        sh(f"git -C {shlex.quote(str(workspace_dir))} rev-parse --is-inside-work-tree")
    except RuntimeError:
        sh(f"git -C {shlex.quote(str(workspace_dir))} init")
    has_head = True
    try:
        sh(f"git -C {shlex.quote(str(workspace_dir))} rev-parse --verify HEAD")
    except RuntimeError:
        has_head = False
    if not has_head:
        sh(f"git -C {shlex.quote(str(workspace_dir))} -c user.email=a -c user.name=a add -A")
        sh(f"git -C {shlex.quote(str(workspace_dir))} -c user.email=a -c user.name=a commit -m baseline --allow-empty")

def export_patch_from_workspace(
    instance_id: str,
    workspace: Path,
    out_predictions_path: Path | None = None,
) -> Path:
    """Create a unified diff between a pristine copy from the image and the current workspace.

    Returns path to a predictions JSONL file suitable for run_evaluation.
    """
    print(f"[DEBUG] export_patch: ws={workspace}")
    # Prefer a repo-relative diff from inside the workspace so paths apply cleanly in the harness
    # Stage all tracked/new files (respects .gitignore), diff against HEAD, then unstage.
    try:
        print("[DEBUG] staging changes for diff (excluding sqlite/db artifacts)")
        stage_cmd = " ".join([
            f"git -C {shlex.quote(str(workspace))} -c core.fileMode=false add -A -- .",
            "\":(exclude)**/*.sqlite3\"",
            "\":(exclude)**/*.sqlite\"",
            "\":(exclude)**/*.db\"",
        ])
        subprocess.run(stage_cmd, shell=True, check=False, capture_output=True, text=True)
        # Extra debugging of staged/unstaged state prior to diff
        try:
            staged = sh(f"git -C {shlex.quote(str(workspace))} diff --cached --name-only")
            print(f"[DEBUG] staged files:\n{staged}")
            unstaged = sh(f"git -C {shlex.quote(str(workspace))} diff --name-only")
            print(f"[DEBUG] unstaged files:\n{unstaged}")
        except Exception as e:
            print(f"[DEBUG] git state inspection failed: {e}")
        # Use pathspec excludes to avoid non-source artifacts
        diff_cmd = " ".join([
            f"git -C {shlex.quote(str(workspace))} -c core.fileMode=false diff --cached -- .",
            "\":(exclude)**/__pycache__/**\"",
            "\":(exclude)**/*.pyc\"",
            "\":(exclude)**/.git/**\"",
            "\":(exclude)**/.clinerules/**\"",
            "\":(exclude)**/*.egg-info/**\"",
            "\":(exclude)**/build/**\"",
            "\":(exclude)**/dist/**\"",
            "\":(exclude)**/.venv/**\"",
            "\":(exclude)**/venv/**\"",
            "\":(exclude)**/*.sqlite3\"",
            "\":(exclude)**/*.sqlite\"",
            "\":(exclude)**/*.db\"",
            "\":(exclude)**/*.html\"",
            "\":(exclude)**/*.txt\"",
            "\":(exclude)**/*.rst\"",
            "\":(exclude)**/*.md\"",
        ])
        try:
            patch_text = sh(diff_cmd)
        except RuntimeError as e:
            print(f"[DEBUG] git diff failed, emitting empty patch: {e}")
            patch_text = ""
        print(f"[DEBUG] diff bytes={len(patch_text)}")
    finally:
        # Best-effort unstage to leave workspace clean
        subprocess.run(
            f"git -C {shlex.quote(str(workspace))} reset -q",
            shell=True,
            check=False,
            capture_output=True,
            text=True,
        )

    # patch_text is already filtered via pathspec excludes above
    pred = {
        "instance_id": instance_id,
        "model_name_or_path": "cline",
        "model_patch": patch_text,
    }
    out_predictions_path = out_predictions_path or Path(tempfile.mkstemp(prefix="preds_", suffix=".jsonl")[1])
    with open(out_predictions_path, "w", encoding="utf-8") as f:
        f.write(json.dumps(pred) + "\n")
    print(f"[DEBUG] wrote predictions: {out_predictions_path}")
    return out_predictions_path

