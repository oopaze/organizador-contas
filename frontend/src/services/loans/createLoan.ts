import { apiRequest } from '../client';
import { Loan, CreateLoanInput } from '../types';

export async function createLoan(input: CreateLoanInput): Promise<Loan> {
  return apiRequest<Loan>('/loans/loans/', {
    method: 'POST',
    body: JSON.stringify(input),
  });
}
