/**
 * Sample Button Component
 * Sample from a distribution with optional seed
 */

import { useState } from 'react';
import type { Distribution } from '../types/models';
import { invokeSample } from '../utils/tauri';

interface SampleButtonProps {
  distribution: Distribution;
  className?: string;
}

export function SampleButton({
  distribution,
  className = ''
}: SampleButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [seed, setSeed] = useState<string>('');
  const [isSampling, setIsSampling] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{
    text: string;
    probability?: number;
    index: number;
  } | null>(null);

  const handleSample = async () => {
    try {
      setIsSampling(true);
      setError(null);
      setResult(null);

      // Parse seed
      const seedValue = seed.trim() ? parseInt(seed) : undefined;

      // Invoke sample command
      const response = await invokeSample(distribution.id, seedValue);

      // Find the completion
      const completion = distribution.completions[response.selection_index];

      setResult({
        text: response.selected_completion,
        probability: response.probability ?? completion?.probability,
        index: response.selection_index,
      });
    } catch (err) {
      console.error('Sampling error:', err);
      setError(err instanceof Error ? err.message : 'Sampling failed');
    } finally {
      setIsSampling(false);
    }
  };

  const handleClose = () => {
    setIsOpen(false);
    setResult(null);
    setError(null);
    setSeed('');
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`sample-trigger-button ${className}`}
      >
        🎲 Sample
      </button>

      {isOpen && (
        <div className="modal-overlay" onClick={handleClose}>
          <div className="modal-content sample-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Sample from Distribution</h3>
              <button
                onClick={handleClose}
                className="modal-close"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <p className="sample-info">
                Sample a completion from the distribution based on its probability
              </p>

              {!result && (
                <div className="sample-controls">
                  <div className="form-group">
                    <label htmlFor="sample-seed">Random Seed (optional)</label>
                    <input
                      id="sample-seed"
                      type="number"
                      value={seed}
                      onChange={(e) => setSeed(e.target.value)}
                      placeholder="Leave empty for random"
                    />
                    <p className="help-text">
                      Use the same seed to get reproducible samples
                    </p>
                  </div>

                  <button
                    onClick={handleSample}
                    disabled={isSampling}
                    className="sample-button"
                  >
                    {isSampling ? 'Sampling...' : '🎲 Sample Now'}
                  </button>
                </div>
              )}

              {result && (
                <div className="sample-result">
                  <div className="result-header">
                    <h4>Sampled Completion</h4>
                    <div className="result-meta">
                      <span className="result-rank">Rank #{result.index + 1}</span>
                      {result.probability !== undefined && (
                        <span className="result-probability">
                          {(result.probability * 100).toFixed(2)}%
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="result-text">
                    {result.text}
                  </div>

                  <button
                    onClick={() => {
                      setResult(null);
                      setError(null);
                    }}
                    className="sample-again-button"
                  >
                    Sample Again
                  </button>
                </div>
              )}

              {error && (
                <div className="sample-error">
                  ⚠️ {error}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                onClick={handleClose}
                className="cancel-button"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
