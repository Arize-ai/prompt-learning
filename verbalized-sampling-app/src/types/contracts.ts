/**
 * TypeScript type definitions generated from JSON Schema contracts
 * These types define the IPC interface between Tauri frontend and Python sidecar
 */

// ============================================================================
// Provider Types
// ============================================================================

export type Provider = 'openai' | 'anthropic' | 'cohere' | 'local_vllm' | 'openrouter';

export const PROVIDER_MAX_K: Record<Provider, number> = {
  openai: 100,
  anthropic: 100,
  cohere: 100,
  local_vllm: 500,
  openrouter: 100,
};

// ============================================================================
// Verbalize Endpoint
// ============================================================================

export interface VerbRequest {
  prompt: string;
  k: number;
  tau?: number;
  temperature?: number;
  seed?: number | null;
  model: string;
  provider: Provider;
  include_token_probabilities?: boolean;
}

export interface TokenProbability {
  token: string;
  prob: number;
}

export interface CompletionResponse {
  text: string;
  probability: number;
  rank: number;
  token_probabilities?: TokenProbability[];
}

export interface TraceMetadata {
  model: string;
  provider: string;
  api_latency_ms: number;
  token_count: number;
  k?: number;
  tau?: number;
  temperature?: number;
  seed?: number;
  api_version?: string;
}

export interface VerbResponse {
  distribution_id: string;
  completions: CompletionResponse[];
  trace_metadata: TraceMetadata;
  timestamp: string;
}

// ============================================================================
// Sample Endpoint
// ============================================================================

export interface SampleRequest {
  distribution_id: string;
  seed?: number | null;
}

export interface SampleResponse {
  selected_completion: string;
  selection_index: number;
  probability?: number;
  seed_used?: number;
}

// ============================================================================
// Export Endpoint
// ============================================================================

export type ExportFormat = 'csv' | 'jsonl';

export interface ExportRequest {
  distribution_ids: string[];
  format: ExportFormat;
  include_metadata?: boolean;
  output_path: string;
}

export interface ExportResponse {
  file_path: string;
  row_count: number;
  file_size_bytes: number;
  format?: ExportFormat;
  included_metadata?: boolean;
}

// ============================================================================
// Session Persistence
// ============================================================================

export interface SessionDistribution {
  distribution_id: string;
  prompt: string;
  completions: CompletionResponse[];
  trace_metadata: TraceMetadata;
  timestamp?: string;
}

export interface SessionSaveRequest {
  distributions: SessionDistribution[];
  notes?: string;
  output_path: string;
}

export interface SessionLoadResponse {
  session_id: string;
  distributions: SessionDistribution[];
  notes?: string;
  app_version: string;
  schema_version: string;
  created_at: string;
  loaded_at?: string;
}

// ============================================================================
// Validation Helpers
// ============================================================================

export function validateVerbRequest(request: VerbRequest): string | null {
  // Validate prompt
  if (!request.prompt || request.prompt.length === 0) {
    return 'Prompt cannot be empty';
  }
  if (request.prompt.length > 100000) {
    return 'Prompt exceeds maximum length of 100,000 characters';
  }

  // Validate k based on provider
  const maxK = PROVIDER_MAX_K[request.provider];
  if (request.k < 1) {
    return 'k must be at least 1';
  }
  if (request.k > maxK) {
    return `k exceeds maximum of ${maxK} for provider ${request.provider}`;
  }

  // Validate tau
  const tau = request.tau ?? 1.0;
  if (tau < 0.0 || tau > 10.0) {
    return 'tau must be between 0.0 and 10.0';
  }

  // Validate temperature
  const temperature = request.temperature ?? 0.8;
  if (temperature < 0.0 || temperature > 2.0) {
    return 'temperature must be between 0.0 and 2.0';
  }

  // Validate model
  if (!request.model || request.model.length === 0) {
    return 'Model cannot be empty';
  }

  return null;
}

export function validateExportRequest(request: ExportRequest): string | null {
  if (!request.distribution_ids || request.distribution_ids.length === 0) {
    return 'At least one distribution ID required';
  }
  if (!request.output_path || request.output_path.length === 0) {
    return 'Output path cannot be empty';
  }
  return null;
}

export function validateSessionSaveRequest(request: SessionSaveRequest): string | null {
  if (!request.distributions || request.distributions.length === 0) {
    return 'At least one distribution required';
  }
  if (!request.output_path || request.output_path.length === 0) {
    return 'Output path cannot be empty';
  }
  if (request.notes && request.notes.length > 10000) {
    return 'Notes exceed maximum length of 10,000 characters';
  }
  return null;
}

// ============================================================================
// Default Values
// ============================================================================

export const DEFAULT_TAU = 1.0;
export const DEFAULT_TEMPERATURE = 0.8;
export const DEFAULT_INCLUDE_TOKEN_PROBABILITIES = false;
export const DEFAULT_INCLUDE_METADATA = true;
export const DEFAULT_SCHEMA_VERSION = 'v1';
