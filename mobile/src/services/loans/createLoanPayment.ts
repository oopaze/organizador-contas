import { apiRequest } from '../client';
import { LoanPayment, CreateLoanPaymentInput } from '../types';

export async function createLoanPayment(input: CreateLoanPaymentInput): Promise<LoanPayment> {
  return apiRequest<LoanPayment>('/loans/loan_payments/', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
