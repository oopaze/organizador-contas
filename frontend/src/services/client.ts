// Single API client with mock mode toggle

// Toggle this to switch between mock and real API
export const USE_MOCK_API = false;

const API_BASE_URL = 'http://127.0.0.1:8000';

// Token management
export const tokenManager = {
  getAccessToken: (): string | null => {
    const key = USE_MOCK_API ? 'mock_access_token' : 'access_token';
    return localStorage.getItem(key);
  },
  getRefreshToken: (): string | null => {
    const key = USE_MOCK_API ? 'mock_refresh_token' : 'refresh_token';
    return localStorage.getItem(key);
  },
  setTokens: (accessToken: string, refreshToken: string) => {
    if (USE_MOCK_API) {
      localStorage.setItem('mock_access_token', accessToken);
      localStorage.setItem('mock_refresh_token', refreshToken);
    } else {
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('refresh_token', refreshToken);
    }
  },
  clearTokens: () => {
    if (USE_MOCK_API) {
      localStorage.removeItem('mock_access_token');
      localStorage.removeItem('mock_refresh_token');
    } else {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },
};

// API request handler
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = tokenManager.getAccessToken();
  const headers = new Headers({
    'Content-Type': 'application/json',
  });

  if (options.headers) {
    const optionHeaders = new Headers(options.headers);
    optionHeaders.forEach((value, key) => {
      headers.set(key, value);
    });
  }

  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Token expired, try to refresh
      const { refreshToken } = await import('./auth/refresh');
      const refreshed = await refreshToken();
      if (refreshed) {
        // Retry the request
        return apiRequest(endpoint, options);
      } else {
        tokenManager.clearTokens();
        window.location.href = '/';
        throw new Error('Session expired');
      }
    }
    const error = await response.json().catch(() => ({ detail: 'An error occurred' }));
    throw new Error(error.detail || 'An error occurred');
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json();
}

// File upload request handler
export async function apiUploadRequest<T>(
  endpoint: string,
  formData: FormData
): Promise<T> {
  const token = tokenManager.getAccessToken();
  const headers: HeadersInit = {};

  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    method: 'POST',
    headers,
    body: formData,
  });

  if (!response.ok) {
    throw new Error('Upload failed');
  }

  return response.json();
}
