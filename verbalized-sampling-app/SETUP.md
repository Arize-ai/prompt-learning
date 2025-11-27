# Verbalized Sampling - Setup Guide

## API Key Configuration

The app requires API keys to be set as environment variables before launching.

### Required Environment Variables

Set the API keys for the providers you want to use:

```bash
# OpenRouter (recommended - access to multiple providers)
export OPENROUTER_API_KEY="your-key-here"

# OpenAI
export OPENAI_API_KEY="your-key-here"

# Anthropic
export ANTHROPIC_API_KEY="your-key-here"

# Cohere
export COHERE_API_KEY="your-key-here"

# Local vLLM (if using local deployment)
# Default endpoint: http://localhost:8000
```

### Getting API Keys

- **OpenRouter**: Get your key at https://openrouter.ai/keys
- **OpenAI**: Get your key at https://platform.openai.com/api-keys
- **Anthropic**: Get your key at https://console.anthropic.com/
- **Cohere**: Get your key at https://dashboard.cohere.com/api-keys

### Running the App

#### Option 1: Set environment variables then launch
```bash
export OPENROUTER_API_KEY="your-key"
open "Verbalized Sampling.app"
```

#### Option 2: Create a launch script
```bash
#!/bin/bash
# launch.sh

export OPENROUTER_API_KEY="sk-or-v1-..."
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."

open "/Applications/Verbalized Sampling.app"
```

Make it executable:
```bash
chmod +x launch.sh
./launch.sh
```

#### Option 3: Add to shell profile
Add to `~/.zshrc` or `~/.bashrc`:
```bash
export OPENROUTER_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
```

Then restart your terminal or run:
```bash
source ~/.zshrc  # or source ~/.bashrc
```

### Local vLLM Setup (Optional)

If using local vLLM:

1. Install vLLM:
```bash
pip install vllm
```

2. Start vLLM server:
```bash
vllm serve <model-name> --port 8000
```

3. The app will automatically connect to `http://localhost:8000`

### Verifying Configuration

1. Launch the app
2. Check the sidecar is running: `curl http://localhost:8765/api/v1/health`
3. Select your provider in the UI
4. If API key is missing, you'll see an error when generating

### Security Notes

- Never commit API keys to version control
- Use environment variables or a secrets manager
- Consider using OpenRouter to access multiple providers with one key
- For production, implement secure key storage via Tauri's stronghold plugin

## Provider Capabilities

### OpenRouter
- Access to Claude, GPT-4, Gemini, Llama, Mistral, and more
- Single API key for multiple providers
- Good for experimentation
- Max k: 100

### OpenAI
- Native GPT models
- Best for GPT-4 Turbo and GPT-3.5
- Max k: 100

### Anthropic
- Claude 3.5 Sonnet, Opus, Sonnet, Haiku
- Max k: 100

### Cohere
- Command, Command-R models
- Max k: 100

### Local vLLM
- Any model you can run locally
- No API costs
- Max k: 500
