import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, AuthContextType } from '@/types';
import { authService } from '@/services/auth';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setTokenState] = useState<string | null>(authService.getToken());
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      const storedToken = authService.getToken();
      if (storedToken) {
        try {
          const userData = await authService.getCurrentUser();
          setUser(userData);
          setTokenState(storedToken);
        } catch (error) {
          authService.removeToken();
          setTokenState(null);
        }
      }
      setIsLoading(false);
    };

    loadUser();
  }, []);

  const login = async (newToken: string) => {
    authService.setToken(newToken);
    setTokenState(newToken);
    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      authService.removeToken();
      setTokenState(null);
      throw error;
    }
  };

  const logout = () => {
    authService.removeToken();
    setUser(null);
    setTokenState(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};
