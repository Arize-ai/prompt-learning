/**
 * Provider form for verbalized sampling configuration
 */

import React from 'react';
import type { VerbRequest, Provider } from '../types/contracts';
import { PROVIDER_MAX_K } from '../types/contracts';

interface ProviderFormProps {
  formState: VerbRequest;
  onUpdate: <K extends keyof VerbRequest>(field: K, value: VerbRequest[K]) => void;
  onSubmit: () => void;
  isLoading: boolean;
  error: string | null;
}

const PROVIDER_MODELS: Record<Provider, string[]> = {
  openai: ['gpt-4', 'gpt-4-turbo', 'gpt-3.5-turbo'],
  anthropic: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
  cohere: ['command', 'command-light', 'command-r', 'command-r-plus'],
  local_vllm: ['llama-3-70b', 'mixtral-8x7b', 'custom'],
};

export function ProviderForm({
  formState,
  onUpdate,
  onSubmit,
  isLoading,
  error,
}: ProviderFormProps) {
  const maxK = PROVIDER_MAX_K[formState.provider];
  const availableModels = PROVIDER_MODELS[formState.provider];

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSubmit();
  };

  return (
    <form onSubmit={handleSubmit} className="provider-form">
      <div className="form-section">
        <h2>Configuration</h2>

        {/* Provider Selection */}
        <div className="form-group">
          <label htmlFor="provider">Provider</label>
          <select
            id="provider"
            value={formState.provider}
            onChange={(e) => {
              const provider = e.target.value as Provider;
              onUpdate('provider', provider);
              // Update model to first available for new provider
              onUpdate('model', PROVIDER_MODELS[provider][0]);
            }}
            disabled={isLoading}
          >
            <option value="openai">OpenAI</option>
            <option value="anthropic">Anthropic</option>
            <option value="cohere">Cohere</option>
            <option value="local_vllm">Local vLLM</option>
          </select>
        </div>

        {/* Model Selection */}
        <div className="form-group">
          <label htmlFor="model">Model</label>
          <select
            id="model"
            value={formState.model}
            onChange={(e) => onUpdate('model', e.target.value)}
            disabled={isLoading}
          >
            {availableModels.map((model) => (
              <option key={model} value={model}>
                {model}
              </option>
            ))}
          </select>
        </div>

        {/* Prompt */}
        <div className="form-group">
          <label htmlFor="prompt">Prompt</label>
          <textarea
            id="prompt"
            value={formState.prompt}
            onChange={(e) => onUpdate('prompt', e.target.value)}
            placeholder="Enter your prompt..."
            rows={4}
            disabled={isLoading}
            required
          />
        </div>
      </div>

      <div className="form-section">
        <h3>Sampling Parameters</h3>

        {/* Number of Completions (k) */}
        <div className="form-group">
          <label htmlFor="k">
            Number of Completions (k) - Max: {maxK}
          </label>
          <input
            type="number"
            id="k"
            value={formState.k}
            onChange={(e) => onUpdate('k', parseInt(e.target.value) || 1)}
            min={1}
            max={maxK}
            disabled={isLoading}
            required
          />
        </div>

        {/* Temperature */}
        <div className="form-group">
          <label htmlFor="temperature">
            Temperature: {formState.temperature.toFixed(2)}
          </label>
          <input
            type="range"
            id="temperature"
            value={formState.temperature}
            onChange={(e) =>
              onUpdate('temperature', parseFloat(e.target.value))
            }
            min={0}
            max={2}
            step={0.1}
            disabled={isLoading}
          />
          <div className="range-labels">
            <span>Deterministic (0)</span>
            <span>Creative (2)</span>
          </div>
        </div>

        {/* Tau (Temperature Scaling) */}
        <div className="form-group">
          <label htmlFor="tau">Tau (Temperature Scaling): {formState.tau.toFixed(2)}</label>
          <input
            type="range"
            id="tau"
            value={formState.tau}
            onChange={(e) => onUpdate('tau', parseFloat(e.target.value))}
            min={0.1}
            max={5}
            step={0.1}
            disabled={isLoading}
          />
          <div className="range-labels">
            <span>Sharp (0.1)</span>
            <span>Smooth (5)</span>
          </div>
        </div>

        {/* Seed */}
        <div className="form-group">
          <label htmlFor="seed">Random Seed (optional)</label>
          <input
            type="number"
            id="seed"
            value={formState.seed ?? ''}
            onChange={(e) =>
              onUpdate('seed', e.target.value ? parseInt(e.target.value) : null)
            }
            placeholder="Leave empty for random"
            disabled={isLoading}
          />
        </div>

        {/* Token Probabilities */}
        <div className="form-group checkbox-group">
          <label>
            <input
              type="checkbox"
              checked={formState.include_token_probabilities}
              onChange={(e) =>
                onUpdate('include_token_probabilities', e.target.checked)
              }
              disabled={isLoading}
            />
            Include token probabilities
          </label>
        </div>
      </div>

      {/* Error Display */}
      {error && (
        <div className="error-message" role="alert">
          <strong>Error:</strong> {error}
        </div>
      )}

      {/* Submit Button */}
      <button
        type="submit"
        className="submit-button"
        disabled={isLoading || !formState.prompt}
      >
        {isLoading ? 'Generating...' : 'Generate Distribution'}
      </button>
    </form>
  );
}
