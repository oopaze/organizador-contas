import { apiRequest } from '../client';
import { PurchaseIntention } from '../types';

export async function convertIntention(
  id: number,
  data: { category?: string; paid_at?: string } = {}
): Promise<PurchaseIntention> {
  return apiRequest<PurchaseIntention>(`/planning/intentions/${id}/convert/`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}
