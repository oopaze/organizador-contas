import { apiRequest } from '../client';
import { LedgerResult } from '../types';

export interface LedgerFilters {
  start?: string;
  end?: string;
  include_unpaid?: boolean;
}

export async function getLedger(filters: LedgerFilters = {}): Promise<LedgerResult> {
  const params = new URLSearchParams();
  if (filters.start) params.append('start', filters.start);
  if (filters.end) params.append('end', filters.end);
  if (filters.include_unpaid === false) params.append('include_unpaid', 'false');
  const query = params.toString();
  return apiRequest<LedgerResult>(`/transactions/transactions/ledger/${query ? `?${query}` : ''}`);
}
