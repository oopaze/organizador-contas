import { apiRequest, USE_MOCK_API } from '../client';
import { User } from '../types';
import { mockUsers, delay } from '../mockData';

async function updateProfileMock(data: Partial<User>): Promise<User> {
  await delay();
  mockUsers[0] = { ...mockUsers[0], ...data };
  return mockUsers[0];
}

async function updateProfileReal(data: Partial<User>): Promise<User> {
  return apiRequest<User>('/user/me/profile/', {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

export async function updateProfile(data: Partial<User>): Promise<User> {
  return USE_MOCK_API ? await updateProfileMock(data) : await updateProfileReal(data);
}
