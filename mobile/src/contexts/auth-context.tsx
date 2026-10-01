import React, { createContext, useContext, useState, useEffect } from 'react';
import {
  tokenManager,
  User,
  RegisterRequest,
  login as apiLogin,
  register as apiRegister,
  getCurrentUser,
} from '../services';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: RegisterRequest) => Promise<void>;
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
        if (token) {
          const currentUser = await getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        await tokenManager.clearTokens();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const response = await apiLogin({ email, password });
    setUser(response.user);
  };

  const register = async (data: RegisterRequest) => {
    await apiRegister(data);
  };

  const logout = () => {
    void tokenManager.clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        login,
        register,
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