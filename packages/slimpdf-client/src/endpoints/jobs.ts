/**
 * Jobs endpoint client - status checking and downloads
 */

import type { JobStatusResponse, PollOptions } from '../types.js';
import { request, requestBlob, type RequestContext } from './base.js';
import { pollUntilComplete } from '../utils/polling.js';

export class JobsClient {
  constructor(private ctx: RequestContext) {}

  /**
   * Get the status of a job
   */
  async getStatus(jobId: string): Promise<JobStatusResponse> {
    return request<JobStatusResponse>(this.ctx, 'GET', `/v1/status/${jobId}`);
  }

  /**
   * Download the processed file
   * @throws {JobExpiredError} if the download link has expired
   * @throws {NotFoundError} if the job or file is not found
   */
  async download(jobId: string): Promise<Blob> {
    return requestBlob(this.ctx, 'GET', `/v1/download/${jobId}`);
  }

  /**
   * Wait for a job to complete with exponential backoff polling
   * @throws {JobFailedError} if the job fails
   * @throws {PollingTimeoutError} if polling times out
   */
  async waitForCompletion(
    jobId: string,
    options?: PollOptions
  ): Promise<JobStatusResponse> {
    return pollUntilComplete(
      jobId,
      () => this.getStatus(jobId),
      options
    );
  }
}
