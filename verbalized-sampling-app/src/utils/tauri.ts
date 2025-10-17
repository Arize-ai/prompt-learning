/**
 * Tauri API utilities for invoking backend commands
 */

import { invoke } from '@tauri-apps/api/core';
import type { VerbRequest, VerbResponse } from '../types/contracts';

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
 * Check if Tauri API is available (for development vs production)
 */
export function isTauriAvailable(): boolean {
  return '__TAURI__' in window;
}
