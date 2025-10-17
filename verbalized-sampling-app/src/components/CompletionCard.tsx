/**
 * Completion card component for displaying individual completions
 */

import React, { useState } from 'react';
import type { CompletionResponse } from '../types/contracts';

interface CompletionCardProps {
  completion: CompletionResponse;
}

export function CompletionCard({ completion }: CompletionCardProps) {
  const [showTokenProbs, setShowTokenProbs] = useState(false);

  const probabilityPercent = (completion.probability * 100).toFixed(2);
  const hasTokenProbs =
    completion.token_probabilities && completion.token_probabilities.length > 0;

  // Get probability color based on value
  const getProbabilityColor = (prob: number): string => {
    if (prob > 0.3) return '#22c55e'; // Green
    if (prob > 0.15) return '#eab308'; // Yellow
    if (prob > 0.05) return '#f97316'; // Orange
    return '#ef4444'; // Red
  };

  const probColor = getProbabilityColor(completion.probability);

  return (
    <div className="completion-card">
      {/* Header with rank and probability */}
      <div className="completion-header">
        <div className="rank-badge">#{completion.rank}</div>
        <div
          className="probability-badge"
          style={{ backgroundColor: probColor }}
        >
          {probabilityPercent}%
        </div>
      </div>

      {/* Completion text */}
      <div className="completion-text">{completion.text}</div>

      {/* Probability bar */}
      <div className="probability-bar-container">
        <div
          className="probability-bar"
          style={{
            width: `${completion.probability * 100}%`,
            backgroundColor: probColor,
          }}
        />
      </div>

      {/* Token probabilities toggle */}
      {hasTokenProbs && (
        <div className="token-probs-section">
          <button
            className="token-probs-toggle"
            onClick={() => setShowTokenProbs(!showTokenProbs)}
          >
            {showTokenProbs ? '▼' : '▶'} Token Probabilities (
            {completion.token_probabilities!.length})
          </button>

          {showTokenProbs && (
            <div className="token-probs-list">
              {completion.token_probabilities!.map((tp, idx) => (
                <div key={idx} className="token-prob-item">
                  <span className="token-text">"{tp.token}"</span>
                  <span className="token-prob">
                    {(tp.prob * 100).toFixed(1)}%
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
