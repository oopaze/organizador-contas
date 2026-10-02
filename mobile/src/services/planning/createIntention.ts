import { apiRequest } from '../client';
import { PurchaseIntention, PurchaseIntentionInput } from '../types';

export async function createIntention(data: PurchaseIntentionInput): Promise<PurchaseIntention> {
  return apiRequest<PurchaseIntention>('/planning/intentions/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
