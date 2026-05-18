"use client";

import {
  useCallback,
  createContext,
  startTransition,
  useContext,
  useEffect,
  useState
} from "react";

import { api } from "@/lib/api";
import type { User } from "@/lib/types";

type AuthContextValue = {
  token: string | null;
  user: User | null;
  initialized: boolean;
  signIn: (payload: { email: string; password: string }) => Promise<void>;
  signUp: (payload: {
    email: string;
    password: string;
    display_name: string;
    timezone: string;
  }) => Promise<void>;
  signOut: () => void;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const TOKEN_KEY = "safebond_token";
const USER_KEY = "safebond_user";

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [initialized, setInitialized] = useState(false);

  useEffect(() => {
    const storedToken = window.localStorage.getItem(TOKEN_KEY);
    const storedUser = window.localStorage.getItem(USER_KEY);

    if (storedToken) {
      setToken(storedToken);
    }
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser) as User);
      } catch {
        window.localStorage.removeItem(USER_KEY);
      }
    }
    setInitialized(true);
  }, []);

  const persist = (nextToken: string, nextUser: User) => {
    window.localStorage.setItem(TOKEN_KEY, nextToken);
    window.localStorage.setItem(USER_KEY, JSON.stringify(nextUser));
    startTransition(() => {
      setToken(nextToken);
      setUser(nextUser);
    });
  };

  const signIn = async (payload: { email: string; password: string }) => {
    const response = await api.login(payload);
    persist(response.access_token, response.user);
  };

  const signUp = async (payload: {
    email: string;
    password: string;
    display_name: string;
    timezone: string;
  }) => {
    const response = await api.register(payload);
    persist(response.access_token, response.user);
  };

  const signOut = useCallback(() => {
    window.localStorage.removeItem(TOKEN_KEY);
    window.localStorage.removeItem(USER_KEY);
    startTransition(() => {
      setToken(null);
      setUser(null);
    });
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }
    let cancelled = false;

    api.me(token)
      .then((nextUser) => {
        if (!cancelled) {
          setUser(nextUser);
        }
      })
      .catch(() => {
        if (!cancelled) {
          signOut();
        }
      });

    return () => {
      cancelled = true;
    };
  }, [token, signOut]);

  const value: AuthContextValue = {
    token,
    user,
    initialized,
    signIn,
    signUp,
    signOut
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within AuthProvider.");
  }
  return context;
}
