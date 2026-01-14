import { apiRequest, tokenManager, USE_MOCK_API } from '../client';
import { LoginRequest, LoginResponse } from '../types';
import { mockUsers, delay } from '../mockData';

async function loginMock(credentials: LoginRequest): Promise<LoginResponse> {
  await delay();
  const user = mockUsers.find(u => u.email === credentials.email);
  
  if (!user || credentials.password !== 'password123') {
    throw new Error('Invalid email or password');
  }

  return {
    access_token: 'mock_access_token_' + Date.now(),
    refresh_token: 'mock_refresh_token_' + Date.now(),
    user,
  };
}

async function loginReal(credentials: LoginRequest): Promise<LoginResponse> {
  return apiRequest<LoginResponse>('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(credentials),
  });
}

export async function login(credentials: LoginRequest): Promise<LoginResponse> {
  const response = USE_MOCK_API ? await loginMock(credentials) : await loginReal(credentials);
  tokenManager.setTokens(response.access_token, response.refresh_token);
  return response;
}
