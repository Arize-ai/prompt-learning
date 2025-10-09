import argparse
import re
import json
import os
import shlex
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import cast
import shutil

from container_helpers import (
    materialize_repo_from_image,
    start_bound_container,
    stop_container,
    container_name_for,
    ensure_git_baseline,
    export_patch_from_workspace,
)

def is_port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        try:
            s.connect((host, port))
            return True
        except OSError:
            return False


def ensure_extension_symlink(cline_repo: Path) -> None:
    dist_dir = cline_repo / "dist-standalone"
    ext_link = dist_dir / "extension"
    if not ext_link.exists():
        try:
            ext_link.symlink_to(cline_repo)
        except FileExistsError:
            pass

def wait_for_grpc_ready(host: str, port: int, timeout_s: int = 60) -> None:
    start = time.time()
    while time.time() - start < timeout_s:
        if is_port_open(host, port):
            # As a stronger check, try grpcurl list if available
            if shutil_which("grpcurl") is not None:
                try:
                    subprocess.run(
                        ["grpcurl", "-plaintext", f"{host}:{port}", "list"],
                        check=True,
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL,
                    )
                    return
                except subprocess.CalledProcessError:
                    pass
            else:
                return
        time.sleep(0.5)
    raise TimeoutError(f"gRPC server not ready at {host}:{port} after {timeout_s}s")


def shutil_which(cmd: str) -> str | None:
    from shutil import which
    return which(cmd)

def kill_processes_listening_on_ports(ports: list[int]) -> None:
    for port in ports:
        try:
            out = subprocess.run(
                f"lsof -nP -iTCP:{port} -sTCP:LISTEN -t",
                shell=True,
                check=False,
                text=True,
                capture_output=True,
            ).stdout.strip()
            if not out:
                continue
            pids = {pid for pid in out.splitlines() if pid.isdigit()}
            for pid in pids:
                subprocess.run(f"kill -9 {pid}", shell=True, check=False)
        except Exception:
            pass


def per_job_state_dir(proto_port: int) -> Path:
    """Return the cline state directory used by the server and readers.

    Uses CLINE_DIR_BASE if set, otherwise falls back to TMPDIR or /tmp.
    """
    base = cast(str, os.environ.get("CLINE_DIR_BASE") or os.environ.get("TMPDIR") or "/tmp")
    return Path(base).joinpath(f"cline-state-{proto_port}")


def run_cmd(cmd: str, cwd: Path | None = None, env: dict | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, shell=True, check=check, text=True, capture_output=True)


def ensure_python_venv_for_port(proto_port: int) -> Path:
    base_dir = per_job_state_dir(proto_port)
    venv_dir = base_dir.joinpath("python-venv")
    bin_dir = venv_dir.joinpath("bin")
    python_bin = bin_dir.joinpath("python")
    if not python_bin.exists():
        # Create a fresh virtual environment using the current interpreter
        cmd = f"{shlex.quote(sys.executable)} -m venv {shlex.quote(str(venv_dir))}"
        subprocess.run(cmd, shell=True, check=True)
    return venv_dir


def provision_python_venv_for_repo(venv_dir: Path, workspace: Path) -> None:
    py = venv_dir.joinpath("bin", "python")
    run_cmd(f"{shlex.quote(str(py))} -m pip install -U pip setuptools wheel", check=False)
    reqs = [
        workspace.joinpath("requirements.txt"),
        workspace.joinpath("requirements-dev.txt"),
        workspace.joinpath("requirements", "dev.txt"),
        workspace.joinpath("requirements", "test.txt"),
    ]
    for rf in reqs:
        if rf.exists():
            run_cmd(f"{shlex.quote(str(py))} -m pip install -r {shlex.quote(str(rf))}", check=False)
    if workspace.joinpath("pyproject.toml").exists() or workspace.joinpath("setup.py").exists() or workspace.joinpath("setup.cfg").exists():
        run_cmd(f"{shlex.quote(str(py))} -m pip install -e {shlex.quote(str(workspace))}", check=False)


