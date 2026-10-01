import React, { createContext, useContext, useState } from 'react';
import { User } from '../services';
import { useAuth } from './auth-context';

interface UserContextType {
  user: User | null;
  loading: boolean;
  refetchUser: () => Promise<void>;
}

const UserContext = createContext<UserContextType | undefined>(undefined);

/**
 * Espelho do usuário do AuthProvider (fonte única — evita o GET /user/me
 * duplicado do PWA no boot). O perfil offline vem do cache do auth-context.
 */
export const UserProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, refreshUser } = useAuth();
  const [loading, setLoading] = useState(false);

  const refetchUser = async () => {
    setLoading(true);
    try {
      await refreshUser();
    } catch {
      // sem rede: mantém o usuário atual (cache)
    } finally {
      setLoading(false);
    }
  };

  return (
    <UserContext.Provider value={{ user, loading, refetchUser }}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};
