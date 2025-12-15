/**
 * Tauri API utilities for invoking backend commands
 */

import { invoke } from '@tauri-apps/api/core';
import type {
  VerbRequest,
  VerbResponse,
  SampleResponse,
  ExportRequest,
  ExportResponse,
  SessionSaveRequest,
  SessionLoadResponse,
  ApiKeyResponse,
  ApiProvider,
} from '../types/contracts';

/**
 * Invoke verbalize command to generate weighted completion distribution
 */
export async function invokeVerbalize(
  params: VerbRequest
): Promise<VerbResponse> {
  try {
    const response = await invoke<VerbResponse>('verbalize', { params });
    return response;
  } catch (error) {
    console.error('Verbalize command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Invoke sample command to sample from a distribution
 */
export async function invokeSample(
  distributionId: string,
  seed?: number
): Promise<SampleResponse> {
  try {
    const response = await invoke<SampleResponse>('sample', {
      distributionId,
      seed: seed ?? null,
    });
    return response;
  } catch (error) {
    console.error('Sample command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Invoke export command to export distributions to file
 */
export async function invokeExport(
  params: ExportRequest
): Promise<ExportResponse> {
  try {
    const response = await invoke<ExportResponse>('export', { request: params });
    return response;
  } catch (error) {
    console.error('Export command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Invoke session_save command to save current session
 */
export async function invokeSessionSave(
  params: SessionSaveRequest
): Promise<string> {
  try {
    const filePath = await invoke<string>('session_save', { request: params });
    return filePath;
  } catch (error) {
    console.error('Session save command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Invoke session_load command to load a saved session
 */
export async function invokeSessionLoad(
  filePath: string
): Promise<SessionLoadResponse> {
  try {
    const response = await invoke<SessionLoadResponse>('session_load', {
      filePath,
    });
    return response;
  } catch (error) {
    console.error('Session load command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Store an API key securely in Stronghold
 */
export async function invokeStoreApiKey(
  provider: ApiProvider,
  key: string
): Promise<void> {
  try {
    await invoke<void>('store_api_key', { provider, key });
  } catch (error) {
    console.error('Store API key command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Retrieve an API key from Stronghold
 */
export async function invokeGetApiKey(
  provider: ApiProvider
): Promise<string> {
  try {
    const key = await invoke<string>('get_api_key', { provider });
    return key;
  } catch (error) {
    console.error('Get API key command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Check if an API key exists for a provider
 */
export async function invokeCheckApiKey(
  provider: ApiProvider
): Promise<ApiKeyResponse> {
  try {
    const response = await invoke<ApiKeyResponse>('check_api_key', { provider });
    return response;
  } catch (error) {
    console.error('Check API key command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Delete an API key from Stronghold
 */
export async function invokeDeleteApiKey(
  provider: ApiProvider
): Promise<void> {
  try {
    await invoke<void>('delete_api_key', { provider });
  } catch (error) {
    console.error('Delete API key command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * List all providers with stored API keys
 */
export async function invokeListApiKeys(): Promise<ApiKeyResponse[]> {
  try {
    const response = await invoke<ApiKeyResponse[]>('list_api_keys');
    return response;
  } catch (error) {
    console.error('List API keys command failed:', error);
    throw new Error(error instanceof Error ? error.message : String(error));
  }
}

/**
 * Check if Tauri API is available (for development vs production)
 */
export function isTauriAvailable(): boolean {
  return '__TAURI__' in window;
}
