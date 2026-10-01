jest.mock('expo-secure-store', () => ({
  getItemAsync: jest.fn(),
  setItemAsync: jest.fn(),
  deleteItemAsync: jest.fn(),
}));
jest.mock('../auth/refresh', () => ({ refreshToken: jest.fn() }));

import * as SecureStore from 'expo-secure-store';
import { refreshToken } from '../auth/refresh';
import {
  apiRequest,
  setSessionExpiredHandler,
  SessionExpiredError,
  tokenManager,
} from '../client';

const mockedSecureStore = SecureStore as jest.Mocked<typeof SecureStore>;
const mockedRefresh = refreshToken as jest.Mock;

describe('apiRequest', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedSecureStore.getItemAsync.mockResolvedValue('token-abc');
  });

  test('envia Authorization com o token', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({ ok: 1 }),
    }) as jest.Mock;

    await apiRequest('/transactions/transactions/');

    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/transactions/transactions/'),
      expect.objectContaining({
        headers: expect.any(Headers),
      })
    );
    const headers = (global.fetch as jest.Mock).mock.calls[0][1].headers as Headers;
    expect(headers.get('Authorization')).toBe('Bearer token-abc');
  });

  test('em 403 renova o token e repete a request', async () => {
    global.fetch = jest
      .fn()
      .mockResolvedValueOnce({ ok: false, status: 403, json: async () => ({}) })
      .mockResolvedValueOnce({ ok: true, status: 200, json: async () => ({ value: 7 }) }) as jest.Mock;
    mockedRefresh.mockResolvedValue(true);

    const result = await apiRequest('/x');

    expect(result).toEqual({ value: 7 });
    expect(mockedRefresh).toHaveBeenCalledTimes(1);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  test('refresh falhando limpa tokens, chama handler e lança SessionExpiredError', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: false,
      status: 403,
      json: async () => ({}),
    }) as jest.Mock;
    mockedRefresh.mockResolvedValue(false);
    const handler = jest.fn();
    setSessionExpiredHandler(handler);

    await expect(apiRequest('/x')).rejects.toBeInstanceOf(SessionExpiredError);

    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('access_token');
    expect(mockedSecureStore.deleteItemAsync).toHaveBeenCalledWith('refresh_token');
    expect(handler).toHaveBeenCalledTimes(1);
    setSessionExpiredHandler(null);
  });

  test('204 devolve objeto vazio', async () => {
    global.fetch = jest.fn().mockResolvedValue({
      ok: true,
      status: 204,
      json: async () => ({}),
    }) as jest.Mock;

    await expect(apiRequest('/x')).resolves.toEqual({});
  });
});
