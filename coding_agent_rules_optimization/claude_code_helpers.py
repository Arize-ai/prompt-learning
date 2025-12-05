import os
import subprocess
from pathlib import Path

from container_helpers import (
    materialize_repo_from_image,
    start_bound_container,
    stop_container,
    ensure_git_baseline,
    export_patch_from_workspace,
)


def run_claude_for_instance(
    instance_id: str,
    image_tag: str,
    workspace: Path,
    task_text: str,
    wait_seconds: int = 300,
    ruleset_text: str = "",
    model_name: str = "claude-sonnet-4-5",
) -> dict:
    """
    Run Claude Code CLI in act mode for a single SWE-bench instance.

    1) Materialize repo from image to host workspace (if empty)
    2) Start container with bind mount of workspace
    3) Run Claude Code CLI with the task
    4) Export patch from workspace

    Args:
        instance_id: The SWE-bench instance ID
        image_tag: Docker image tag for the instance
        workspace: Path to workspace directory
        task_text: The problem statement to solve
        wait_seconds: Max seconds to wait (passed as --max-turns equivalent)
        ruleset_text: Optional ruleset to append to system prompt

    Returns:
        dict with task results including predictions_path
    """
    # Step 1: Materialize repo from image to workspace
    workspace.mkdir(parents=True, exist_ok=True)
    materialize_repo_from_image(image_tag, workspace)
    ensure_git_baseline(workspace)

    # Step 2: Start bound container
    stop_container(instance_id)
    start_bound_container(image_tag, instance_id, workspace)

    try:
        # Step 3: Run Claude Code CLI
        cmd = [
            "claude",
            "-p",  # Print mode (non-interactive)
            "--output-format",
            "text",
            "--dangerously-skip-permissions",  # Skip permission prompts
            # No --max-turns: let Claude run until done (timeout acts as safety valve)
            "--model",
            model_name,
        ]

        # Add ruleset if provided
        if ruleset_text:
            cmd.extend(["--append-system-prompt", ruleset_text])

        # Add the task text as the query
        cmd.append(task_text)

        # Debug: Print command
        print(f"\n[DEBUG {instance_id}] Running command:")
        print(f"  {' '.join(cmd[:8])}... (task text truncated)")
        print(f"  CWD: {workspace}")
        print(f"  Timeout: {wait_seconds}s")

        # Run Claude Code in the workspace directory
        result = subprocess.run(
            cmd,
            cwd=str(workspace),
            capture_output=True,
            text=True,
            timeout=wait_seconds,
            env=os.environ.copy(),
        )

        # Debug: Print result
        print(f"[DEBUG {instance_id}] Command completed:")
        print(f"  Exit code: {result.returncode}")
        print(f"  Stdout length: {len(result.stdout)} chars")
        print(f"  Stderr length: {len(result.stderr)} chars")
        if result.stderr:
            print(f"  Stderr preview: {result.stderr[:500]}")
        if result.stdout:
            print(f"  Stdout preview: {result.stdout[:500]}")

        # Step 4: Export patch from workspace
        preds_path = export_patch_from_workspace(
            instance_id=instance_id,
            workspace=workspace,
            model_name_or_path="claude-code",
        )

        print(f"[DEBUG {instance_id}] Patch exported to: {preds_path}")
        if preds_path.exists():
            patch_size = preds_path.stat().st_size
            print(f"[DEBUG {instance_id}] Patch size: {patch_size} bytes")

        return {
            "instance_id": instance_id,
            "predictions_path": str(preds_path),
            "failure": False,
            "workspace": str(workspace),
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode,
        }

    except subprocess.TimeoutExpired:
        # Still try to export whatever changes were made
        preds_path = export_patch_from_workspace(
            instance_id=instance_id,
            workspace=workspace,
            model_name_or_path="claude-code",
        )
        return {
            "instance_id": instance_id,
            "predictions_path": str(preds_path),
            "failure": False,
            "workspace": str(workspace),
            "timeout": True,
        }
    except Exception as e:
        return {
            "instance_id": instance_id,
            "predictions_path": "",
            "failure": True,
            "workspace": str(workspace),
            "error": str(e),
        }
