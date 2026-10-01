import { apiRequest } from '../client';
import { Loan } from '../types';

export interface LoanFilters {
  actor_id?: number;
  status?: 'active' | 'settled' | 'cancelled';
}

export async function getLoans(filters: LoanFilters = {}): Promise<Loan[]> {
  const params = new URLSearchParams();
  if (filters.actor_id) params.append('actor_id', String(filters.actor_id));
  if (filters.status) params.append('status', filters.status);
  const query = params.toString();
  return apiRequest<Loan[]>(`/loans/loans/${query ? `?${query}` : ''}`);
}
