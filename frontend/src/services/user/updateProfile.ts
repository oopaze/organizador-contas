import { apiRequest, USE_MOCK_API } from '../client';
import { User } from '../types';
import { mockUsers, delay } from '../mockData';

export interface ProfileUpdateInput {
  first_name?: string;
  last_name?: string;
  bio?: string;
  salary?: number;
  salary_day?: number;
  modo_on?: boolean;
  monthly_spending_goal?: number | null;
  monthly_savings_goal?: number | null;
  monthly_essentials_goal?: number | null;
}

async function updateProfileMock(data: ProfileUpdateInput): Promise<User> {
  await delay();
  mockUsers[0] = { ...mockUsers[0], ...data };
  return mockUsers[0];
}

async function updateProfileReal(data: ProfileUpdateInput): Promise<User> {
  return apiRequest<User>('/user/me/profile/', {
    method: 'PATCH',
    body: JSON.stringify(data),
  });
}

export async function updateProfile(data: ProfileUpdateInput): Promise<User> {
  return USE_MOCK_API ? await updateProfileMock(data) : await updateProfileReal(data);
}
