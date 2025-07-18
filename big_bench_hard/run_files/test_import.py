#!/usr/bin/env python3
"""
Simple test script to verify imports work correctly.
Run this first to make sure all dependencies are installed.
"""

print("Testing imports...")

try:
    import pandas as pd
    print("✓ pandas imported successfully")
except ImportError as e:
    print(f"✗ pandas import failed: {e}")
    exit(1)

try:
    import requests
    print("✓ requests imported successfully")
except ImportError as e:
    print(f"✗ requests import failed: {e}")
    exit(1)

try:
    import json
    print("✓ json imported successfully")
except ImportError as e:
    print(f"✗ json import failed: {e}")
    exit(1)

try:
    from arize_toolkit.extensions.prompt_optimizer import PromptLearningOptimizer
    print("✓ PromptLearningOptimizer imported successfully")
except ImportError as e:
    print(f"✗ PromptLearningOptimizer import failed: {e}")
    print("   Make sure you have arize-toolkit installed: pip install arize-toolkit")
    exit(1)

try:
    from phoenix.evals import OpenAIModel
    print("✓ OpenAIModel imported successfully")
except ImportError as e:
    print(f"✗ OpenAIModel import failed: {e}")
    print("   Make sure you have arize-phoenix-evals installed: pip install arize-phoenix-evals")
    exit(1)

try:
    import openai
    print("✓ openai imported successfully")
except ImportError as e:
    print(f"✗ openai import failed: {e}")
    exit(1)

try:
    from sklearn.metrics import accuracy_score
    print("✓ scikit-learn imported successfully")
except ImportError as e:
    print(f"✗ scikit-learn import failed: {e}")
    exit(1)

print("\n🎉 All imports successful!")
print("Now you can run: python test_bbh_download.py") 