/**
 * SlimPDF Client - Main client class
 */

import type { ClientOptions } from './types.js';
import type { RequestContext } from './endpoints/base.js';
import { CompressClient } from './endpoints/compress.js';
import { MergeClient } from './endpoints/merge.js';
import { ImageToPdfClient } from './endpoints/image-to-pdf.js';
import { JobsClient } from './endpoints/jobs.js';
import { AuthClient } from './endpoints/auth.js';
import { BillingClient } from './endpoints/billing.js';
import { ApiKeysClient } from './endpoints/api-keys.js';

/**
 * SlimPDF API Client
 *
 * @example
 * ```typescript
 * const client = new SlimPdfClient({
 *   baseUrl: 'https://api.slimpdf.io',
 *   accessToken: 'your-jwt-or-api-key', // optional
 * });
 *
 * // Compress a PDF
 * const result = await client.compress.submitAndWait(file, { quality: 'high' });
 * const blob = await result.download();
 *
 * // Merge PDFs
 * const merged = await client.merge.submitAndWait([pdf1, pdf2]);
 *
 * // Convert images to PDF
 * const pdf = await client.imageToPdf.submitAndWait(images, { pageSize: 'a4' });
 * ```
 */
export class SlimPdfClient {
  private _accessToken: string | undefined;
  private readonly ctx: RequestContext;

  /** Compress PDF files */
  readonly compress: CompressClient;

  /** Merge multiple PDFs */
  readonly merge: MergeClient;

  /** Convert images to PDF */
  readonly imageToPdf: ImageToPdfClient;

  /** Check job status and download files */
  readonly jobs: JobsClient;

  /** Authentication (Google OAuth) */
  readonly auth: AuthClient;

  /** Billing (Stripe) */
  readonly billing: BillingClient;

  /** API key management (Pro) */
  readonly apiKeys: ApiKeysClient;

  constructor(options: ClientOptions) {
    this._accessToken = options.accessToken;

    // Create request context
    this.ctx = {
      baseUrl: options.baseUrl.replace(/\/$/, ''), // Remove trailing slash
      getAccessToken: () => this._accessToken,
      fetch: options.fetch || globalThis.fetch.bind(globalThis),
    };

    // Initialize endpoint clients
    this.compress = new CompressClient(this.ctx);
    this.merge = new MergeClient(this.ctx);
    this.imageToPdf = new ImageToPdfClient(this.ctx);
    this.jobs = new JobsClient(this.ctx);
    this.auth = new AuthClient(this.ctx);
    this.billing = new BillingClient(this.ctx);
    this.apiKeys = new ApiKeysClient(this.ctx);
  }

  /**
   * Set the access token for authenticated requests
   * Can be a JWT token or an API key (sk_live_...)
   */
  setAccessToken(token: string): void {
    this._accessToken = token;
  }

  /**
   * Clear the access token
   */
  clearAccessToken(): void {
    this._accessToken = undefined;
  }

  /**
   * Check if the client has an access token set
   */
  get isAuthenticated(): boolean {
    return !!this._accessToken;
  }
}
