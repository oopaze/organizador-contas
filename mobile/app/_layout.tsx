import '../global.css';

import { useEffect } from 'react';
import { Stack, router, useSegments } from 'expo-router';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { AuthProvider, useAuth } from '../src/contexts/auth-context';
import { UserProvider } from '../src/contexts/user-context';
import { shouldRedirectToLogin } from '../src/lib/auth-guard';
import { setSessionExpiredHandler } from '../src/services';

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
    </Stack>
  );
}

export default function RootLayout() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <AuthProvider>
          <UserProvider>
            <RootNavigator />
          </UserProvider>
        </AuthProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}