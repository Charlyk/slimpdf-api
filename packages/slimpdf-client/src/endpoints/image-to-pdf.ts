/**
 * Image to PDF endpoint client
 */

import type {
  ImageToPdfResponse,
  ImageToPdfOptions,
  JobResult,
  PollOptions,
} from '../types.js';
import { request, type RequestContext } from './base.js';
import { createMultiFileFormData, appendFormFields, type FileInput } from '../utils/form-data.js';
import { JobsClient } from './jobs.js';

export class ImageToPdfClient {
  private jobs: JobsClient;

  constructor(private ctx: RequestContext) {
    this.jobs = new JobsClient(ctx);
  }

  /**
   * Submit images for PDF conversion
   * Returns immediately with a job ID. Images are added to the PDF in order.
   *
   * Supported formats: JPG, PNG, WebP, TIFF, BMP, GIF
   *
   * @param files - Image files to convert (in order)
   * @param options - Conversion options
   * @returns Job info with job_id and image_count
   */
  async submit(
    files: FileInput[],
    options: ImageToPdfOptions = {}
  ): Promise<ImageToPdfResponse> {
    const formData = createMultiFileFormData('files', files);

    appendFormFields(formData, {
      page_size: options.pageSize,
    });

    return request<ImageToPdfResponse>(this.ctx, 'POST', '/v1/image-to-pdf', {
      body: formData,
    });
  }

  /**
   * Submit images for PDF conversion and wait for completion
   * Convenience method that handles polling automatically.
   *
   * @param files - Image files to convert (in order)
   * @param options - Conversion options
   * @param pollOptions - Polling configuration
   * @returns Job result with status and download function
   */
  async submitAndWait(
    files: FileInput[],
    options: ImageToPdfOptions = {},
    pollOptions?: PollOptions
  ): Promise<JobResult> {
    const job = await this.submit(files, options);
    const status = await this.jobs.waitForCompletion(job.job_id, pollOptions);

    return {
      status,
      download: () => this.jobs.download(job.job_id),
    };
  }
}
