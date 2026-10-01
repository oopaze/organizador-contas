import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';
import {
  tokenManager,
  User,
  RegisterRequest,
  login as apiLogin,
  register as apiRegister,
  getCurrentUser,
} from '../services';

const PROFILE_KEY = 'poupix:user-profile';

/**
 * Falha de credencial (sessão expirada) x falha de rede. Só a primeira pode
 * limpar os tokens: sem rede o usuário segue autenticado com o perfil salvo
 * (ADR 0002 — leitura offline).
 */
function isAuthFailure(error: unknown): boolean {
  if (error instanceof Error && error.name === 'SessionExpiredError') return true;
  const status = (error as { response?: { status?: number } } | null)?.response?.status;
  return status === 401 || status === 403;
}

async function readCachedUser(): Promise<User | null> {
  try {
    const raw = await AsyncStorage.getItem(PROFILE_KEY);
    return raw ? (JSON.parse(raw) as User) : null;
  } catch {
    return null;
  }
}

async function persistUser(user: User): Promise<void> {
  try {
    await AsyncStorage.setItem(PROFILE_KEY, JSON.stringify(user));
  } catch {
    // cache é best-effort
  }
}

async function clearCachedUser(): Promise<void> {
  try {
    await AsyncStorage.removeItem(PROFILE_KEY);
  } catch {
    // cache é best-effort
  }
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
  refreshUser: () => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Sessão anterior: valida o token guardado no SecureStore.
    const initAuth = async () => {
      try {
        const token = await tokenManager.getAccessToken();
        if (!token) return;

        try {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
          await persistUser(currentUser);
        } catch (error) {
          if (isAuthFailure(error)) {
            await tokenManager.clearTokens();
            await clearCachedUser();
            setUser(null);
          } else {
            setUser(await readCachedUser());
          }
        }
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiLogin({ email, password });
    setUser(response.user);
    await persistUser(response.user);
  };

  const register = async (data: RegisterRequest) => {
    await apiRegister(data);
  };

  const refreshUser = async () => {
    const currentUser = await getCurrentUser();
    setUser(currentUser);
    await persistUser(currentUser);
  };

  const logout = () => {
    void tokenManager.clearTokens();
    void clearCachedUser();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
        refreshUser,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
