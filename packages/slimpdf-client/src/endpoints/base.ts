/**
 * Base HTTP client for API requests
 */

import { handleErrorResponse } from '../errors.js';

export interface RequestContext {
  baseUrl: string;
  getAccessToken: () => string | undefined;
  fetch: typeof fetch;
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
  } = {}
): Promise<T> {
  const { body, query, headers: customHeaders } = options;

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
  return response.json() as Promise<T>;
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

  const headers: Record<string, string> = {};
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
