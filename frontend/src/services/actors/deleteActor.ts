import { apiRequest, USE_MOCK_API } from '../client';
import { mockActors, delay } from '../mockData';

async function deleteActorMock(id: number): Promise<void> {
  await delay();
  const index = mockActors.findIndex(a => a.id === id);
  if (index === -1) throw new Error('Actor not found');
  mockActors.splice(index, 1);
}

async function deleteActorReal(id: number): Promise<void> {
  return apiRequest<void>(`/transactions/actors/${id}/`, {
    method: 'DELETE',
  });
}

export async function deleteActor(id: number): Promise<void> {
  return USE_MOCK_API ? await deleteActorMock(id) : await deleteActorReal(id);
}
