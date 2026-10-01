jest.mock('../../services', () => ({
  login: jest.fn(),
  getCurrentUser: jest.fn(),
  tokenManager: {
    getAccessToken: jest.fn(),
    setTokens: jest.fn(),
    clearTokens: jest.fn(),
  },
  setSessionExpiredHandler: jest.fn(),
}));

import AsyncStorage from '@react-native-async-storage/async-storage';
import { act, renderHook, waitFor } from '@testing-library/react-native';
import { getCurrentUser, login, tokenManager } from '../../services';
import { AuthProvider, useAuth } from '../auth-context';

const mockedLogin = login as jest.Mock;
const mockedGetCurrentUser = getCurrentUser as jest.Mock;
const mockedTokenManager = tokenManager as jest.Mocked<typeof tokenManager>;
const mockedGetItem = AsyncStorage.getItem as jest.Mock;

function wrapper({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

beforeEach(() => {
  jest.clearAllMocks();
  mockedGetItem.mockResolvedValue(null);
});

test('login guarda o usuário', async () => {
  mockedTokenManager.getAccessToken.mockResolvedValue('stale-token');
  mockedGetCurrentUser.mockRejectedValue(new Error('no session'));
  mockedLogin.mockResolvedValue({
    access_token: 'a',
    refresh_token: 'r',
    user: { id: 1, email: 'eu@ex.com' },
  });

  const { result } = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  await act(async () => {
    await result.current.login('eu@ex.com', 'senha');
  });

  expect(mockedLogin).toHaveBeenCalledWith({ email: 'eu@ex.com', password: 'senha' });
  expect(result.current.user).toEqual({ id: 1, email: 'eu@ex.com' });
  expect(AsyncStorage.setItem).toHaveBeenCalled();
});

test('sessão inicial expirada limpa os tokens e o perfil salvo', async () => {
  mockedTokenManager.getAccessToken.mockResolvedValue('stale-token');
  const expired = Object.assign(new Error('expired'), { name: 'SessionExpiredError' });
  mockedGetCurrentUser.mockRejectedValue(expired);

  const { result } = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  expect(mockedTokenManager.clearTokens).toHaveBeenCalled();
  expect(result.current.user).toBeNull();
});

test('falha de rede mantém os tokens e restaura o usuário do cache', async () => {
  mockedTokenManager.getAccessToken.mockResolvedValue('token-valido');
  mockedGetCurrentUser.mockRejectedValue(new TypeError('Network request failed'));
  mockedGetItem.mockResolvedValue(JSON.stringify({ id: 9, email: 'offline@ex.com' }));

  const { result } = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  expect(mockedTokenManager.clearTokens).not.toHaveBeenCalled();
  expect(result.current.user).toEqual({ id: 9, email: 'offline@ex.com' });
  expect(result.current.isAuthenticated).toBe(true);
});

test('falha de rede sem cache mantém os tokens e não autentica', async () => {
  mockedTokenManager.getAccessToken.mockResolvedValue('token-valido');
  mockedGetCurrentUser.mockRejectedValue(new TypeError('Network request failed'));

  const { result } = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  expect(mockedTokenManager.clearTokens).not.toHaveBeenCalled();
  expect(result.current.user).toBeNull();
});

test('logout limpa os tokens e o usuário', async () => {
  mockedTokenManager.getAccessToken.mockResolvedValue(null);

  const { result } = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  await act(async () => {
    result.current.logout();
  });

  expect(mockedTokenManager.clearTokens).toHaveBeenCalled();
  expect(result.current.user).toBeNull();
});
