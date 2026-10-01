import { apiRequest } from '../client';

export async function deleteLoanPayment(id: number): Promise<void> {
  await apiRequest<void>(`/loans/loan_payments/${id}/`, { method: 'DELETE' });
}