def ensure_standalone_built(cline_repo: Path) -> None:
    core_js = cline_repo / "dist-standalone/cline-core.js"
    descriptor = cline_repo / "dist-standalone/proto/descriptor_set.pb"
    if core_js.exists() and descriptor.exists():
        return
    # print("[INFO] Building standalone core (npm run compile-standalone)...", file=sys.stderr)
    run_cmd("npm run compile-standalone", cwd=cline_repo)


def _extract_between_response_tags(text: str) -> str:
    try:
        m = re.search(r"<response>([\s\S]*?)</response>", text)
        return (m.group(1) if m else "").strip()
    except Exception:
        return ""

def check_failure_in_ui_messages(task_id: str, cline_dir: Path | None = None) -> bool:
    cline_dir = cline_dir or Path.home().joinpath(".cline")
    task_dir = cline_dir.joinpath("data", "tasks", task_id)
    ui_messages = task_dir.joinpath("ui_messages.json")
    if "Cline tried to use plan_mode_respond without value for required parameter 'response'".lower() in ui_messages.read_text(encoding="utf-8").lower():
        return True
    return False

def read_plan_from_ui_messages(task_id: str, cline_dir: Path | None = None) -> str | None:
    """Find the last plan_mode_respond ask in ui_messages and extract its response."""
    cline_dir = cline_dir or Path.home().joinpath(".cline")
    task_dir = cline_dir.joinpath("data", "tasks", task_id)
    ui_messages = task_dir.joinpath("ui_messages.json")
    if not ui_messages.exists():
        return None
    try:
        with ui_messages.open("r", encoding="utf-8") as f:
            arr = json.loads(f.read())
        for msg in reversed(arr):
            if msg.get("type") == "ask" and msg.get("ask") == "plan_mode_respond":
                # if msg.get("partial") is True:
                #     break
                text = msg.get("text")
                if isinstance(text, str) and text:
                    # Try JSON with {"response": "..."}
                    try:
                        obj = json.loads(text)
                        resp = obj.get("response")
                        if isinstance(resp, str) and resp.strip():
                            return resp.strip()
                        # Empty or missing response -> ignore and continue scanning
                        continue
                    except Exception:
                        pass
                    # Try XML-like <response>...</response>
                    extracted = _extract_between_response_tags(text)
                    if extracted:
                        return extracted
                    # Otherwise ignore this ask and continue (avoid saving empty payloads)
                    continue
    except Exception:
        return None
    return None

def read_ui_messages(task_id: str, cline_dir: Path | None = None) -> list[dict] | None:
    """Load the full ui conversation history for a task (all model/user messages)."""
    cline_dir = cline_dir or Path.home().joinpath(".cline")
    task_dir = cline_dir.joinpath("data", "tasks", task_id)
    ui_messages = task_dir.joinpath("ui_messages.json")
    if not ui_messages.exists():
        return None
    # The file may be written concurrently; tolerate short empty/partial states
    for _ in range(10):
        try:
            text = ui_messages.read_text(encoding="utf-8")
        except Exception:
            time.sleep(0.05)
            continue
        if not text.strip():
            time.sleep(0.05)
            continue
        try:
            arr = json.loads(text)
            return arr if isinstance(arr, list) else None
        except json.JSONDecodeError:
            time.sleep(0.05)
            continue
    return None


def read_final_plan(task_id: str, cline_dir: Path | None = None) -> str:
    """Return only the final plan text using multiple strategies."""
    # 1) completion_result (if present)
    cline_dir = cline_dir or Path.home().joinpath(".cline")
    plan = read_plan_from_ui_messages(task_id, cline_dir)
    if plan:
        return plan
    return ""


