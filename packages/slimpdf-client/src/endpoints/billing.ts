/**
 * Billing endpoint client
 */

import type { BillingInterval, CheckoutResponse, PortalResponse } from '../types.js';
import { request, type RequestContext } from './base.js';

export class BillingClient {
  constructor(private ctx: RequestContext) {}

  /**
   * Create a Stripe checkout session for Pro subscription
   * Requires authentication.
   *
   * @param interval - Billing interval ('month' or 'year')
   * @returns Checkout URL to redirect the user to
   */
  async createCheckout(interval: BillingInterval): Promise<CheckoutResponse> {
    return request<CheckoutResponse>(this.ctx, 'POST', '/v1/billing/checkout', {
      query: { interval },
    });
  }

  /**
   * Create a Stripe customer portal session
   * Requires authentication and an existing Stripe customer.
   *
   * @returns Portal URL to redirect the user to
   */
  async createPortalSession(): Promise<PortalResponse> {
    return request<PortalResponse>(this.ctx, 'POST', '/v1/billing/portal');
  }
}
