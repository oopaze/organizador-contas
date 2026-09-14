import { apiRequest } from '../client';
import { PurchaseIntention } from '../types';

export async function getIntentions(month?: string): Promise<PurchaseIntention[]> {
  const query = month ? `?month=${encodeURIComponent(month)}` : '';
  return apiRequest<PurchaseIntention[]>(`/planning/intentions/${query}`);
}