def grpcurl_json(cline_repo: Path, host: str, port: int, method: str, payload: dict) -> dict:
    descriptor = cline_repo / "dist-standalone/proto/descriptor_set.pb"
    if shutil_which("grpcurl") is None:
        raise RuntimeError("grpcurl is required (e.g., brew install grpcurl)")
    args = [
        "grpcurl",
        "-protoset",
        str(descriptor),
        "-plaintext",
        "-d",
        json.dumps(payload),
        f"{host}:{port}",
        method,
    ]
    res = subprocess.run(args, text=True, capture_output=True)
    if res.returncode != 0:
        raise RuntimeError(f"grpcurl failed: {res.stderr.strip()} | stdout={res.stdout.strip()}")
    try:
        return json.loads(res.stdout or "{}")
    except json.JSONDecodeError:
        return {}


def start_cline_server_if_needed(
    cline_repo: Path, workspace: Path, host: str, proto_port: int, hostbridge_port: int
):
    # Simple, single-attempt launcher (as in cline_helpers.py)
    ensure_standalone_built(cline_repo)
    ensure_extension_symlink(cline_repo)

    if is_port_open(host, proto_port) or is_port_open(host, hostbridge_port):
        kill_processes_listening_on_ports([proto_port, hostbridge_port])
        time.sleep(0.5)

    per_job_dir = per_job_state_dir(proto_port)
    # Ensure an isolated Python venv per server instance and prefer it in PATH
    venv_dir = ensure_python_venv_for_port(proto_port)
    venv_bin = venv_dir.joinpath("bin")
    provision_python_venv_for_repo(venv_dir, workspace)

    env = os.environ.copy()
    env["PATH"] = f"{str(venv_bin)}:{env.get('PATH','')}"
    env["VIRTUAL_ENV"] = str(venv_dir)
    env["PYTHON"] = str(venv_bin.joinpath("python"))
    env.update(
        {
            "E2E_TEST": "false",
            "WORKSPACE_DIR": str(workspace),
            "PROTOBUS_PORT": str(proto_port),
            "DEV_WORKSPACE_FOLDER": str(workspace),
            "TEST_HOSTBRIDGE_WORKSPACE_DIR": str(workspace),
            "HOSTBRIDGE_PORT": str(hostbridge_port),
            "E2E_API_SERVER_PORT": str(proto_port + 7777 - 30000),
            "CLINE_ENVIRONMENT": "local",
            "CLINE_DIR": str(per_job_dir),
            "CLINE_SKIP_RESUME_CONFIRMATION": "1",
            "CLINE_AUTO_FOLLOWUP": "1",
            "CLINE_STANDALONE_CAPTURE_STDIO": "1",
        }
    )
    log_path = Path(os.getenv("TMPDIR", "/tmp")).joinpath(f"cline-python-server-{proto_port}.log")
    cmd = "npx tsx scripts/test-standalone-core-api-server.ts"
    logf = open(log_path, "w")
    proc = subprocess.Popen(
        cmd.split(), cwd=str(cline_repo), env=env, stdout=logf, stderr=subprocess.STDOUT
    )
    wait_for_grpc_ready(host, proto_port, timeout_s=90)
    print(f"[INFO] Starting standalone server; log: {log_path}", file=sys.stderr)
    try:
        logf.flush()
    except Exception:
        pass
    return proc

def list_task_ids(cline_repo: Path, host: str, port: int) -> list[str]:
    out = grpcurl_json(cline_repo, host, port, "cline.TaskService/getTaskHistory", {})
    tasks = out.get("tasks") or []
    ids: list[str] = []
    for t in tasks:
        if isinstance(t, dict):
            tid = t.get("id")
            if isinstance(tid, str) and tid:
                ids.append(tid)
    return ids

def get_latest_task_id(cline_repo: Path, host: str, port: int) -> str | None:
    out = grpcurl_json(cline_repo, host, port, "cline.TaskService/getTaskHistory", {})
    tasks = out.get("tasks") or []
    if not tasks:
        return None
    return tasks[0].get("id")

def submit_task(cline_repo: Path, host: str, port: int, text: str) -> None:
    grpcurl_json(cline_repo, host, port, "cline.TaskService/newTask", {"text": text})

