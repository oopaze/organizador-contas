import { apiRequest, USE_MOCK_API } from '../client';
import { Actor } from '../types';
import { mockActors, delay } from '../mockData';

async function getActorsMock(): Promise<Actor[]> {
  await delay();
  return [...mockActors];
}

async function getActorsReal(): Promise<Actor[]> {
  return apiRequest<Actor[]>('/transactions/actors/');
}

export async function getActors(): Promise<Actor[]> {
  return USE_MOCK_API ? await getActorsMock() : await getActorsReal();
}
