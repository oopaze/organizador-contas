import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, delay } from '../mockData';

async function getActorMock(id: number): Promise<Actor> {
  await delay();
  const actor = mockActors.find(a => a.id === id);
  if (!actor) throw new Error('Actor not found');
  return actor;
}

async function getActorReal(id: number): Promise<Actor> {
  return apiRequest<Actor>(`/transactions/actors/${id}/`);
}

export async function getActor(id: number): Promise<Actor> {
  return USE_MOCK_API ? await getActorMock(id) : await getActorReal(id);
}
