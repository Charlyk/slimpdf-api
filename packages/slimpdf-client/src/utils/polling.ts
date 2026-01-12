/**
 * Polling utility with exponential backoff
 */

import type { JobStatusResponse, PollOptions } from '../types.js';
import { JobFailedError, PollingTimeoutError } from '../errors.js';

const DEFAULT_MAX_ATTEMPTS = 60;
const DEFAULT_INITIAL_INTERVAL_MS = 1000;
const DEFAULT_MAX_INTERVAL_MS = 5000;

/**
 * Calculate next polling interval with exponential backoff
 */
function getNextInterval(
  currentInterval: number,
  maxInterval: number
): number {
  // Exponential backoff with 1.5x multiplier
  const nextInterval = Math.min(currentInterval * 1.5, maxInterval);
  // Add some jitter (±10%)
  const jitter = nextInterval * 0.1 * (Math.random() * 2 - 1);
  return Math.round(nextInterval + jitter);
}

/**
 * Wait for a specified duration
 */
function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Poll until job completes or fails
 */
export async function pollUntilComplete(
  jobId: string,
  getStatus: () => Promise<JobStatusResponse>,
  options: PollOptions = {}
): Promise<JobStatusResponse> {
  const {
    maxAttempts = DEFAULT_MAX_ATTEMPTS,
    initialIntervalMs = DEFAULT_INITIAL_INTERVAL_MS,
    maxIntervalMs = DEFAULT_MAX_INTERVAL_MS,
    onStatusChange,
  } = options;

  let attempts = 0;
  let currentInterval = initialIntervalMs;
  let lastStatus: JobStatusResponse | null = null;

  while (attempts < maxAttempts) {
    const status = await getStatus();

    // Notify on status change
    if (onStatusChange && status.status !== lastStatus?.status) {
      onStatusChange(status);
    }
    lastStatus = status;

    // Check for terminal states
    if (status.status === 'completed') {
      return status;
    }

    if (status.status === 'failed') {
      throw new JobFailedError(jobId, status.error_message || 'Unknown error');
    }

    // Still processing, wait and retry
    attempts++;
    await sleep(currentInterval);
    currentInterval = getNextInterval(currentInterval, maxIntervalMs);
  }

  throw new PollingTimeoutError(
    jobId,
    `Job ${jobId} did not complete within ${maxAttempts} polling attempts`
  );
}
