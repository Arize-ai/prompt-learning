/**
 * API Key Settings Component
 * Secure management of API keys using Tauri Stronghold
 */

import { useState, useEffect } from 'react';
import type { ApiProvider } from '../types/contracts';
import {
  invokeStoreApiKey,
  invokeCheckApiKey,
  invokeDeleteApiKey,
  invokeListApiKeys,
} from '../utils/tauri';

interface ApiKeySettingsProps {
  isOpen: boolean;
  onClose: () => void;
}

interface ProviderKeyState {
  provider: ApiProvider;
  label: string;
  key: string;
  hasKey: boolean;
  keyPreview?: string;
  showKey: boolean;
  isSaving: boolean;
  isDeleting: boolean;
  error: string | null;
  success: string | null;
}

const PROVIDERS: { provider: ApiProvider; label: string; placeholder: string }[] = [
  { provider: 'openrouter', label: 'OpenRouter', placeholder: 'sk-or-v1-...' },
  { provider: 'openai', label: 'OpenAI', placeholder: 'sk-...' },
  { provider: 'anthropic', label: 'Anthropic', placeholder: 'sk-ant-...' },
  { provider: 'cohere', label: 'Cohere', placeholder: 'co-...' },
];

export function ApiKeySettings({ isOpen, onClose }: ApiKeySettingsProps) {
  const [providerStates, setProviderStates] = useState<Record<ApiProvider, ProviderKeyState>>(
    {} as Record<ApiProvider, ProviderKeyState>
  );
  const [isLoading, setIsLoading] = useState(true);

  // Initialize provider states
  useEffect(() => {
    const initialStates: Record<ApiProvider, ProviderKeyState> = {} as Record<
      ApiProvider,
      ProviderKeyState
    >;

    PROVIDERS.forEach(({ provider, label }) => {
      initialStates[provider] = {
        provider,
        label,
        key: '',
        hasKey: false,
        showKey: false,
        isSaving: false,
        isDeleting: false,
        error: null,
        success: null,
      };
    });

    setProviderStates(initialStates);
  }, []);

  // Load existing keys on mount
  useEffect(() => {
    if (isOpen) {
      loadApiKeys();
    }
  }, [isOpen]);

  const loadApiKeys = async () => {
    try {
      setIsLoading(true);
      const apiKeys = await invokeListApiKeys();

      setProviderStates((prev) => {
        const updated = { ...prev };
        apiKeys.forEach((apiKey) => {
          if (updated[apiKey.provider as ApiProvider]) {
            updated[apiKey.provider as ApiProvider] = {
              ...updated[apiKey.provider as ApiProvider],
              hasKey: apiKey.has_key,
              keyPreview: apiKey.key_preview,
            };
          }
        });
        return updated;
      });
    } catch (err) {
      console.error('Failed to load API keys:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveKey = async (provider: ApiProvider) => {
    const state = providerStates[provider];
    if (!state.key.trim()) {
      setProviderStates((prev) => ({
        ...prev,
        [provider]: { ...prev[provider], error: 'API key cannot be empty' },
      }));
      return;
    }

    try {
      setProviderStates((prev) => ({
        ...prev,
        [provider]: { ...prev[provider], isSaving: true, error: null, success: null },
      }));

      await invokeStoreApiKey(provider, state.key.trim());

      // Check the saved key to get preview
      const response = await invokeCheckApiKey(provider);

      setProviderStates((prev) => ({
        ...prev,
        [provider]: {
          ...prev[provider],
          isSaving: false,
          hasKey: true,
          keyPreview: response.key_preview,
          key: '',
          success: 'API key saved successfully',
        },
      }));

      // Clear success message after 3 seconds
      setTimeout(() => {
        setProviderStates((prev) => ({
          ...prev,
          [provider]: { ...prev[provider], success: null },
        }));
      }, 3000);
    } catch (err) {
      setProviderStates((prev) => ({
        ...prev,
        [provider]: {
          ...prev[provider],
          isSaving: false,
          error: err instanceof Error ? err.message : 'Failed to save API key',
        },
      }));
    }
  };

  const handleDeleteKey = async (provider: ApiProvider) => {
    if (!confirm(`Are you sure you want to delete the ${providerStates[provider].label} API key?`)) {
      return;
    }

    try {
      setProviderStates((prev) => ({
        ...prev,
        [provider]: { ...prev[provider], isDeleting: true, error: null, success: null },
      }));

      await invokeDeleteApiKey(provider);

      setProviderStates((prev) => ({
        ...prev,
        [provider]: {
          ...prev[provider],
          isDeleting: false,
          hasKey: false,
          keyPreview: undefined,
          success: 'API key deleted successfully',
        },
      }));

      // Clear success message after 3 seconds
      setTimeout(() => {
        setProviderStates((prev) => ({
          ...prev,
          [provider]: { ...prev[provider], success: null },
        }));
      }, 3000);
    } catch (err) {
      setProviderStates((prev) => ({
        ...prev,
        [provider]: {
          ...prev[provider],
          isDeleting: false,
          error: err instanceof Error ? err.message : 'Failed to delete API key',
        },
      }));
    }
  };

  const handleKeyChange = (provider: ApiProvider, value: string) => {
    setProviderStates((prev) => ({
      ...prev,
      [provider]: { ...prev[provider], key: value, error: null },
    }));
  };

  const toggleShowKey = (provider: ApiProvider) => {
    setProviderStates((prev) => ({
      ...prev,
      [provider]: { ...prev[provider], showKey: !prev[provider].showKey },
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content api-key-modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h3>API Key Settings</h3>
          <button onClick={onClose} className="modal-close" aria-label="Close">
            ×
          </button>
        </div>

        <div className="modal-body">
          <p className="api-key-info">
            Store your API keys securely using encrypted Stronghold storage. Keys are never sent
            to the frontend or logged.
          </p>

          {isLoading ? (
            <div className="loading-state">Loading API keys...</div>
          ) : (
            <div className="api-key-providers">
              {PROVIDERS.map(({ provider, label, placeholder }) => {
                const state = providerStates[provider];
                if (!state) return null;

                return (
                  <div key={provider} className="api-key-provider">
                    <div className="provider-header">
                      <h4>{label}</h4>
                      {state.hasKey && (
                        <span className="key-status active">
                          ✓ Key stored {state.keyPreview && `(${state.keyPreview})`}
                        </span>
                      )}
                      {!state.hasKey && (
                        <span className="key-status inactive">No key stored</span>
                      )}
                    </div>

                    <div className="key-input-group">
                      <div className="key-input-wrapper">
                        <input
                          type={state.showKey ? 'text' : 'password'}
                          value={state.key}
                          onChange={(e) => handleKeyChange(provider, e.target.value)}
                          placeholder={placeholder}
                          className="key-input"
                          disabled={state.isSaving || state.isDeleting}
                        />
                        <button
                          type="button"
                          onClick={() => toggleShowKey(provider)}
                          className="toggle-visibility"
                          aria-label={state.showKey ? 'Hide key' : 'Show key'}
                        >
                          {state.showKey ? '👁️' : '👁️‍🗨️'}
                        </button>
                      </div>

                      <div className="key-actions">
                        <button
                          onClick={() => handleSaveKey(provider)}
                          disabled={state.isSaving || state.isDeleting || !state.key.trim()}
                          className="save-key-button"
                        >
                          {state.isSaving ? 'Saving...' : 'Save Key'}
                        </button>

                        {state.hasKey && (
                          <button
                            onClick={() => handleDeleteKey(provider)}
                            disabled={state.isSaving || state.isDeleting}
                            className="delete-key-button"
                          >
                            {state.isDeleting ? 'Deleting...' : 'Delete'}
                          </button>
                        )}
                      </div>
                    </div>

                    {state.error && (
                      <div className="key-message error">⚠️ {state.error}</div>
                    )}

                    {state.success && (
                      <div className="key-message success">✅ {state.success}</div>
                    )}
                  </div>
                );
              })}
            </div>
          )}

          <div className="api-key-help">
            <h4>Getting API Keys:</h4>
            <ul>
              <li>
                <strong>OpenRouter:</strong>{' '}
                <a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer">
                  openrouter.ai/keys
                </a>
              </li>
              <li>
                <strong>OpenAI:</strong>{' '}
                <a href="https://platform.openai.com/api-keys" target="_blank" rel="noopener noreferrer">
                  platform.openai.com/api-keys
                </a>
              </li>
              <li>
                <strong>Anthropic:</strong>{' '}
                <a href="https://console.anthropic.com/settings/keys" target="_blank" rel="noopener noreferrer">
                  console.anthropic.com/settings/keys
                </a>
              </li>
              <li>
                <strong>Cohere:</strong>{' '}
                <a href="https://dashboard.cohere.com/api-keys" target="_blank" rel="noopener noreferrer">
                  dashboard.cohere.com/api-keys
                </a>
              </li>
            </ul>
          </div>
        </div>

        <div className="modal-footer">
          <button onClick={onClose} className="cancel-button">
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
