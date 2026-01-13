/**
 * Base HTTP client for API requests
 */

import { handleErrorResponse } from '../errors.js';
import type { RateLimitInfo } from '../types.js';

export interface RequestContext {
  baseUrl: string;
  getAccessToken: () => string | undefined;
  getLanguage: () => string;
  fetch: typeof fetch;
}

/**
 * Parse rate limit headers from response.
 * Returns undefined if headers are not present (Pro users).
 */
function parseRateLimitHeaders(response: Response): RateLimitInfo | undefined {
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const resetAt = response.headers.get('X-RateLimit-Reset');

  // Pro users don't have rate limit headers
  if (!limit || !remaining || !resetAt) {
    return undefined;
  }

  return {
    limit: parseInt(limit, 10),
    remaining: parseInt(remaining, 10),
    resetAt: parseInt(resetAt, 10),
  };
}

/**
 * Make an authenticated request
 */
export async function request<T>(
  ctx: RequestContext,
  method: string,
  path: string,
  options: {
    body?: FormData | Record<string, unknown>;
    query?: Record<string, string | number | boolean | undefined>;
    headers?: Record<string, string>;
    /** Include rate limit info from response headers */
    includeRateLimit?: boolean;
  } = {}
): Promise<T> {
  const { body, query, headers: customHeaders, includeRateLimit } = options;

  // Build URL with query params
  let url = `${ctx.baseUrl}${path}`;
  if (query) {
    const params = new URLSearchParams();
    Object.entries(query).forEach(([key, value]) => {
      if (value !== undefined) {
        params.append(key, String(value));
      }
    });
    const queryString = params.toString();
    if (queryString) {
      url += `?${queryString}`;
    }
  }

  // Build headers
  const headers: Record<string, string> = { ...customHeaders };

  // Add language header
  headers['X-Language'] = ctx.getLanguage();

  // Add auth header if token exists
  const token = ctx.getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  // Don't set Content-Type for FormData (browser sets it with boundary)
  if (body && !(body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  // Make request
  const response = await ctx.fetch(url, {
    method,
    headers,
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  });

  // Handle errors
  if (!response.ok) {
    await handleErrorResponse(response);
  }

  // Parse JSON response
  const data = await response.json() as T;

  // Optionally include rate limit info
  if (includeRateLimit) {
    const rateLimit = parseRateLimitHeaders(response);
    if (rateLimit) {
      (data as Record<string, unknown>).rateLimit = rateLimit;
    }
  }

  return data;
}

/**
 * Make a request that returns a blob (for file downloads)
 */
export async function requestBlob(
  ctx: RequestContext,
  method: string,
  path: string
): Promise<Blob> {
  const url = `${ctx.baseUrl}${path}`;

  const headers: Record<string, string> = {
    'X-Language': ctx.getLanguage(),
  };
  const token = ctx.getAccessToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await ctx.fetch(url, {
    method,
    headers,
  });

  if (!response.ok) {
    await handleErrorResponse(response);
  }

  return response.blob();
}
