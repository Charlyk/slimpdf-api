/**
 * SlimPDF Client Types
 */

// ============================================================================
// Enums / Union Types
// ============================================================================

/**
 * Compression quality preset.
 * Higher compression = lower quality output.
 *
 * - `low`: Maximum compression, 50 DPI - smallest files, works on already-compressed PDFs
 * - `medium`: High compression, 72 DPI - good balance (default)
 * - `high`: Medium compression, 100 DPI - better quality
 * - `maximum`: Light compression, 150 DPI - best quality
 *
 * Note: If compression would increase file size, the original is returned.
 */
export type CompressionQuality = 'low' | 'medium' | 'high' | 'maximum';
export type PageSize = 'a4' | 'letter' | 'original';
export type JobStatus = 'pending' | 'processing' | 'completed' | 'failed';
export type ToolType = 'compress' | 'merge' | 'image_to_pdf';
export type Plan = 'free' | 'pro';
export type BillingInterval = 'month' | 'year';
export type ApiEnvironment = 'development' | 'production';

// ============================================================================
// API URL Constants
// ============================================================================

/** Production API URL */
export const API_URL_PRODUCTION = 'https://api.slimpdf.io';

/** Development API URL */
export const API_URL_DEVELOPMENT = 'https://dev.api.slimpdf.io';

// ============================================================================
// Client Configuration
// ============================================================================

/** Supported languages for API responses */
export type SupportedLanguage = 'en' | 'es' | 'fr' | 'de' | 'pt' | 'it' | 'ja' | 'zh' | 'ko';

export interface ClientOptions {
  /**
   * Base URL of the SlimPDF API.
   * If not provided, will be determined by the `environment` option.
   * @example 'https://api.slimpdf.io'
   */
  baseUrl?: string;
  /**
   * API environment to use. Defaults to 'production'.
   * - 'production': https://api.slimpdf.io
   * - 'development': https://dev.api.slimpdf.io
   * Ignored if `baseUrl` is provided.
   */
  environment?: ApiEnvironment;
  /** Optional access token (JWT or API key) for authenticated requests */
  accessToken?: string;
  /** Optional language for API responses (default: 'en') */
  language?: SupportedLanguage;
  /** Optional custom fetch function for testing or custom implementations */
  fetch?: typeof fetch;
}

export interface PollOptions {
  /** Maximum number of polling attempts (default: 60) */
  maxAttempts?: number;
  /** Initial polling interval in milliseconds (default: 1000) */
  initialIntervalMs?: number;
  /** Maximum polling interval in milliseconds (default: 5000) */
  maxIntervalMs?: number;
  /** Callback when status changes */
  onStatusChange?: (status: JobStatusResponse) => void;
}

// ============================================================================
// User & Authentication
// ============================================================================

export interface User {
  id: string;
  email: string | null;
  name: string | null;
  plan: Plan;
  is_pro: boolean;
}

export interface UsageStats {
  used: number;
  limit: number;
  remaining: number;
}

export interface UsageResponse {
  compress: UsageStats;
  merge: UsageStats;
  image_to_pdf: UsageStats;
}

export interface MeResponse {
  user: User;
  usage: UsageResponse;
}

export interface AuthTokenResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
  is_new_user: boolean;
}

export interface VerifyResponse {
  authenticated: boolean;
  user_id: string | null;
  plan: Plan;
  is_pro: boolean;
}

// ============================================================================
// Rate Limiting
// ============================================================================

/**
 * Rate limit information returned from API responses.
 * Only present for free tier users - Pro users have unlimited access.
 */
export interface RateLimitInfo {
  /** Maximum requests allowed per day */
  limit: number;
  /** Requests remaining in current period */
  remaining: number;
  /** Unix timestamp when the limit resets (midnight UTC) */
  resetAt: number;
}

// ============================================================================
// Job Responses
// ============================================================================

export interface CompressResponse {
  job_id: string;
  status: string;
  message: string;
  /** Rate limit info (only present for free tier users) */
  rateLimit?: RateLimitInfo;
}

export interface MergeResponse {
  job_id: string;
  status: string;
  message: string;
  file_count: number;
  /** Rate limit info (only present for free tier users) */
  rateLimit?: RateLimitInfo;
}

export interface ImageToPdfResponse {
  job_id: string;
  status: string;
  message: string;
  image_count: number;
  /** Rate limit info (only present for free tier users) */
  rateLimit?: RateLimitInfo;
}

export interface JobStatusResponse {
  job_id: string;
  status: JobStatus;
  tool: ToolType;
  original_size: number | null;
  output_size: number | null;
  reduction_percent: number | null;
  download_url: string | null;
  expires_at: string | null;
  error_message: string | null;
  created_at: string;
  completed_at: string | null;
}

// ============================================================================
// Billing
// ============================================================================

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface PortalResponse {
  portal_url: string;
}

// ============================================================================
// API Keys
// ============================================================================

export interface ApiKey {
  id: string;
  name: string;
  key_prefix: string;
  created_at: string;
  last_used_at: string | null;
  is_active: boolean;
}

export interface ApiKeyCreateResponse {
  id: string;
  name: string;
  /** The full API key - only shown once! */
  key: string;
  key_prefix: string;
  created_at: string;
  message: string;
}

// ============================================================================
// Request Options
// ============================================================================

export interface CompressOptions {
  /** Compression quality preset */
  quality?: CompressionQuality;
  /** Target file size in MB (Pro only) */
  targetSizeMb?: number;
}

export interface ImageToPdfOptions {
  /** Page size for the output PDF */
  pageSize?: PageSize;
}

// ============================================================================
// Result Types (for submitAndWait convenience methods)
// ============================================================================

export interface JobResult {
  status: JobStatusResponse;
  /** Download the processed file as a Blob */
  download: () => Promise<Blob>;
}

// ============================================================================
// Error Response
// ============================================================================

export interface ErrorResponse {
  detail: string;
}
