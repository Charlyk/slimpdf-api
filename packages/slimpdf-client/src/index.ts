/**
 * SlimPDF Client SDK
 *
 * @packageDocumentation
 */

// Main client
export { SlimPdfClient } from './client.js';

// Types
export type {
  // Config
  ClientOptions,
  PollOptions,
  // Enums
  CompressionQuality,
  PageSize,
  JobStatus,
  ToolType,
  Plan,
  BillingInterval,
  // User & Auth
  User,
  UsageStats,
  UsageResponse,
  MeResponse,
  AuthTokenResponse,
  VerifyResponse,
  // Jobs
  CompressResponse,
  MergeResponse,
  ImageToPdfResponse,
  JobStatusResponse,
  JobResult,
  // Billing
  CheckoutResponse,
  PortalResponse,
  // API Keys
  ApiKey,
  ApiKeyCreateResponse,
  // Options
  CompressOptions,
  ImageToPdfOptions,
  // Errors
  ErrorResponse,
} from './types.js';

// Errors
export {
  SlimPdfError,
  AuthenticationError,
  ForbiddenError,
  NotFoundError,
  JobExpiredError,
  FileSizeError,
  RateLimitError,
  ValidationError,
  ProcessingError,
  PollingTimeoutError,
  JobFailedError,
} from './errors.js';

// Endpoint clients (for advanced usage)
export { CompressClient } from './endpoints/compress.js';
export { MergeClient } from './endpoints/merge.js';
export { ImageToPdfClient } from './endpoints/image-to-pdf.js';
export { JobsClient } from './endpoints/jobs.js';
export { AuthClient } from './endpoints/auth.js';
export { BillingClient } from './endpoints/billing.js';
export { ApiKeysClient } from './endpoints/api-keys.js';