def submit_and_get_task_id(cline_repo: Path, host: str, port: int, text: str, timeout_s: float = 30.0) -> str | None:
    before = set(list_task_ids(cline_repo, host, port))
    submit_task(cline_repo, host, port, text)
    start = time.time()
    while time.time() - start < timeout_s:
        after = list_task_ids(cline_repo, host, port)
        for tid in after:
            if tid not in before:
                return tid
        time.sleep(0.2)
    # Fallback: return latest if available
    latest = get_latest_task_id(cline_repo, host, port)
    return latest

def toggle_mode(cline_repo: Path, host: str, port: int, mode: str, message: str | None = None, images: list[str] | None = None, files: list[str] | None = None) -> None:
    target = (mode or "").strip().upper()
    if target not in {"PLAN", "ACT"}:
        raise ValueError("mode must be 'plan' or 'act'")
    payload: dict = {"mode": target}
    if message or images or files:
        payload["chatContent"] = {
            **({"message": message} if message else {}),
            **({"images": images} if images else {}),
            **({"files": files} if files else {}),
        }
    grpcurl_json(cline_repo, host, port, "cline.StateService/togglePlanActModeProto", payload)

def enable_auto_approve(cline_repo: Path, host: str, port: int) -> None:
    payload = {
        "version": 9999,
        "enabled": True,
        "actions": {
            "read_files": True,
            "read_files_externally": True,
            "edit_files": True,
            "edit_files_externally": True,
            "execute_safe_commands": True,
            "execute_all_commands": True,
            "use_browser": False,
            "use_mcp": False,
        },
        "max_requests": 100,
        "enable_notifications": False,
        "favorites": [
            "execute_safe_commands",
            "read_files",
            "edit_files",
            "skipResumeConfirmation"
        ],
    }
    grpcurl_json(cline_repo, host, port, "cline.StateService/updateAutoApprovalSettings", payload)
    # Also toggle YOLO mode to enable approve-all path inside ToolExecutor/AutoApprove
    grpcurl_json(cline_repo, host, port, "cline.StateService/updateSettings", {"yolo_mode_toggled": True})

def set_openai_gpt41(cline_repo: Path, host: str, port: int) -> None:
    payload = {
        "apiConfiguration": {
            "planModeApiProvider": "OPENAI",
            "actModeApiProvider": "OPENAI",
            "openAiApiKey": os.environ.get("OPENAI_API_KEY", ""),
            "planModeOpenAiModelId": "gpt-4.1",
            "actModeOpenAiModelId": "gpt-4.1",
        }
    }
    grpcurl_json(cline_repo, host, port, "cline.ModelsService/updateApiConfigurationProto", payload)

def set_anthropic_claude45(cline_repo: Path, host: str, port: int) -> None:
    payload = {
        "apiConfiguration": {
            "planModeApiProvider": "ANTHROPIC",
            "actModeApiProvider": "ANTHROPIC",
            "apiKey": os.environ.get("ANTHROPIC_API_KEY", ""),
            "planModeApiModelId": "claude-sonnet-4-5-20250929:1m",
            "actModeApiModelId": "claude-sonnet-4-5-20250929:1m",
        }
    }
    grpcurl_json(cline_repo, host, port, "cline.ModelsService/updateApiConfigurationProto", payload)


def write_ruleset_to_workspace(workspace: Path, ruleset_text: str) -> Path:
    rules_dir = workspace.joinpath(".clinerules")
    rules_dir.mkdir(parents=True, exist_ok=True)
    # Optionally append a debug marker so we can confirm rule application in output
    marker = os.getenv("RULES_DEBUG_MARKER")
    content = ruleset_text if not marker else (ruleset_text + f"\n\n[Debug] If rules applied, include token: {marker}\n")
    rules_path = rules_dir.joinpath("optimized-rules.md")
    rules_path.write_text(content, encoding="utf-8")
    # print(f"[RULES] Wrote rules to {rules_path} ({len(content)} bytes)", file=sys.stderr)
    return rules_path


