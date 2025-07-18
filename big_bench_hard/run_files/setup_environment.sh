#!/bin/bash

# BigBench Hard Environment Setup Script
echo "🚀 Setting up BigBench Hard Environment"
echo "======================================"

# Environment name
ENV_NAME="bbh_env"

# Check if conda is available
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Anaconda or Miniconda first."
    exit 1
fi

echo "✓ Conda found"

# Remove existing environment if it exists
echo "🧹 Removing existing environment (if exists)..."
conda env remove -n $ENV_NAME -y 2>/dev/null || true

# Create new environment
echo "📦 Creating new conda environment: $ENV_NAME"
conda create -n $ENV_NAME python=3.9 -y

# Activate environment
echo "🔄 Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate $ENV_NAME

# Verify activation
if [[ "$CONDA_DEFAULT_ENV" != "$ENV_NAME" ]]; then
    echo "❌ Failed to activate environment"
    exit 1
fi

echo "✅ Environment activated: $CONDA_DEFAULT_ENV"

# Install pip packages
echo "📥 Installing Python packages..."
pip install --upgrade pip

# Install packages from requirements.txt
pip install pandas>=1.3.0
pip install scikit-learn>=1.0.0
pip install requests>=2.25.0
pip install nest-asyncio>=1.5.0
pip install openai>=1.0.0
pip install tiktoken>=0.4.0
pip install email-validator>=2.0.0
pip install arize-toolkit>=0.1.0
pip install arize-phoenix-evals>=0.1.0
pip install arize-phoenix-client>=0.1.0

echo "🧪 Testing imports..."
python -c "
import pandas as pd
import requests
import openai
import tiktoken
import email_validator
from phoenix.evals import llm_generate, OpenAIModel
from arize_toolkit.extensions.prompt_optimizer import PromptLearningOptimizer
from sklearn.metrics import accuracy_score
print('✅ All imports successful!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Environment setup complete!"
    echo ""
    echo "To use this environment:"
    echo "  conda activate $ENV_NAME"
    echo ""
    echo "To test the setup:"
    echo "  python test_import.py"
    echo "  python test_bbh_download.py"
    echo ""
    echo "To run experiments:"
    echo "  python run_bbh_experiments.py"
else
    echo "❌ Import test failed. Check the error messages above."
    exit 1
fi 