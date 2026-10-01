import { apiRequest } from '../client';

export async function deleteLoan(id: number): Promise<void> {
  await apiRequest<void>(`/loans/loans/${id}/`, { method: 'DELETE' });
}
