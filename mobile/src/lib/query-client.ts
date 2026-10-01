import AsyncStorage from '@react-native-async-storage/async-storage';
import { QueryClient } from '@tanstack/react-query';
import { createAsyncStoragePersister } from '@tanstack/query-async-storage-persister';

export const PERSIST_KEY = 'poupix-query-cache';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, gcTime: Infinity, retry: 1 },
  },
});

export const persister = createAsyncStoragePersister({
  storage: AsyncStorage,
  key: PERSIST_KEY,
  throttleTime: 1000,
});

/**
 * maxAge explícito: o default do persist-client é 24 h, o que apagaria o
 * cache de leitura offline em viagens/fim de semana (ADR 0002 usa o banner
 * com timestamp como aviso, não expiração).
 */
export const persistOptions = { persister, maxAge: Infinity };