def apply_ruleset_if_provided(cline_repo: Path, workspace: Path, host: str, port: int, ruleset_text: str | None) -> None:
    if not ruleset_text:
        return
    try:
        text = ruleset_text
        if not text:
            return
        rule_path = write_ruleset_to_workspace(workspace, text)
        # Refresh and toggle
        toggles_before = grpcurl_json(cline_repo, host, port, "cline.FileService/refreshRules", {})
        grpcurl_json(
            cline_repo,
            host,
            port,
            "cline.FileService/toggleClineRule",
            {"isGlobal": False, "rulePath": str(rule_path), "enabled": True},
        )
        toggles_after = grpcurl_json(cline_repo, host, port, "cline.FileService/refreshRules", {})
    except Exception as e:
        print(f"[RULES] Failed to apply rules: {e}", file=sys.stderr)

def run_cline_for_instance(
    instance_id: str,
    image_tag: str,
    cline_repo: Path,
    workspaces_root: Path,
    task_text: str,
    host: str,
    proto_port: int,
    hostbridge_port: int,
    mode: str,
    wait_seconds: int = 600,
    ruleset_text: str = "",
) -> dict:
    """
    1) Materialize repo from image to host workspace (if empty)
    2) Start container with bind mount of workspace
    3) Start Cline server (host) pointing at the workspace
    4) Submit task; wait up to wait_seconds; return either final plan or predictions path, based on cline mode
    """
    workspace = workspaces_root / instance_id.lower()
    workspace.mkdir(parents=True, exist_ok=True)
    # Step 1: copy /testbed from the image to host workspace (no-op if already populated)
    materialize_repo_from_image(image_tag, workspace)
    # Ensure diffs are relative to a baseline commit
    ensure_git_baseline(workspace)
    # Step 2: start the bound container (edit persistence via bind mount)
    stop_container(instance_id)
    start_bound_container(image_tag, instance_id, workspace)
    server_proc = None
    try:
        # Step 3: start Cline server on host (or reuse if already running)
        server_proc = start_cline_server_if_needed(
            cline_repo, workspace, host, proto_port, hostbridge_port
        )
        # Avoid blocking prompts in ACT mode
        enable_auto_approve(cline_repo, host, proto_port)
        toggle_mode(cline_repo, host, proto_port, mode)

        set_openai_gpt41(cline_repo, host, proto_port) 
        # set_anthropic_claude45(cline_repo, host, proto_port)

        apply_ruleset_if_provided(
            cline_repo,
            workspace,
            host,
            proto_port,
            ruleset_text
        )
        # Step 4: submit task and wait for result
        task_id = submit_and_get_task_id(cline_repo, host, proto_port, task_text, timeout_s=30) or ""
        per_job_dir = per_job_state_dir(proto_port)
        # Poll for final output (helpers read from disk)
        start = time.time()

        while time.time() - start < wait_seconds:
            time.sleep(0.5)
            ui_messages = read_ui_messages(task_id, per_job_dir)
            with open(f"ui_messages/{instance_id}.json", "w") as f:
                json.dump(ui_messages, f, ensure_ascii=False, indent=2)

        if mode == "plan":
            final_plan = read_final_plan(task_id, per_job_dir)

            return {
                "task_id": task_id,
                "final_plan": final_plan or "",
                "failure": False,
                "cline_state_dir": str(per_job_dir),
                "workspace": str(workspace),
                "container": container_name_for(instance_id),
            }
        else:
            preds_path = export_patch_from_workspace(
                instance_id=instance_id,
                workspace=workspace,
            )

            return {
                "task_id": task_id,
                "predictions_path": str(preds_path),
                "failure": False,
                "cline_state_dir": str(per_job_dir),
                "workspace": str(workspace),
                "container": container_name_for(instance_id),
            }

        
    finally:
        # Keep the container up for you to test; stop it later when done
        if server_proc is not None:
            try:
                server_proc.terminate()
                server_proc.wait(timeout=10)
            except Exception:
                pass
            if server_proc.poll() is None:
                try:
                    server_proc.kill()
                except Exception:
                    pass
        if mode == "act":
            try:
                shutil.rmtree(per_job_state_dir(proto_port).joinpath("python-venv"), ignore_errors=True)
            except Exception:
                pass