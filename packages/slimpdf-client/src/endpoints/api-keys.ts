/**
 * API Keys endpoint client
 */

import type { ApiKey, ApiKeyCreateResponse } from '../types.js';
import { request, type RequestContext } from './base.js';

export class ApiKeysClient {
  constructor(private ctx: RequestContext) {}

  /**
   * List all API keys for the current user
   * Requires Pro subscription.
   *
   * @returns List of API keys (without the full key value)
   */
  async list(): Promise<ApiKey[]> {
    return request<ApiKey[]>(this.ctx, 'GET', '/v1/keys');
  }

  /**
   * Create a new API key
   * Requires Pro subscription. Maximum 5 active keys per user.
   *
   * IMPORTANT: The full key is only returned once! Store it securely.
   *
   * @param name - Optional name for the API key
   * @returns The created API key with full key value (shown only once!)
   */
  async create(name?: string): Promise<ApiKeyCreateResponse> {
    return request<ApiKeyCreateResponse>(this.ctx, 'POST', '/v1/keys', {
      body: { name: name || 'Default' },
    });
  }

  /**
   * Revoke an API key
   * Requires Pro subscription.
   *
   * @param keyId - ID of the API key to revoke
   */
  async revoke(keyId: string): Promise<void> {
    await request<{ message: string }>(this.ctx, 'DELETE', `/v1/keys/${keyId}`);
  }
}
