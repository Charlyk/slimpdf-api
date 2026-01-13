/**
 * Auth endpoint client
 */

import type { AuthTokenResponse, MeResponse, VerifyResponse } from '../types.js';
import { request, type RequestContext } from './base.js';

export class AuthClient {
  constructor(private ctx: RequestContext) {}

  /**
   * Authenticate with Firebase
   * Exchange a Firebase ID token for a SlimPDF JWT access token.
   * Supports all Firebase auth providers (Google, Apple, email/password, etc.).
   *
   * @param idToken - Firebase ID token from Firebase Auth
   * @returns Auth response with access_token and user info
   */
  async loginWithFirebase(idToken: string): Promise<AuthTokenResponse> {
    return request<AuthTokenResponse>(this.ctx, 'POST', '/v1/auth/firebase', {
      body: { id_token: idToken },
    });
  }

  /**
   * @deprecated Use `loginWithFirebase` instead. This method will be removed in a future version.
   */
  async loginWithGoogle(idToken: string): Promise<AuthTokenResponse> {
    return this.loginWithFirebase(idToken);
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
