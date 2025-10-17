/**
 * Tauri API utilities for invoking backend commands
 */

import { invoke } from '@tauri-apps/api/core';
import type {
  VerbRequest,
  VerbResponse,
  SampleRequest,
  SampleResponse,
  ExportRequest,
  ExportResponse,
  SessionSaveRequest,
  SessionLoadResponse,
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
 * Check if Tauri API is available (for development vs production)
 */
export function isTauriAvailable(): boolean {
  return '__TAURI__' in window;
}
