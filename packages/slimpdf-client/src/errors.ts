/**
 * SlimPDF Client Error Classes
 */

/**
 * Base error class for all SlimPDF errors
 */
export class SlimPdfError extends Error {
  constructor(
    public readonly statusCode: number,
    message: string,
    public readonly detail?: string
  ) {
    super(message);
    this.name = 'SlimPdfError';
    Object.setPrototypeOf(this, SlimPdfError.prototype);
  }
}

/**
 * Thrown when authentication fails (401)
 */
export class AuthenticationError extends SlimPdfError {
  constructor(message: string = 'Authentication required', detail?: string) {
    super(401, message, detail);
    this.name = 'AuthenticationError';
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}

/**
 * Thrown when access is forbidden (403)
 */
export class ForbiddenError extends SlimPdfError {
  constructor(message: string = 'Access forbidden', detail?: string) {
    super(403, message, detail);
    this.name = 'ForbiddenError';
    Object.setPrototypeOf(this, ForbiddenError.prototype);
  }
}

/**
 * Thrown when a resource is not found (404)
 */
export class NotFoundError extends SlimPdfError {
  constructor(message: string = 'Resource not found', detail?: string) {
    super(404, message, detail);
    this.name = 'NotFoundError';
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

/**
 * Thrown when a download link has expired (410)
 */
export class JobExpiredError extends SlimPdfError {
  constructor(message: string = 'Download link has expired', detail?: string) {
    super(410, message, detail);
    this.name = 'JobExpiredError';
    Object.setPrototypeOf(this, JobExpiredError.prototype);
  }
}

/**
 * Thrown when file size exceeds the limit (413)
 */
export class FileSizeError extends SlimPdfError {
  constructor(message: string = 'File size exceeds limit', detail?: string) {
    super(413, message, detail);
    this.name = 'FileSizeError';
    Object.setPrototypeOf(this, FileSizeError.prototype);
  }
}

/**
 * Thrown when rate limit is exceeded (429)
 */
export class RateLimitError extends SlimPdfError {
  constructor(message: string = 'Rate limit exceeded', detail?: string) {
    super(429, message, detail);
    this.name = 'RateLimitError';
    Object.setPrototypeOf(this, RateLimitError.prototype);
  }
}

/**
 * Thrown when the request is invalid (400)
 */
export class ValidationError extends SlimPdfError {
  constructor(message: string = 'Invalid request', detail?: string) {
    super(400, message, detail);
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * Thrown when job processing fails (500)
 */
export class ProcessingError extends SlimPdfError {
  constructor(message: string = 'Processing failed', detail?: string) {
    super(500, message, detail);
    this.name = 'ProcessingError';
    Object.setPrototypeOf(this, ProcessingError.prototype);
  }
}

/**
 * Thrown when polling times out
 */
export class PollingTimeoutError extends SlimPdfError {
  constructor(
    public readonly jobId: string,
    message: string = 'Polling timed out'
  ) {
    super(408, message);
    this.name = 'PollingTimeoutError';
    Object.setPrototypeOf(this, PollingTimeoutError.prototype);
  }
}

/**
 * Thrown when job fails during processing
 */
export class JobFailedError extends SlimPdfError {
  constructor(
    public readonly jobId: string,
    public readonly errorMessage: string
  ) {
    super(500, `Job ${jobId} failed: ${errorMessage}`);
    this.name = 'JobFailedError';
    Object.setPrototypeOf(this, JobFailedError.prototype);
  }
}

/**
 * Parse API error response and throw appropriate error
 */
export async function handleErrorResponse(response: Response): Promise<never> {
  let detail: string | undefined;

  try {
    const body = await response.json();
    detail = body.detail || body.message || JSON.stringify(body);
  } catch {
    detail = await response.text().catch(() => undefined);
  }

  const message = detail || response.statusText || 'Request failed';

  switch (response.status) {
    case 400:
      throw new ValidationError(message, detail);
    case 401:
      throw new AuthenticationError(message, detail);
    case 403:
      throw new ForbiddenError(message, detail);
    case 404:
      throw new NotFoundError(message, detail);
    case 410:
      throw new JobExpiredError(message, detail);
    case 413:
      throw new FileSizeError(message, detail);
    case 429:
      throw new RateLimitError(message, detail);
    case 500:
    case 502:
    case 503:
    case 504:
      throw new ProcessingError(message, detail);
    default:
      throw new SlimPdfError(response.status, message, detail);
  }
}
