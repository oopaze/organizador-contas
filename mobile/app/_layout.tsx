import '../global.css';

import { useCallback, useEffect, useState } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { PersistQueryClientProvider } from '@tanstack/react-query-persist-client';
import { Stack, router, useSegments } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { OfflineBanner } from '../src/components/offline-banner';
import { AuthProvider, useAuth } from '../src/contexts/auth-context';
import { UserProvider } from '../src/contexts/user-context';
import { shouldRedirectToLogin } from '../src/lib/auth-guard';
import { PERSIST_KEY, persistOptions, queryClient } from '../src/lib/query-client';
import { useOnlineStatus } from '../src/lib/use-online-status';
import { setSessionExpiredHandler } from '../src/services';

async function readPersistedAt(): Promise<number | null> {
  const raw = await AsyncStorage.getItem(PERSIST_KEY);
  if (!raw) return null;
  try {
    const { timestamp } = JSON.parse(raw) as { timestamp?: number };
    return typeof timestamp === 'number' ? timestamp : null;
  } catch {
    return null;
  }
}

function RootNavigator() {
  const { isAuthenticated, loading } = useAuth();
  const segments = useSegments();

  useEffect(() => {
    setSessionExpiredHandler(() => {
      router.replace('/login');
    });
    return () => setSessionExpiredHandler(null);
  }, []);

  useEffect(() => {
    const inAuthGroup = segments[0] === 'login';
    if (shouldRedirectToLogin(isAuthenticated, loading, inAuthGroup)) {
      router.replace('/login');
    }
  }, [isAuthenticated, loading, segments]);

  return (
    <Stack>
      <Stack.Screen name="login" options={{ headerShown: false }} />
      <Stack.Screen name="(tabs)" options={{ headerShown: false }} />
      <Stack.Screen name="settings" options={{ title: 'Configurações' }} />
      <Stack.Screen name="integrations" options={{ title: 'Conectores' }} />
    </Stack>
  );
}

export default function RootLayout() {
  const [persistedAt, setPersistedAt] = useState<number | null>(null);
  const isOnline = useOnlineStatus();

  const refreshPersistedAt = useCallback(async () => {
    setPersistedAt(await readPersistedAt());
  }, []);

  useEffect(() => {
    void refreshPersistedAt();
  }, [refreshPersistedAt]);

  // No v5 o onSuccess do provider só dispara após o hydrate inicial;
  // ao ficar offline releio o cache para o banner mostrar o horário real do último persist.
  useEffect(() => {
    if (!isOnline) void refreshPersistedAt();
  }, [isOnline, refreshPersistedAt]);

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <PersistQueryClientProvider
          client={queryClient}
          persistOptions={persistOptions}
          onSuccess={refreshPersistedAt}
        >
          <AuthProvider>
            <UserProvider>
              {!isOnline ? <OfflineBanner persistedAt={persistedAt} /> : null}
              <RootNavigator />
            </UserProvider>
          </AuthProvider>
        </PersistQueryClientProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}