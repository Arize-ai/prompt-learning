/**
 * Main application component
 */

import { useState } from 'react';
import { ProviderForm } from './components/ProviderForm';
import { DistributionView } from './components/DistributionView';
import { ApiKeySettings } from './components/ApiKeySettings';
import { useVerbalize } from './hooks/useVerbalize';
import './App.css';

function App() {
  const {
    formState,
    updateField,
    verbalize,
    reset,
    isLoading,
    error,
    distribution,
  } = useVerbalize();

  const [showForm, setShowForm] = useState(true);
  const [showSettings, setShowSettings] = useState(false);

  const handleSubmit = async () => {
    await verbalize();
    // Auto-scroll to results if successful
    if (distribution) {
      setTimeout(() => {
        document.querySelector('.distribution-view')?.scrollIntoView({
          behavior: 'smooth',
          block: 'start',
        });
      }, 100);
    }
  };

  const handleReset = () => {
    reset();
    setShowForm(true);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div>
            <h1>🎲 Verbalized Sampling</h1>
            <p className="subtitle">
              Visualize probability distributions over LLM completions
            </p>
          </div>
          <button
            className="settings-button"
            onClick={() => setShowSettings(true)}
            aria-label="API Key Settings"
          >
            ⚙️ Settings
          </button>
        </div>
      </header>

      {/* API Key Settings Modal */}
      <ApiKeySettings
        isOpen={showSettings}
        onClose={() => setShowSettings(false)}
      />

      {/* Main Content */}
      <main className="app-main">
        {/* Provider Form Section */}
        <section className="form-section-container">
          <div className="section-header">
            <h2>Configuration</h2>
            {distribution && (
              <button
                className="toggle-button"
                onClick={() => setShowForm(!showForm)}
              >
                {showForm ? 'Hide Form' : 'Show Form'}
              </button>
            )}
          </div>

          {showForm && (
            <ProviderForm
              formState={formState}
              onUpdate={updateField}
              onSubmit={handleSubmit}
              isLoading={isLoading}
              error={error}
            />
          )}
        </section>

        {/* Distribution Results Section */}
        {distribution && (
          <section className="results-section">
            <div className="section-header">
              <h2>Results</h2>
              <button className="reset-button" onClick={handleReset}>
                New Distribution
              </button>
            </div>
            <DistributionView distribution={distribution} />
          </section>
        )}

        {/* Empty State */}
        {!distribution && !isLoading && (
          <div className="empty-state">
            <p>Configure your parameters and click "Generate Distribution" to start</p>
          </div>
        )}

        {/* Loading State */}
        {isLoading && (
          <div className="loading-state">
            <div className="spinner"></div>
            <p>Generating distribution...</p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <p>
          Powered by Tauri + React + FastAPI |{' '}
          <a
            href="https://github.com/Arize-ai/prompt-learning"
            target="_blank"
            rel="noopener noreferrer"
          >
            GitHub
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;
