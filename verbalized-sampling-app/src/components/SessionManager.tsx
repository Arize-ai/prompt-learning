/**
 * Session Management UI
 * Save/load sessions with auto-save toggle
 */

import { useState } from 'react';
import { open, save } from '@tauri-apps/plugin-dialog';
import type { Distribution, Session } from '../types/models';
import type { SessionSaveRequest, SessionLoadResponse } from '../types/contracts';
import { invokeSessionSave, invokeSessionLoad } from '../utils/tauri';

interface SessionManagerProps {
  distributions: Distribution[];
  currentSession?: Session;
  autoSave: boolean;
  onAutoSaveToggle: (enabled: boolean) => void;
  onSessionLoaded: (session: SessionLoadResponse) => void;
  onSessionSaved: (filePath: string) => void;
}

export function SessionManager({
  distributions,
  currentSession,
  autoSave,
  onAutoSaveToggle,
  onSessionLoaded,
  onSessionSaved,
}: SessionManagerProps) {
  const [notes, setNotes] = useState(currentSession?.notes || '');
  const [isSaving, setIsSaving] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const handleSave = async () => {
    if (distributions.length === 0) {
      setError('No distributions to save');
      return;
    }

    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);

      // Open save dialog
      const filePath = await save({
        defaultPath: 'session.json',
        filters: [{
          name: 'Session',
          extensions: ['json']
        }]
      });

      if (!filePath) {
        setIsSaving(false);
        return; // User cancelled
      }

      // Prepare session data
      const sessionData: SessionSaveRequest = {
        distributions: distributions.map(dist => ({
          distribution_id: dist.id,
          prompt: dist.prompt,
          completions: dist.completions,
          trace_metadata: dist.traceMetadata,
          timestamp: dist.timestamp.toISOString(),
        })),
        notes: notes || undefined,
        output_path: filePath,
      };

      // Save session
      const savedPath = await invokeSessionSave(sessionData);

      setSuccessMessage(`Session saved to ${savedPath}`);
      onSessionSaved(savedPath);

      // Clear message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Save session error:', err);
      setError(err instanceof Error ? err.message : 'Failed to save session');
    } finally {
      setIsSaving(false);
    }
  };

  const handleLoad = async () => {
    try {
      setIsLoading(true);
      setError(null);
      setSuccessMessage(null);

      // Open file dialog
      const selected = await open({
        multiple: false,
        filters: [{
          name: 'Session',
          extensions: ['json']
        }]
      });

      if (!selected || typeof selected !== 'string') {
        setIsLoading(false);
        return; // User cancelled
      }

      // Load session
      const session = await invokeSessionLoad(selected);

      setNotes(session.notes || '');
      setSuccessMessage(`Loaded ${session.distributions.length} distributions from session`);
      onSessionLoaded(session);

      // Clear message after 3 seconds
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      console.error('Load session error:', err);
      setError(err instanceof Error ? err.message : 'Failed to load session');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="session-manager">
      <div className="session-header">
        <h3>Session Management</h3>
        {currentSession && (
          <span className="session-info">
            {distributions.length} distribution{distributions.length !== 1 ? 's' : ''}
          </span>
        )}
      </div>

      <div className="session-controls">
        <div className="session-buttons">
          <button
            onClick={handleSave}
            disabled={isSaving || distributions.length === 0}
            className="session-button save-button"
          >
            {isSaving ? 'Saving...' : '💾 Save Session'}
          </button>

          <button
            onClick={handleLoad}
            disabled={isLoading}
            className="session-button load-button"
          >
            {isLoading ? 'Loading...' : '📂 Load Session'}
          </button>
        </div>

        <div className="auto-save-toggle">
          <label>
            <input
              type="checkbox"
              checked={autoSave}
              onChange={(e) => onAutoSaveToggle(e.target.checked)}
            />
            <span>Auto-save after each generation</span>
          </label>
        </div>
      </div>

      <div className="session-notes">
        <label htmlFor="session-notes">Session Notes</label>
        <textarea
          id="session-notes"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="Add notes about this session..."
          rows={3}
        />
      </div>

      {error && (
        <div className="session-message error">
          ⚠️ {error}
        </div>
      )}

      {successMessage && (
        <div className="session-message success">
          ✅ {successMessage}
        </div>
      )}
    </div>
  );
}
