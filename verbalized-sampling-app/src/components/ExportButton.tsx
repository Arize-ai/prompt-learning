/**
 * Export Button Component
 * Export single or multiple distributions to CSV/JSONL
 */

import { useState } from 'react';
import { save } from '@tauri-apps/plugin-dialog';
import type { ExportFormat, ExportRequest } from '../types/contracts';
import { invokeExport } from '../utils/tauri';

interface ExportButtonProps {
  distributionIds: string[];
  label?: string;
  className?: string;
}

export function ExportButton({
  distributionIds,
  label = '📤 Export',
  className = ''
}: ExportButtonProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [format, setFormat] = useState<ExportFormat>('jsonl');
  const [includeMetadata, setIncludeMetadata] = useState(true);
  const [isExporting, setIsExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const handleExport = async () => {
    if (distributionIds.length === 0) {
      setError('No distributions selected');
      return;
    }

    try {
      setIsExporting(true);
      setError(null);
      setSuccess(null);

      // Determine file extension
      const extension = format === 'csv' ? 'csv' : 'jsonl';
      const defaultPath = distributionIds.length === 1
        ? `distribution.${extension}`
        : `distributions.${extension}`;

      // Open save dialog
      const filePath = await save({
        defaultPath,
        filters: [{
          name: format.toUpperCase(),
          extensions: [extension]
        }]
      });

      if (!filePath) {
        setIsExporting(false);
        return; // User cancelled
      }

      // Prepare export request
      const request: ExportRequest = {
        distribution_ids: distributionIds,
        format,
        include_metadata: includeMetadata,
        output_path: filePath,
      };

      // Execute export
      const response = await invokeExport(request);

      setSuccess(`Exported ${response.row_count} rows to ${response.file_path}`);

      // Auto-close success message and modal after 2 seconds
      setTimeout(() => {
        setSuccess(null);
        setIsOpen(false);
      }, 2000);
    } catch (err) {
      console.error('Export error:', err);
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <>
      <button
        onClick={() => setIsOpen(true)}
        className={`export-trigger-button ${className}`}
        disabled={distributionIds.length === 0}
      >
        {label}
      </button>

      {isOpen && (
        <div className="modal-overlay" onClick={() => setIsOpen(false)}>
          <div className="modal-content export-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Export Distributions</h3>
              <button
                onClick={() => setIsOpen(false)}
                className="modal-close"
                aria-label="Close"
              >
                ×
              </button>
            </div>

            <div className="modal-body">
              <p className="export-info">
                Exporting {distributionIds.length} distribution{distributionIds.length !== 1 ? 's' : ''}
              </p>

              <div className="export-options">
                <div className="form-group">
                  <label htmlFor="export-format">Format</label>
                  <select
                    id="export-format"
                    value={format}
                    onChange={(e) => setFormat(e.target.value as ExportFormat)}
                  >
                    <option value="jsonl">JSONL (Newline-delimited JSON)</option>
                    <option value="csv">CSV (Comma-separated values)</option>
                  </select>
                </div>

                <div className="checkbox-group">
                  <label>
                    <input
                      type="checkbox"
                      checked={includeMetadata}
                      onChange={(e) => setIncludeMetadata(e.target.checked)}
                    />
                    <span>Include metadata (model, provider, timestamps)</span>
                  </label>
                </div>
              </div>

              {error && (
                <div className="export-message error">
                  ⚠️ {error}
                </div>
              )}

              {success && (
                <div className="export-message success">
                  ✅ {success}
                </div>
              )}
            </div>

            <div className="modal-footer">
              <button
                onClick={() => setIsOpen(false)}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                onClick={handleExport}
                disabled={isExporting}
                className="confirm-button"
              >
                {isExporting ? 'Exporting...' : 'Export'}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
