/**
 * Auth endpoint client
 */

import type { AuthTokenResponse, MeResponse, VerifyResponse } from '../types.js';
import { request, type RequestContext } from './base.js';

export class AuthClient {
  constructor(private ctx: RequestContext) {}

  /**
   * Authenticate with Google OAuth
   * Exchange a Google ID token for a SlimPDF JWT access token.
   *
   * @param idToken - Google ID token from Google Sign-In
   * @returns Auth response with access_token and user info
   */
  async loginWithGoogle(idToken: string): Promise<AuthTokenResponse> {
    return request<AuthTokenResponse>(this.ctx, 'POST', '/v1/auth/google', {
      body: { id_token: idToken },
    });
  }

  /**
   * Get current user info and usage stats
   * Requires authentication (JWT or API key)
   *
   * @returns User info and usage statistics
   */
  async getCurrentUser(): Promise<MeResponse> {
    return request<MeResponse>(this.ctx, 'GET', '/v1/auth/me');
  }

  /**
   * Verify current token validity
   * Works with or without authentication.
   *
   * @returns Token verification status
   */
  async verifyToken(): Promise<VerifyResponse> {
    return request<VerifyResponse>(this.ctx, 'GET', '/v1/auth/verify');
  }
}
