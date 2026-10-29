import { createContext, useEffect, useState } from "react";

import {
  fetchCurrentUser,
  loginUser,
  logoutUser,
  registerUser,
} from "../services/api";

const TOKEN_STORAGE_KEY = "wastewise_token";

const AuthContext = createContext(null);

function normalizeEmail(email) {
  return email.trim().toLowerCase();
}

function candidatePasswords(password) {
  const options = [password];
  const trimmedPassword = password.trim();

  if (!options.includes(trimmedPassword)) {
    options.push(trimmedPassword);
  }

  return options;
}

function readStoredToken() {
  return window.localStorage.getItem(TOKEN_STORAGE_KEY);
}

function persistToken(token) {
  if (token) {
    window.localStorage.setItem(TOKEN_STORAGE_KEY, token);
    return;
  }

  window.localStorage.removeItem(TOKEN_STORAGE_KEY);
}

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => readStoredToken());
  const [user, setUser] = useState(null);
  const [isRestoring, setIsRestoring] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function restoreSession() {
      if (!token) {
        if (!cancelled) {
          setUser(null);
          setIsRestoring(false);
        }
        return;
      }

      try {
        const currentUser = await fetchCurrentUser(token);
        if (!cancelled) {
          setUser(currentUser);
        }
      } catch {
        persistToken(null);
        if (!cancelled) {
          setToken(null);
          setUser(null);
        }
      } finally {
        if (!cancelled) {
          setIsRestoring(false);
        }
      }
    }

    restoreSession();

    return () => {
      cancelled = true;
    };
  }, [token]);

  async function handleAuthenticatedSession(nextToken) {
    persistToken(nextToken);
    setToken(nextToken);
    const currentUser = await fetchCurrentUser(nextToken);
    setUser(currentUser);
    return currentUser;
  }

  async function signUp(email, password) {
    const normalizedEmail = normalizeEmail(email);
    const safePassword = password.trim();
    await registerUser({ email: normalizedEmail, password: safePassword });
    const { access_token: accessToken } = await loginUser({
      email: normalizedEmail,
      password: safePassword,
    });
    return handleAuthenticatedSession(accessToken);
  }

  async function signIn(email, password) {
    const normalizedEmail = normalizeEmail(email);
    let lastError = null;

    for (const nextPassword of candidatePasswords(password)) {
      try {
        const { access_token: accessToken } = await loginUser({
          email: normalizedEmail,
          password: nextPassword,
        });
        return handleAuthenticatedSession(accessToken);
      } catch (error) {
        lastError = error;
      }
    }

    throw lastError ?? new Error("Invalid email or password");
  }

  async function signOut() {
    const activeToken = token;
    persistToken(null);
    setToken(null);
    setUser(null);

    if (!activeToken) {
      return;
    }

    try {
      await logoutUser(activeToken);
    } catch {
      // Sign-out is client-side for this milestone, so local cleanup is enough.
    }
  }

  const value = {
    token,
    user,
    isAuthenticated: Boolean(token && user),
    isRestoring,
    signIn,
    signOut,
    signUp,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export { AuthContext };
