/**
 * Merge endpoint client
 */

import type { MergeResponse, JobResult, PollOptions } from '../types.js';
import { request, type RequestContext } from './base.js';
import { createMultiFileFormData, type FileInput } from '../utils/form-data.js';
import { JobsClient } from './jobs.js';

export class MergeClient {
  private jobs: JobsClient;

  constructor(private ctx: RequestContext) {
    this.jobs = new JobsClient(ctx);
  }

  /**
   * Submit PDFs for merging
   * Returns immediately with a job ID. Files are merged in the order provided.
   *
   * @param files - PDF files to merge (in order)
   * @returns Job info with job_id and file_count
   */
  async submit(files: FileInput[]): Promise<MergeResponse> {
    const formData = createMultiFileFormData('files', files);

    return request<MergeResponse>(this.ctx, 'POST', '/v1/merge', {
      body: formData,
    });
  }

  /**
   * Submit PDFs for merging and wait for completion
   * Convenience method that handles polling automatically.
   *
   * @param files - PDF files to merge (in order)
   * @param pollOptions - Polling configuration
   * @returns Job result with status and download function
   */
  async submitAndWait(
    files: FileInput[],
    pollOptions?: PollOptions
  ): Promise<JobResult> {
    const job = await this.submit(files);
    const status = await this.jobs.waitForCompletion(job.job_id, pollOptions);

    return {
      status,
      download: () => this.jobs.download(job.job_id),
    };
  }
}
