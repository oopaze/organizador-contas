import { apiRequest } from '../client';
import { LoanStats } from '../types';

export async function getLoanStats(): Promise<LoanStats> {
  return apiRequest<LoanStats>('/loans/loans/stats/');
}
