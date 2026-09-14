import { apiRequest } from '../client';
import { PurchaseIntention } from '../types';

export async function getIntentions(options: {
  month?: string;
  start?: string;
  end?: string;
  status?: string;
} = {}): Promise<PurchaseIntention[]> {
  const query = new URLSearchParams();
  if (options.month) query.append('month', options.month);
  if (options.start) query.append('start', options.start);
  if (options.end) query.append('end', options.end);
  if (options.status) query.append('status', options.status);
  const suffix = query.toString();
  return apiRequest<PurchaseIntention[]>(`/planning/intentions/${suffix ? `?${suffix}` : ''}`);
}
