/**
 * Distribution visualization component
 */

import type { VerbResponse } from '../types/contracts';
import { CompletionCard } from './CompletionCard';

interface DistributionViewProps {
  distribution: VerbResponse;
}

export function DistributionView({ distribution }: DistributionViewProps) {
  const { completions, trace_metadata, timestamp } = distribution;

  return (
    <div className="distribution-view">
      {/* Header with Metadata */}
      <div className="distribution-header">
        <h2>Distribution Results</h2>
        <div className="metadata">
          <span className="metadata-item">
            <strong>Model:</strong> {trace_metadata.model}
          </span>
          <span className="metadata-item">
            <strong>Provider:</strong> {trace_metadata.provider}
          </span>
          <span className="metadata-item">
            <strong>Completions:</strong> {completions.length}
          </span>
          <span className="metadata-item">
            <strong>Latency:</strong> {trace_metadata.api_latency_ms.toFixed(0)}ms
          </span>
          {trace_metadata.temperature && (
            <span className="metadata-item">
              <strong>Temp:</strong> {trace_metadata.temperature.toFixed(2)}
            </span>
          )}
          {trace_metadata.tau && (
            <span className="metadata-item">
              <strong>Tau:</strong> {trace_metadata.tau.toFixed(2)}
            </span>
          )}
        </div>
        <div className="timestamp">
          Generated: {new Date(timestamp).toLocaleString()}
        </div>
      </div>

      {/* Completions Grid */}
      <div className="completions-grid">
        {completions.map((completion, index) => (
          <CompletionCard
            key={`${distribution.distribution_id}-${index}`}
            completion={completion}
          />
        ))}
      </div>

      {/* Distribution Stats */}
      <div className="distribution-stats">
        <h3>Distribution Statistics</h3>
        <div className="stats-grid">
          <div className="stat-item">
            <span className="stat-label">Total Tokens:</span>
            <span className="stat-value">{trace_metadata.token_count}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Entropy:</span>
            <span className="stat-value">
              {calculateEntropy(completions).toFixed(3)} bits
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Max Probability:</span>
            <span className="stat-value">
              {(Math.max(...completions.map((c) => c.probability)) * 100).toFixed(
                1
              )}
              %
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Min Probability:</span>
            <span className="stat-value">
              {(Math.min(...completions.map((c) => c.probability)) * 100).toFixed(
                1
              )}
              %
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

/**
 * Calculate Shannon entropy of probability distribution
 */
function calculateEntropy(completions: { probability: number }[]): number {
  return -completions.reduce((entropy, c) => {
    if (c.probability > 0) {
      return entropy + c.probability * Math.log2(c.probability);
    }
    return entropy;
  }, 0);
}
