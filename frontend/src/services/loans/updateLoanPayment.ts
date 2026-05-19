import { apiRequest } from '../client';
import { LoanPayment } from '../types';

export async function updateLoanPayment(id: number, input: Partial<LoanPayment>): Promise<LoanPayment> {
  return apiRequest<LoanPayment>(`/loans/loan_payments/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(input),
  });
}
