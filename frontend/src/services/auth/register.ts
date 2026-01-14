import { apiRequest, USE_MOCK_API } from '../client';
import { RegisterRequest, User } from '../types';
import { mockUsers, incrementIds, delay } from '../mockData';

async function registerMock(data: RegisterRequest): Promise<User> {
  await delay();
  
  if (mockUsers.find(u => u.email === data.email)) {
    throw new Error('User with this email already exists');
  }

  const newUser: User = {
    id: incrementIds.nextUserId++,
    email: data.email,
    first_name: data.first_name,
    last_name: data.last_name,
  };

  mockUsers.push(newUser);
  return newUser;
}

async function registerReal(data: RegisterRequest): Promise<User> {
  return apiRequest<User>('/user/register/', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export async function register(data: RegisterRequest): Promise<User> {
  return USE_MOCK_API ? await registerMock(data) : await registerReal(data);
}