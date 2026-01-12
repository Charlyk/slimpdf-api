/**
 * Compress endpoint client
 */

import type {
  CompressResponse,
  CompressOptions,
  JobResult,
  PollOptions,
} from '../types.js';
import { request, type RequestContext } from './base.js';
import { createFileFormData, appendFormFields, type FileInput } from '../utils/form-data.js';
import { JobsClient } from './jobs.js';

export class CompressClient {
  private jobs: JobsClient;

  constructor(private ctx: RequestContext) {
    this.jobs = new JobsClient(ctx);
  }

  /**
   * Submit a PDF for compression
   * Returns immediately with a job ID. Use jobs.getStatus() or jobs.waitForCompletion() to track progress.
   *
   * @param file - PDF file to compress
   * @param options - Compression options
   * @returns Job info with job_id
   */
  async submit(
    file: FileInput,
    options: CompressOptions = {}
  ): Promise<CompressResponse> {
    const formData = createFileFormData('file', file);

    appendFormFields(formData, {
      quality: options.quality,
      target_size_mb: options.targetSizeMb,
    });

    return request<CompressResponse>(this.ctx, 'POST', '/v1/compress', {
      body: formData,
    });
  }

  /**
   * Submit a PDF for compression and wait for completion
   * Convenience method that handles polling automatically.
   *
   * @param file - PDF file to compress
   * @param options - Compression options
   * @param pollOptions - Polling configuration
   * @returns Job result with status and download function
   */
  async submitAndWait(
    file: FileInput,
    options: CompressOptions = {},
    pollOptions?: PollOptions
  ): Promise<JobResult> {
    const job = await this.submit(file, options);
    const status = await this.jobs.waitForCompletion(job.job_id, pollOptions);

    return {
      status,
      download: () => this.jobs.download(job.job_id),
    };
  }
}
