/**
 * Hook for verbalize form state and API integration
 */

import { useState } from 'react';
import { invokeVerbalize } from '../utils/tauri';
import { validateVerbRequest } from '../types/contracts';
import { invokeCheckApiKey } from '../utils/tauri';
import type { VerbRequest, VerbResponse, Provider, ApiProvider } from '../types/contracts';

export function useVerbalize() {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [distribution, setDistribution] = useState<VerbResponse | null>(null);

  const [formState, setFormState] = useState<VerbRequest>({
    prompt: '',
    k: 5,
    tau: 1.0,
    temperature: 0.8,
    seed: null,
    model: 'gpt-4',
    provider: 'openai' as Provider,
    include_token_probabilities: false,
  });

  const updateField = <K extends keyof VerbRequest>(
    field: K,
    value: VerbRequest[K]
  ) => {
    setFormState((prev) => ({ ...prev, [field]: value }));
    setError(null); // Clear error when user edits
  };

  const verbalize = async () => {
    // Validate request
    const validationError = validateVerbRequest(formState);
    if (validationError) {
      setError(validationError);
      return;
    }

    // Check API key for provider (skip for local_vllm)
    if (formState.provider !== 'local_vllm') {
      try {
        const apiKeyCheck = await invokeCheckApiKey(formState.provider as ApiProvider);
        if (!apiKeyCheck.has_key) {
          setError(
            `No API key found for ${formState.provider}. Please configure your API key in Settings.`
          );
          return;
        }
      } catch (err) {
        console.error('API key check failed:', err);
        // Don't block on check failure, let the actual request fail
      }
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await invokeVerbalize(formState);
      setDistribution(response);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : String(err);
      setError(errorMessage);
      setDistribution(null);
    } finally {
      setIsLoading(false);
    }
  };

  const reset = () => {
    setFormState({
      prompt: '',
      k: 5,
      tau: 1.0,
      temperature: 0.8,
      seed: null,
      model: 'gpt-4',
      provider: 'openai' as Provider,
      include_token_probabilities: false,
    });
    setDistribution(null);
    setError(null);
  };

  return {
    formState,
    updateField,
    verbalize,
    reset,
    isLoading,
    error,
    distribution,
  };
}
