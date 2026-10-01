import * as SecureStore from 'expo-secure-store';
import { refreshToken } from './auth/refresh';

// Toggle this to switch between mock and real API
export const USE_MOCK_API = false;

export const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_URL || 'https://api.poupix.connectakit.com.br';

let sessionExpiredHandler: (() => void) | null = null;

export function setSessionExpiredHandler(handler: (() => void) | null) {
  sessionExpiredHandler = handler;
}

export class SessionExpiredError extends Error {
  constructor() {
    super('Session expired');
    this.name = 'SessionExpiredError';
  }
}

const accessKey = () => (USE_MOCK_API ? 'mock_access_token' : 'access_token');
const refreshKey = () => (USE_MOCK_API ? 'mock_refresh_token' : 'refresh_token');

export const tokenManager = {
  getAccessToken: (): Promise<string | null> => SecureStore.getItemAsync(accessKey()),
  getRefreshToken: (): Promise<string | null> => SecureStore.getItemAsync(refreshKey()),
  setTokens: async (accessToken: string, refreshToken: string) => {
    await SecureStore.setItemAsync(accessKey(), accessToken);
    await SecureStore.setItemAsync(refreshKey(), refreshToken);
  },
  clearTokens: async () => {
    await SecureStore.deleteItemAsync(accessKey());
    await SecureStore.deleteItemAsync(refreshKey());
  },
};

export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {},
  retried = false
): Promise<T> {
  const token = await tokenManager.getAccessToken();
  const isFormData = options.body instanceof FormData;
  const headers = new Headers(
    isFormData ? {} : { 'Content-Type': 'application/json' }
  );

  if (options.headers) {
    const optionHeaders = new Headers(options.headers);
    optionHeaders.forEach((value, key) => headers.set(key, value));
  }
  if (token) headers.set('Authorization', `Bearer ${token}`);

  const response = await fetch(`${API_BASE_URL}${endpoint}`, { ...options, headers });

  if (!response.ok) {
    if (response.status === 403 && !retried) {
      const refreshed = await refreshToken();
      if (refreshed) return apiRequest<T>(endpoint, options, true);
      await tokenManager.clearTokens();
      sessionExpiredHandler?.();
      throw new SessionExpiredError();
    }
    const data = await response.json().catch(() => ({}));
    const err = new Error(
      data.detail || data.error_description || data.error || 'An error occurred'
    ) as Error & { response?: { status: number; data: Record<string, unknown> } };
    err.response = { status: response.status, data };
    throw err;
  }

  if (response.status === 204) return {} as T;
  return response.json();
}

export async function apiUploadRequest<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = await tokenManager.getAccessToken();
  const headers: HeadersInit = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({}));
    const err = new Error(
      data.detail || data.error || 'Upload failed'
    ) as Error & { response?: { status: number; data: Record<string, unknown> } };
    err.response = { status: response.status, data };
    throw err;
  }

  return response.json();
}
