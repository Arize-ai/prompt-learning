"""
Simple tests for Claude Code helpers.

Usage:
    python test_claude_code.py --simple     # Test with a very simple task
    python test_claude_code.py --swebench   # Test with a real SWE-bench instance (takes longer)
"""

import argparse
import sys
import os
from pathlib import Path
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from claude_code_helpers import run_claude_for_instance
from swebench.harness.test_spec.test_spec import make_test_spec
from swebench.harness.utils import load_swebench_dataset


def test_simple_task():
    """Test with a very simple task that doesn't require SWE-bench."""
    print("\n=== Testing simple task ===")

    # Create a temporary workspace
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir) / "test_workspace"
        workspace.mkdir(parents=True, exist_ok=True)

        # Create a simple Python file
        test_file = workspace / "test.py"
        test_file.write_text("def add(a, b):\n    return a + b\n")

        # Initialize git
        os.system(
            f"cd {workspace} && git init && git add . && git -c user.email=test@test.com -c user.name=Test commit -m 'initial'"
        )

        print(f"Workspace: {workspace}")
        print(f"Initial file contents:\n{test_file.read_text()}")

        # Simple task - ask Claude to add a multiply function
        task = "Add a multiply(a, b) function to test.py that multiplies two numbers"

        # Mock the container functions since we're not using Docker for this simple test
        print(f"\nTask: {task}")
        print("\nNote: This simple test requires Docker containers to be set up.")
        print(
            "Use --swebench for a full integration test, or manually test run_claude_for_instance"
        )


def test_swebench_instance():
    """Test with an actual SWE-bench instance."""
    print("\n=== Testing SWE-bench instance ===")

    # Use a simple, fast instance from SWE-bench Lite
    instance_id = "sympy__sympy-13177"  # A relatively simple issue

    print(f"Loading instance: {instance_id}")
    dataset = load_swebench_dataset("SWE-bench/SWE-bench_Lite", "test", [instance_id])

    if not dataset:
        print(f"ERROR: Could not load instance {instance_id}")
        return False

    instance = dataset[0]
    print(f"Problem statement preview: {instance['problem_statement'][:200]}...")

    # Get image tag
    image_tag = make_test_spec(instance).instance_image_key
    print(f"Image tag: {image_tag}")

    # Create workspace in temp directory
    workspace = Path(tempfile.gettempdir()) / "claude_code_test" / instance_id.lower()
    print(f"Workspace: {workspace}")

    # Test without ruleset first
    print("\n--- Testing WITHOUT ruleset ---")
    try:
        result = run_claude_for_instance(
            instance_id=instance_id,
            image_tag=image_tag,
            workspace=workspace,
            task_text=instance["problem_statement"],  # Truncate for faster test
            wait_seconds=300,  # Short timeout for testing
            ruleset_text="",
        )

        print(f"\nResult:")
        print(f"  Success: {not result['failure']}")
        print(f"  Predictions path: {result.get('predictions_path', 'N/A')}")
        print(f"  Workspace: {result.get('workspace', 'N/A')}")

        # Check if there was an error
        if result.get("failure"):
            print(f"\n✗ FAILED with error: {result.get('error', 'Unknown error')}")
            if result.get("stdout"):
                print(f"\nStdout:\n{result['stdout']}")
            if result.get("stderr"):
                print(f"\nStderr:\n{result['stderr']}")
            return False

        if result.get("timeout"):
            print(f"\n⚠ Timeout occurred after {300} seconds")

        if result.get("stdout"):
            print(f"\nStdout preview:\n{result['stdout'][:300]}...")
        if result.get("stderr"):
            print(f"\nStderr preview:\n{result['stderr'][:300]}...")

        # Check if patch was created
        preds_path_str = result.get("predictions_path", "")
        if not preds_path_str:
            print("⚠ Warning: No predictions path returned")
            return False

        preds_path = Path(preds_path_str)
        if preds_path.exists() and preds_path.is_file():
            import json

            with open(preds_path) as f:
                content = f.read().strip()
                if content:
                    pred = json.loads(content.split("\n")[0])  # First line of JSONL
                    patch_len = len(pred.get("model_patch", ""))
                    print(f"\nPatch created: {patch_len} characters")
                    if patch_len > 0:
                        print("✓ Patch successfully generated!")
                    else:
                        print("⚠ Warning: Empty patch generated")
                else:
                    print("⚠ Warning: Empty predictions file")
        else:
            print(f"⚠ Warning: Predictions file not found or not a file: {preds_path}")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    # Test with ruleset
    print("\n--- Testing WITH ruleset ---")
    simple_ruleset = """
# Test Ruleset
- Write clear, concise code
- Add comments to explain complex logic
- Follow PEP 8 style guidelines
"""

    # Clean workspace for fresh test
    if workspace.exists():
        shutil.rmtree(workspace, ignore_errors=True)

    try:
        result = run_claude_for_instance(
            instance_id=instance_id,
            image_tag=image_tag,
            workspace=workspace,
            task_text=instance["problem_statement"],
            wait_seconds=300,
            ruleset_text=simple_ruleset,
        )

        if result.get("timeout"):
            print(f"\n⚠ Timeout occurred after {300} seconds")

        print(f"\nResult:")
        print(f"  Success: {not result['failure']}")
        print(f"  Predictions path: {result.get('predictions_path', 'N/A')}")

        if result.get("stdout"):
            print(f"\nStdout preview:\n{result['stdout'][:300]}...")

        print("✓ Test with ruleset completed!")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback

        traceback.print_exc()
        return False

    return True


def test_minimal():
    """Minimal smoke test - just check imports and function signature."""
    print("\n=== Minimal smoke test ===")

    from claude_code_helpers import run_claude_for_instance
    import inspect

    # Check function signature
    sig = inspect.signature(run_claude_for_instance)
    print(f"Function signature: {sig}")

    params = list(sig.parameters.keys())
    expected_params = [
        "instance_id",
        "image_tag",
        "workspace",
        "task_text",
        "wait_seconds",
        "ruleset_text",
    ]

    print(f"\nExpected parameters: {expected_params}")
    print(f"Actual parameters: {params}")

    if params == expected_params:
        print("✓ Function signature matches!")
        return True
    else:
        print("✗ Function signature mismatch!")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Claude Code helpers")
    parser.add_argument(
        "--simple", action="store_true", help="Run simple task test (requires Docker)"
    )
    parser.add_argument(
        "--swebench", action="store_true", help="Run full SWE-bench test (takes longer)"
    )
    parser.add_argument(
        "--minimal",
        action="store_true",
        help="Run minimal smoke test (no Docker needed)",
    )

    args = parser.parse_args()

    # Default to minimal test if no args
    if not any([args.simple, args.swebench, args.minimal]):
        args.minimal = True

    success = True

    if args.minimal:
        success = test_minimal() and success

    if args.simple:
        test_simple_task()

    if args.swebench:
        success = test_swebench_instance() and success

    print("\n" + "=" * 60)
    if success:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
        sys.exit(1)
