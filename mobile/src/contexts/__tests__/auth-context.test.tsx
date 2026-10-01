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

import { act, renderHook, waitFor } from '@testing-library/react-native';
import { getCurrentUser, login, tokenManager } from '../../services';
import { AuthProvider, useAuth } from '../auth-context';

const mockedLogin = login as jest.Mock;
const mockedGetCurrentUser = getCurrentUser as jest.Mock;
const mockedTokenManager = tokenManager as jest.Mocked<typeof tokenManager>;

function wrapper({ children }: { children: React.ReactNode }) {
  return <AuthProvider>{children}</AuthProvider>;
}

beforeEach(() => {
  jest.clearAllMocks();
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
});

test('sessão inicial inválida limpa os tokens', async () => {
  mockedTokenManager.getAccessToken.mockResolvedValue('stale-token');
  mockedGetCurrentUser.mockRejectedValue(new Error('401'));

  const { result } = await renderHook(() => useAuth(), { wrapper });
  await waitFor(() => expect(result.current.loading).toBe(false));

  expect(mockedTokenManager.clearTokens).toHaveBeenCalled();
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