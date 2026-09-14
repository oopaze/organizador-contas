import { apiRequest } from '../client';
import { TransactionDetail } from '../types';

export async function ensureCardBills(month: string): Promise<TransactionDetail[]> {
  const result = await apiRequest<{ bills: TransactionDetail[] }>(
    '/transactions/transactions/ensure_card_bills/',
    { method: 'POST', body: JSON.stringify({ month }) }
  );
  return result.bills;
}
