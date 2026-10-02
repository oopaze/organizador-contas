import { apiRequest, USE_MOCK_API } from '../client';
import { User } from '../types';
import { mockUsers, delay } from '../mockData';

async function getCurrentUserMock(): Promise<User> {
  await delay();
  return mockUsers[0];
}

async function getCurrentUserReal(): Promise<User> {
  return apiRequest<User>('/user/me/');
}

export async function getCurrentUser(): Promise<User> {
  return USE_MOCK_API ? await getCurrentUserMock() : await getCurrentUserReal();
}
