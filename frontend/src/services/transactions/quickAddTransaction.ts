import { apiRequest } from '../client';
import { QuickAddInput, QuickAddResult } from '../types';

export async function quickAddTransaction(input: QuickAddInput): Promise<QuickAddResult> {
  return apiRequest<QuickAddResult>('/transactions/transactions/quick_add/', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
