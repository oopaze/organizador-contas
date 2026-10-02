import { apiRequest } from '../client';
import { PurchaseIntention, PurchaseIntentionInput } from '../types';

export async function updateIntention(
  id: number,
  data: Partial<PurchaseIntentionInput>
): Promise<PurchaseIntention> {
  return apiRequest<PurchaseIntention>(`/planning/intentions/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}
