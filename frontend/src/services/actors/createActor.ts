import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, incrementIds, delay } from '../mockData';

async function createActorMock(data: Omit<Actor, 'id'>): Promise<Actor> {
  await delay();
  const newActor: Actor = {
    ...data,
    id: incrementIds.nextActorId++,
  };
  mockActors.push(newActor);
  return newActor;
}

async function createActorReal(data: Omit<Actor, 'id'>): Promise<Actor> {
  return apiRequest<Actor>('/transactions/actors/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function createActor(data: Omit<Actor, 'id'>): Promise<Actor> {
  return USE_MOCK_API ? await createActorMock(data) : await createActorReal(data);
}