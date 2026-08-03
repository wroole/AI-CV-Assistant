import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { getMe, login as apiLogin, register as apiRegister, setAuthExpiredHandler, tokens, tryRefresh } from '../api';

const AuthContext = createContext(null);

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const hydrate = useCallback(async () => {
    try {
      setUser(await getMe());
    } catch {
      if (await tryRefresh()) {
        setUser(await getMe());
      } else {
        tokens.clear();
        setUser(null);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (!tokens.access && !tokens.refresh) {
      setLoading(false);
      return;
    }
    hydrate();
  }, [hydrate]);

  useEffect(() => {
    setAuthExpiredHandler(() => setUser(null));
    return () => setAuthExpiredHandler(null);
  }, []);

  const login = useCallback(async (email, password) => {
    const data = await apiLogin(email, password);
    tokens.set({ access: data.access_token, refresh: data.refresh_token });
    setUser(data.user);
    return data.user;
  }, []);

  const register = useCallback(async (email, password, fullName) => {
    const data = await apiRegister(email, password, fullName);
    tokens.set({ access: data.access_token, refresh: data.refresh_token });
    setUser(data.user);
    return data.user;
  }, []);

  const logout = useCallback(() => {
    tokens.clear();
    setUser(null);
  }, []);

  const value = {
    user,
    loading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
