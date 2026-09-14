import { apiRequest } from '../client';
import { TransactionDetail } from '../types';

export interface EnsureSalaryResult {
  salary: TransactionDetail | null;
}

export async function ensureSalary(month: string): Promise<EnsureSalaryResult> {
  return apiRequest<EnsureSalaryResult>('/transactions/transactions/ensure_salary/', {
    method: 'POST',
    body: JSON.stringify({ month }),
  });
}
