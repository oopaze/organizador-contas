import { apiRequest } from '../client';
import { Loan } from '../types';

export async function updateLoan(id: number, input: Partial<Loan>): Promise<Loan> {
  return apiRequest<Loan>(`/loans/loans/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  });
}
