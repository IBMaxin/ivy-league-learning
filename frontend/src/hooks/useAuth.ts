import { useCallback, useEffect, useState } from "react";
import { getToken, getUser, login as apiLogin, logout as apiLogout } from "../api/client";

export function useAuth() {
  const [user, setUser] = useState<string | null>(() => getUser());
  const [hasToken, setHasToken] = useState<boolean>(() => getToken() !== null);

  const refresh = useCallback(() => {
    setUser(getUser());
    setHasToken(getToken() !== null);
  }, []);

  useEffect(() => {
    const onStorage = (e: StorageEvent) => {
      if (e.key === null || e.key === "ivy-token" || e.key === "ivy-user") refresh();
    };
    window.addEventListener("storage", onStorage);
    return () => window.removeEventListener("storage", onStorage);
  }, [refresh]);

  async function login(id: string): Promise<void> {
    await apiLogin(id);
    refresh();
  }

  function logout(): void {
    apiLogout();
    refresh();
  }

  return { user, hasToken, loggedIn: user !== null && hasToken, login, logout, refresh };
}
