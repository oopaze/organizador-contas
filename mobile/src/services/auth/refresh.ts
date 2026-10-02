import { tokenManager, USE_MOCK_API } from '../client';
import { delay } from '../mockData';

async function refreshTokenMock(): Promise<boolean> {
  await delay(200);
  return true;
}

async function refreshTokenReal(): Promise<boolean> {
  try {
    const refreshToken = await tokenManager.getRefreshToken();
    if (!refreshToken) return false;

    const API_BASE_URL =
      process.env.EXPO_PUBLIC_API_URL || 'https://api.poupix.connectakit.com.br';
    const response = await fetch(`${API_BASE_URL}/auth/refresh/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) return false;

    const data = await response.json();
    await tokenManager.setTokens(data.access_token, data.refresh_token);
    return true;
  } catch {
    return false;
  }
}

export async function refreshToken(): Promise<boolean> {
  return USE_MOCK_API ? await refreshTokenMock() : await refreshTokenReal();
}
