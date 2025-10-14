import React, { useState, useEffect } from "react";
import type { ReactNode } from "react";
import { authService } from "../services/auth.ts";
import type { User, AuthContextType } from "../types/feedback.ts";
import { AuthContext } from "./AuthContext.ts";

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth state on app load
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const storedToken = authService.getToken();
        if (storedToken) {
          setToken(storedToken);
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        console.error("Failed to initialize auth:", error);
        authService.logout();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const tokenData = await authService.login({ email, password });
    setToken(tokenData.access_token);
    const currentUser = await authService.getCurrentUser();
    setUser(currentUser);
  };

  const register = async (email: string, password: string) => {
    await authService.register({ email, password });
    // After successful registration, log the user in
    await login(email, password);
  };

  const logout = () => {
    authService.logout();
    setUser(null);
    setToken(null);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    register,
    logout,
    isLoading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
