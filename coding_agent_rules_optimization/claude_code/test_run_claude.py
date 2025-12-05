#!/usr/bin/env python3
"""
Integration test for run_claude function.

Tests running Claude Code on 5 SWE-bench instances in parallel.

Usage:
    python test_run_claude.py
"""

import sys
import os
from pathlib import Path
import shutil

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from run_claude import run_claude


def test_run_claude_parallel():
    """
    Test run_claude on 5 instances with 5 workers (parallel execution).
    """
    print("=" * 80)
    print("Testing run_claude with 5 instances in parallel")
    print("=" * 80)

    # Select 5 relatively simple instances from SWE-bench Lite
    test_instances = [
        "django__django-16408",
        "django__django-14016",
        "django__django-16595",
        "django__django-13448",
        "django__django-11815",
    ]

    run_id = "test_parallel_5"

    print(f"\nTest Configuration:")
    print(f"  Run ID: {run_id}")
    print(f"  Instances: {len(test_instances)}")
    print(f"  Workers: 5 (parallel)")
    print(f"  Timeout: 600s per instance")
    print(f"  Instance IDs:")
    for iid in test_instances:
        print(f"    - {iid}")

    # Clean up any previous test results
    output_file = f"claude_results_{run_id}.csv"
    if Path(output_file).exists():
        print(f"\nRemoving previous test results: {output_file}")
        Path(output_file).unlink()

    logs_dir = Path("logs/run_evaluation") / run_id
    if logs_dir.exists():
        print(f"Removing previous evaluation logs: {logs_dir}")
        shutil.rmtree(logs_dir, ignore_errors=True)

    print("\n" + "=" * 80)
    print("Starting Claude Code runs (this will take a few minutes)...")
    print("=" * 80 + "\n")

    # Run Claude on the instances
    try:
        df = run_claude(
            run_id=run_id,
            dataset_name="SWE-bench/SWE-bench_Lite",
            instance_ids=test_instances,
            ruleset="",  # No custom ruleset
            workers=5,  # 5 workers for parallel execution
            wait_seconds=300,  # 5 minutes per instance
        )
    except Exception as e:
        print(f"\n✗ ERROR: run_claude failed with exception: {e}")
        import traceback

        traceback.print_exc()
        return False

    print("\n" + "=" * 80)
    print("Validating Results")
    print("=" * 80)

    # Validate DataFrame structure
    success = True

    print("\n1. Checking DataFrame structure...")
    expected_columns = [
        "instance_id",
        "problem_statement",
        "ground_truth_patch",
        "test_patch",
        "coding_agent_patch",
        "pass_or_fail",
    ]

    if df.empty:
        print("   ✗ DataFrame is empty!")
        success = False
    else:
        print(f"   ✓ DataFrame has {len(df)} rows")

    actual_columns = list(df.columns)
    if actual_columns == expected_columns:
        print(f"   ✓ Columns match expected: {expected_columns}")
    else:
        print(f"   ✗ Column mismatch!")
        print(f"     Expected: {expected_columns}")
        print(f"     Actual:   {actual_columns}")
        success = False

    # Check all instances are present
    print("\n2. Checking all instances are in results...")
    result_ids = set(df["instance_id"].tolist())
    expected_ids = set(test_instances)

    if result_ids == expected_ids:
        print(f"   ✓ All {len(test_instances)} instances present")
    else:
        missing = expected_ids - result_ids
        extra = result_ids - expected_ids
        if missing:
            print(f"   ✗ Missing instances: {missing}")
            success = False
        if extra:
            print(f"   ⚠ Extra instances: {extra}")

    # Check that patches were generated
    print("\n3. Checking patch generation...")
    patches_generated = 0
    empty_patches = 0

    for _, row in df.iterrows():
        patch = row["coding_agent_patch"]
        if patch and len(str(patch).strip()) > 0:
            patches_generated += 1
        else:
            empty_patches += 1
            print(f"   ⚠ Empty patch for: {row['instance_id']}")

    print(f"   Patches generated: {patches_generated}/{len(df)}")
    print(f"   Empty patches: {empty_patches}/{len(df)}")

    if patches_generated > 0:
        print(f"   ✓ At least some patches were generated")
    else:
        print(f"   ✗ No patches generated at all!")
        success = False

    # Check pass/fail results
    print("\n4. Checking evaluation results...")
    passed = len(df[df["pass_or_fail"] == "pass"])
    failed = len(df[df["pass_or_fail"] == "fail"])

    print(f"   Passed: {passed}")
    print(f"   Failed: {failed}")

    if passed + failed == len(df):
        print(f"   ✓ All instances have pass/fail status")
    else:
        print(f"   ✗ Some instances missing pass/fail status")
        success = False

    # Check output file
    print("\n5. Checking output file...")
    if Path(output_file).exists():
        file_size = Path(output_file).stat().st_size
        print(f"   ✓ Output file created: {output_file} ({file_size} bytes)")
    else:
        print(f"   ✗ Output file not found: {output_file}")
        success = False

    # Check evaluation logs
    print("\n6. Checking evaluation logs...")
    logs_exist = 0
    for iid in test_instances:
        report_path = (
            Path("logs/run_evaluation") / run_id / "claude-code" / iid / "report.json"
        )
        if report_path.exists():
            logs_exist += 1

    print(f"   Evaluation logs found: {logs_exist}/{len(test_instances)}")
    if logs_exist > 0:
        print(f"   ✓ At least some evaluation logs exist")
    else:
        print(f"   ⚠ No evaluation logs found (evaluation may have failed)")

    # Print summary statistics
    print("\n" + "=" * 80)
    print("Test Summary")
    print("=" * 80)

    if not df.empty:
        print(f"\nDataFrame Info:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        print(f"  Memory: {df.memory_usage(deep=True).sum() / 1024:.1f} KB")

        print(f"\nPatch Statistics:")
        patch_lengths = df["coding_agent_patch"].apply(
            lambda x: len(str(x)) if x else 0
        )
        print(f"  Total patch characters: {patch_lengths.sum():,}")
        print(f"  Average patch length: {patch_lengths.mean():.0f} chars")
        print(f"  Max patch length: {patch_lengths.max():,} chars")
        print(f"  Min patch length: {patch_lengths.min()} chars")

        print(f"\nResults Breakdown:")
        for _, row in df.iterrows():
            patch_len = (
                len(str(row["coding_agent_patch"])) if row["coding_agent_patch"] else 0
            )
            status = "✓" if row["pass_or_fail"] == "pass" else "✗"
            print(
                f"  {status} {row['instance_id']}: {patch_len} chars, {row['pass_or_fail']}"
            )

    print("\n" + "=" * 80)
    if success:
        print("✓ All tests passed!")
        print("=" * 80)
        return True
    else:
        print("✗ Some tests failed - check output above")
        print("=" * 80)
        return False


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("Claude Code Integration Test")
    print("=" * 80)
    print("\nThis test will:")
    print("  1. Run Claude Code on 5 SWE-bench instances")
    print("  2. Execute them in parallel with 5 workers")
    print("  3. Validate the output DataFrame structure")
    print("  4. Check patch generation and evaluation")
    print("\nExpected duration: 5-10 minutes")
    print("\nPress Ctrl+C to cancel...")

    try:
        input("\nPress Enter to start the test...")
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(0)

    print()

    success = test_run_claude_parallel()

    sys.exit(0 if success else 1)
