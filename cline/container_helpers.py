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


def materialize_repo_from_image(image_tag: str, workspace_dir: Path) -> None:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    # Skip if workspace not empty
    if any(workspace_dir.iterdir()):
        return
    cid = sh(f"docker create {image_tag}").strip()
    try:
        sh(f"docker cp {cid}:/testbed/. {str(workspace_dir)}")
    finally:
        subprocess.run(f"docker rm {cid}", shell=True, check=False, capture_output=True)


 


def copy_text_to_container(instance_id: str, content: str, dst_path: str) -> None:
    name = container_name_for(instance_id)
    with tempfile.NamedTemporaryFile("w", delete=False) as tf:
        tf.write(content)
        tf.flush()
        sh(f"docker cp {tf.name} {name}:{dst_path}")


def exec_in_container(instance_id: str, cmd: str, timeout=None) -> str:
    name = container_name_for(instance_id)
    # capture stdout+stderr
    return sh(f"docker exec {name} bash -lc {json.dumps(cmd + ' 2>&1')}", timeout=timeout)

def ensure_workspace_materialized(image_tag: str, workspace_dir: Path) -> None:
    workspace_dir.mkdir(parents=True, exist_ok=True)
    if any(workspace_dir.iterdir()):
        return
    materialize_repo_from_image(image_tag, workspace_dir)

def build_and_copy_eval_script(instance_id: str, instance: dict) -> None:
    spec = make_test_spec(instance)
    eval_script = spec.eval_script
    copy_text_to_container(instance_id, eval_script, "/eval.sh")

def copy_log_to_host(instance_id: str, container_log: str = "/testbed/_eval_output.txt") -> Path:
    name = container_name_for(instance_id)
    host_log = Path(tempfile.mkstemp(prefix="swe_eval_", suffix=".txt")[1])
    subprocess.run(f"docker cp {name}:{container_log} {host_log}", shell=True, check=True)
    return host_log

def sanitize_log_to_utf8(host_log_path: Path) -> Path:
    data = host_log_path.read_bytes()
    text = data.decode("utf-8", errors="replace")
    clean_path = Path(tempfile.mkstemp(prefix="swe_eval_utf8_", suffix=".txt")[1])
    clean_path.write_text(text, encoding="utf-8")
    return clean_path

def grade_run(instance: dict, host_log_path: Path) -> dict:
    spec = make_test_spec(instance)
    pred = {
        "instance_id": instance["instance_id"],
        "model_name_or_path": "cline",
        "model_patch": "",
    }
    report = get_eval_report(
        test_spec=spec,
        prediction=pred,
        test_log_path=host_log_path,
        include_tests_status=True,
    )
    return report[instance["instance_id"]]

def run_tests(instance: dict, image_tag: str, workspaces_root: Path) -> str:
    
    instance_id = instance["instance_id"]
    ws = workspaces_root / instance_id.lower()

    # ensure_workspace_materialized(image_tag, ws)
    # stop_container(instance_id)
    # start_bound_container(image_tag, instance_id, ws)

    # reset_repo_in_container(instance_id, instance)  # uses make_test_spec(instance).language
    build_and_copy_eval_script(instance_id, instance)

    # capture stdout+stderr, tee to file, and emit exit code marker
    cmd = r"""/bin/bash -lc 'set -o pipefail; /bin/bash /eval.sh 2>&1 | tee /testbed/_eval_output.txt; ec=${PIPESTATUS[0]}; echo "<<<EXIT_CODE:${ec}>>>"'"""
    try:
        out = exec_in_container(instance_id, cmd, timeout=300)
        return out
    except subprocess.TimeoutExpired:
        return "failed"





def pass_or_fail(out: str) -> bool:
    if "failed".lower() in out.lower() or "fail".lower() in out.lower():
        return False
    else:   
        return True

def reset_repo_in_container(instance_id: str, instance: dict) -> None:
    lang = make_test_spec(instance).language
    base_commit = instance["base_commit"]
    repo_hint = instance.get("repo_url") or instance.get("repo") or ""
    if repo_hint and not repo_hint.startswith("http"):
        repo_url = f"https://github.com/{repo_hint}.git"
    else:
        repo_url = repo_hint or ""
    cmds = [
        "source /opt/miniconda3/bin/activate && conda activate testbed",
        "cd /testbed",
        # Ensure git discovery works across the bind mount boundary and repo is initialized
        "export GIT_DISCOVERY_ACROSS_FILESYSTEM=1",
        # Initialize or repair repo structure so subsequent git commands succeed
        "git init",
        # Avoid dubious ownership errors inside container bind mounts
        "git config --global --add safe.directory /testbed",
    ]
    if repo_url:
        cmds.extend([
            # Ensure origin exists and points to the right URL
            f"(git remote remove origin || true) && git remote add origin {repo_url}",
            # Fetch the base commit object explicitly, shallowly
            f"git fetch --force --depth=1 origin {base_commit}",
        ])
    cmds.extend([
        f"git checkout -f {base_commit}",
        "git clean -xfd",
    ])
    if lang == "py":
        cmds.append("python -m pip install \"setuptools<70\"")
        cmds.append("python -m pip install extension-helpers")
        cmds.append("python -m pip install \"Cython<3\"")
        cmds.append("(python -m pip install -e .) || (python -m pip install .) || (python -m pip install flit-core && python -m pip install -e . --no-build-isolation)")
    exec_in_container(instance_id, " && ".join(cmds))


def run_tests_for_row(
    instance_id: str,
    instance: dict,
) -> str:
    """
    Uses the official dataset to fetch the precise instance dict by instance_id,
    then builds the eval script and runs it inside the container.
    Requires row to provide at least: instance_id, local_image_tag.
    """

    # Fetch the ground-truth instance record (correct version, test directives, etc.)
    
    # Build eval script from the official instance (includes applying test_patch)
    spec = make_test_spec(instance)
    eval_script = spec.eval_script

    copy_text_to_container(instance_id, eval_script, "/eval.sh")
    return exec_in_container(instance_id, "/bin/bash /eval.sh")