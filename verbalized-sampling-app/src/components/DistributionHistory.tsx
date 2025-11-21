/**
 * Distribution History Sidebar
 * Shows list of past distributions with selection
 */

import { useState } from 'react';
import type { Distribution, DistributionListItem } from '../types/models';

interface DistributionHistoryProps {
  distributions: Distribution[];
  currentDistributionId?: string;
  onSelect: (distributionId: string) => void;
  onDelete?: (distributionId: string) => void;
}

export function DistributionHistory({
  distributions,
  currentDistributionId,
  onSelect,
  onDelete,
}: DistributionHistoryProps) {
  const [searchTerm, setSearchTerm] = useState('');

  const distributionItems: DistributionListItem[] = distributions.map((dist) => ({
    id: dist.id,
    prompt: dist.prompt,
    promptPreview: dist.prompt.length > 100 ? dist.prompt.substring(0, 100) + '...' : dist.prompt,
    completionCount: dist.completions.length,
    timestamp: dist.timestamp,
    provider: dist.traceMetadata.provider,
    model: dist.traceMetadata.model,
  }));

  const filteredItems = searchTerm
    ? distributionItems.filter(
        (item) =>
          item.promptPreview.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.provider.toLowerCase().includes(searchTerm.toLowerCase()) ||
          item.model.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : distributionItems;

  const formatTimestamp = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="distribution-history">
      <div className="history-header">
        <h2>History</h2>
        <span className="count-badge">{distributions.length}</span>
      </div>

      <div className="search-box">
        <input
          type="text"
          placeholder="Search distributions..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-input"
        />
      </div>

      <div className="history-list">
        {filteredItems.length === 0 ? (
          <div className="empty-state">
            {searchTerm ? 'No matching distributions' : 'No distributions yet'}
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className={`history-item ${item.id === currentDistributionId ? 'active' : ''}`}
              onClick={() => onSelect(item.id)}
            >
              <div className="item-header">
                <span className="provider-badge">{item.provider}</span>
                <span className="timestamp">{formatTimestamp(item.timestamp)}</span>
              </div>

              <div className="item-prompt">{item.promptPreview}</div>

              <div className="item-footer">
                <span className="model-name">{item.model}</span>
                <span className="completion-count">{item.completionCount} completions</span>
              </div>

              {onDelete && (
                <button
                  className="delete-button"
                  onClick={(e) => {
                    e.stopPropagation();
                    onDelete(item.id);
                  }}
                  aria-label="Delete distribution"
                >
                  ×
                </button>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
