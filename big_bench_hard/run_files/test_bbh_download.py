#!/usr/bin/env python3
"""
Test script for BigBench Hard JSON download functionality.
Run this script to test the download and JSON parsing functions.
"""

import os
import sys
import pandas as pd
from pl_multidataset import (
    download_bbh_json_files,
    get_available_bbh_tasks,
    load_json_to_dataframe,
    data_prep_json,
)


def test_download_functionality():
    """Test the download functionality for BigBench Hard JSON files."""
    print("Testing BigBench Hard JSON download functionality...")

    # Test 1: Download files
    print("\n1. Testing download_bbh_json_files()...")
    try:
        downloaded_files = download_bbh_json_files("bbh-download")
        print(f"✓ Successfully downloaded {len(downloaded_files)} files")

        # Show first few downloaded files
        if downloaded_files:
            print("First 5 downloaded files:")
            for i, file_path in enumerate(downloaded_files[:5]):
                print(f"  - {file_path}")

    except Exception as e:
        print(f"✗ Error downloading files: {e}")
        return False

    # Test 2: Get available tasks
    print("\n2. Testing get_available_bbh_tasks()...")
    try:
        available_tasks = get_available_bbh_tasks("bbh-download")
        print(f"✓ Found {len(available_tasks)} available tasks")

        if available_tasks:
            print("Available tasks:")
            for task in available_tasks:
                print(f"  - {task}")

    except Exception as e:
        print(f"✗ Error getting available tasks: {e}")
        return False

    # Test 3: Load a specific JSON file
    print("\n3. Testing load_json_to_dataframe()...")
    if available_tasks:
        test_task = available_tasks[0]  # Take first available task
        test_file = f"bbh-download/{test_task}.json"

        try:
            df = load_json_to_dataframe(test_file)
            print(f"✓ Successfully loaded {test_task} as DataFrame")
            print(f"   Shape: {df.shape}")
            print(f"   Columns: {list(df.columns)}")

            if len(df) > 0:
                print(f"   Sample input: {df.iloc[0]['input'][:100]}...")
                print(f"   Sample target: {df.iloc[0]['target']}")

        except Exception as e:
            print(f"✗ Error loading JSON file: {e}")
            return False

    # Test 4: Test data preparation
    print("\n4. Testing data_prep_json()...")
    if available_tasks:
        test_task = available_tasks[0]
        test_file = f"bbh-download/{test_task}.json"

        try:
            dataset, train_set, test_set, _, _ = data_prep_json(
                test_file, num_samples=10
            )
            print(f"✓ Successfully prepared data for {test_task}")
            print(f"   Full dataset shape: {dataset.shape}")
            print(f"   Train set shape: {train_set.shape}")
            print(f"   Test set shape: {test_set.shape}")

            # Check if CSV files were created
            if os.path.exists("train.csv") and os.path.exists("test.csv"):
                print("✓ CSV files created successfully")
            else:
                print("✗ CSV files not created")

        except Exception as e:
            print(f"✗ Error preparing data: {e}")
            return False

    print("\n✅ All tests passed!")
    return True


def show_task_info():
    """Show information about available tasks."""
    print("\nTask Information:")
    print("=" * 50)

    available_tasks = get_available_bbh_tasks("bbh-download")

    for task in available_tasks:
        json_file = f"bbh-download/{task}.json"
        if os.path.exists(json_file):
            try:
                df = load_json_to_dataframe(json_file)
                print(f"\n{task}:")
                print(f"  - Examples: {len(df)}")
                print(f"  - Sample input: {df.iloc[0]['input'][:100]}...")
                print(f"  - Sample target: {df.iloc[0]['target']}")
            except Exception as e:
                print(f"  - Error loading: {e}")


if __name__ == "__main__":
    # Run the test
    success = test_download_functionality()

    if success:
        # Show task information
        show_task_info()

        # Clean up test files
        if os.path.exists("train.csv"):
            os.remove("train.csv")
        if os.path.exists("test.csv"):
            os.remove("test.csv")

        print("\n🎉 Test completed successfully!")
        print(
            "You can now use the BigBench Hard JSON functionality in your experiments."
        )
        print("\nTo run experiments with BigBench Hard data, use:")
        print("  from pl_multidataset import run_bbh_experiments")
        print("  bbh_results = run_bbh_experiments()")
    else:
        print("\n❌ Tests failed. Please check the error messages above.")
        sys.exit(1)
