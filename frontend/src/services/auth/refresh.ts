import { tokenManager, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

async function refreshTokenMock(): Promise<boolean> {
  await delay(200);
  return true;
}

async function refreshTokenReal(): Promise<boolean> {
  try {
    const refreshToken = tokenManager.getRefreshToken();
    if (!refreshToken) return false;

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
    const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return false;

    const data = await response.json();
    tokenManager.setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function refreshToken(): Promise<boolean> {
  return USE_MOCK_API ? await refreshTokenMock() : await refreshTokenReal();
}
