import { apiRequest } from '../client';

export async function deleteIntention(id: number): Promise<void> {
  return apiRequest<void>(`/planning/intentions/${id}/`, { method: 'DELETE' });
}
