import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, delay } from '../mockData';

async function updateActorMock(id: number, data: Partial<Actor>): Promise<Actor> {
  await delay();
  const index = mockActors.findIndex(a => a.id === id);
  if (index === -1) throw new Error('Actor not found');
  mockActors[index] = { ...mockActors[index], ...data };
  return mockActors[index];
}

async function updateActorReal(id: number, data: Partial<Actor>): Promise<Actor> {
  return apiRequest<Actor>(`/transactions/actors/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function updateActor(id: number, data: Partial<Actor>): Promise<Actor> {
  return USE_MOCK_API ? await updateActorMock(id, data) : await updateActorReal(id, data);
}
