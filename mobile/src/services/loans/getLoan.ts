import { apiRequest } from '../client';
import { Loan } from '../types';

export async function getLoan(id: number): Promise<Loan> {
  return apiRequest<Loan>(`/loans/loans/${id}/`);
}
