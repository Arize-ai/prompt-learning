#!/bin/bash

# BigBench Hard Python Virtual Environment Setup Script
echo "🚀 Setting up BigBench Hard Python Virtual Environment"
echo "===================================================="

# Environment directory
VENV_NAME="bbh_venv"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found. Please install Python 3.8+ first."
    exit 1
fi

echo "✓ Python3 found: $(python3 --version)"

# Remove existing venv if it exists
if [ -d "$VENV_NAME" ]; then
    echo "🧹 Removing existing virtual environment..."
    rm -rf $VENV_NAME
fi

# Create new virtual environment
echo "📦 Creating new Python virtual environment: $VENV_NAME"
python3 -m venv $VENV_NAME

# Activate environment
echo "🔄 Activating virtual environment..."
source $VENV_NAME/bin/activate

# Verify activation
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated: $(basename $VIRTUAL_ENV)"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install packages
echo "📥 Installing Python packages..."
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
    echo "🎉 Virtual environment setup complete!"
    echo ""
    echo "To use this environment:"
    echo "  source $VENV_NAME/bin/activate"
    echo ""
    echo "To deactivate:"
    echo "  deactivate"
    echo ""
    echo "To test the setup:"
    echo "  python test_import.py"
    echo "  python test_bbh_download.py"
    echo ""
    echo "To run experiments:"
    echo "  python run_bbh_experiments.py"
    echo ""
    echo "🔧 VS Code users: Select '$VENV_NAME/bin/python' as your interpreter"
else
    echo "❌ Import test failed. Check the error messages above."
    exit 1
fi 