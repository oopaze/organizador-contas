import { apiRequest } from '../client';
import { LoanPayment } from '../types';

export interface LoanPaymentFilters {
  loan_id?: number;
  paid_at_month?: number;
  paid_at_year?: number;
}

export async function getLoanPayments(filters: LoanPaymentFilters = {}): Promise<LoanPayment[]> {
  const params = new URLSearchParams();
  if (filters.loan_id) params.append('loan_id', String(filters.loan_id));
  if (filters.paid_at_month) params.append('paid_at__month', String(filters.paid_at_month));
  if (filters.paid_at_year) params.append('paid_at__year', String(filters.paid_at_year));
  const query = params.toString();
  return apiRequest<LoanPayment[]>(`/loans/loan_payments/${query ? `?${query}` : ''}`);
}
