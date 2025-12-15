/**
 * UI State Models
 * Application-specific types for frontend state management
 */

import type {
  Provider,
  CompletionResponse,
  TraceMetadata,
  VerbResponse,
} from './contracts';

// Re-export for external use
export type { SessionDistribution } from './contracts';

// ============================================================================
// Distribution State
// ============================================================================

export interface Distribution {
  id: string;
  prompt: string;
  completions: CompletionResponse[];
  traceMetadata: TraceMetadata;
  timestamp: Date;
  isLoading?: boolean;
  error?: string;
}

export interface DistributionListItem {
  id: string;
  prompt: string;
  promptPreview: string; // First 100 chars
  completionCount: number;
  timestamp: Date;
  provider: string;
  model: string;
}

// ============================================================================
// Provider Configuration
// ============================================================================

export interface ProviderConfig {
  provider: Provider;
  apiKey?: string;
  baseUrl?: string;
  defaultModel: string;
  availableModels: string[];
  isConfigured: boolean;
  isAvailable: boolean;
}

export interface ProviderSettings {
  openai?: ProviderConfig;
  anthropic?: ProviderConfig;
  cohere?: ProviderConfig;
  local_vllm?: ProviderConfig;
}

// ============================================================================
// Session State
// ============================================================================

export interface Session {
  id: string;
  distributions: Distribution[];
  notes?: string;
  appVersion: string;
  schemaVersion: string;
  createdAt: Date;
  loadedAt?: Date;
  isModified: boolean;
  filePath?: string;
}

export interface SessionListItem {
  id: string;
  distributionCount: number;
  notesPreview?: string;
  createdAt: Date;
  filePath: string;
}

// ============================================================================
// Application State
// ============================================================================

export interface AppState {
  currentDistribution?: Distribution;
  distributionHistory: DistributionListItem[];
  currentSession?: Session;
  providerSettings: ProviderSettings;
  preferences: UserPreferences;
  sidecarStatus: SidecarStatus;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  defaultProvider: Provider;
  defaultK: number;
  defaultTau: number;
  defaultTemperature: number;
  autoSaveSession: boolean;
  showTokenProbabilities: boolean;
  exportFormat: 'csv' | 'jsonl';
  includeMetadataInExport: boolean;
}

export interface SidecarStatus {
  isRunning: boolean;
  isHealthy: boolean;
  lastHealthCheck?: Date;
  error?: string;
}

// ============================================================================
// UI Component Props
// ============================================================================

export interface DistributionViewProps {
  distribution: Distribution;
  onSample?: (distributionId: string, seed?: number) => void;
  onExport?: (distributionId: string) => void;
  onDelete?: (distributionId: string) => void;
}

export interface CompletionCardProps {
  completion: CompletionResponse;
  distributionId: string;
  isSelected?: boolean;
  onSelect?: () => void;
}

export interface ProviderFormProps {
  provider: Provider;
  config: ProviderConfig;
  onSave: (config: ProviderConfig) => void;
  onTest?: (config: ProviderConfig) => Promise<boolean>;
}

export interface SessionManagerProps {
  session?: Session;
  onSave: (session: Session) => void;
  onLoad: (filePath: string) => void;
  onNew: () => void;
}

// ============================================================================
// Form State
// ============================================================================

export interface VerbFormState {
  prompt: string;
  k: number;
  tau: number;
  temperature: number;
  seed?: number;
  model: string;
  provider: Provider;
  includeTokenProbabilities: boolean;
  errors: Record<string, string>;
  isSubmitting: boolean;
}

export interface ExportFormState {
  selectedDistributions: string[];
  format: 'csv' | 'jsonl';
  includeMetadata: boolean;
  outputPath: string;
  isExporting: boolean;
  error?: string;
}

export interface SampleFormState {
  distributionId: string;
  seed?: number;
  isLoading: boolean;
  result?: {
    completion: string;
    probability?: number;
    index: number;
  };
}

// ============================================================================
// Utility Functions
// ============================================================================

export function createDistributionFromResponse(response: VerbResponse): Distribution {
  return {
    id: response.distribution_id,
    prompt: '', // Will be set from request
    completions: response.completions,
    traceMetadata: response.trace_metadata,
    timestamp: new Date(response.timestamp),
    isLoading: false,
  };
}

export function createDistributionListItem(distribution: Distribution): DistributionListItem {
  const promptPreview =
    distribution.prompt.length > 100
      ? distribution.prompt.substring(0, 100) + '...'
      : distribution.prompt;

  return {
    id: distribution.id,
    prompt: distribution.prompt,
    promptPreview,
    completionCount: distribution.completions.length,
    timestamp: distribution.timestamp,
    provider: distribution.traceMetadata.provider,
    model: distribution.traceMetadata.model,
  };
}

export function createSessionFromDistributions(
  distributions: Distribution[],
  notes?: string
): Session {
  return {
    id: crypto.randomUUID(),
    distributions,
    notes,
    appVersion: '1.0.0', // Should come from app config
    schemaVersion: 'v1',
    createdAt: new Date(),
    isModified: false,
  };
}

export function getDefaultVerbFormState(provider: Provider): VerbFormState {
  return {
    prompt: '',
    k: 5,
    tau: 1.0,
    temperature: 0.8,
    model: '',
    provider,
    includeTokenProbabilities: false,
    errors: {},
    isSubmitting: false,
  };
}

export function getDefaultUserPreferences(): UserPreferences {
  return {
    theme: 'system',
    defaultProvider: 'openai',
    defaultK: 5,
    defaultTau: 1.0,
    defaultTemperature: 0.8,
    autoSaveSession: true,
    showTokenProbabilities: false,
    exportFormat: 'jsonl',
    includeMetadataInExport: true,
  };
}
