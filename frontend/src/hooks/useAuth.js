import { useState, useEffect } from "react";

export function useAuth() {
  const [token, setToken] = useState(() => localStorage.getItem("ma_token") || "");
  const [username, setUsername] = useState(() => localStorage.getItem("ma_username") || "");
  const [isAdmin, setIsAdmin] = useState(() => localStorage.getItem("ma_is_admin") === "true");

  useEffect(() => {
    if (token) localStorage.setItem("ma_token", token);
    else localStorage.removeItem("ma_token");
  }, [token]);

  useEffect(() => {
    if (username) localStorage.setItem("ma_username", username);
    else localStorage.removeItem("ma_username");
  }, [username]);

  useEffect(() => {
    localStorage.setItem("ma_is_admin", isAdmin ? "true" : "false");
  }, [isAdmin]);

  const logout = () => {
    setToken("");
    setUsername("");
    setIsAdmin(false);
    localStorage.clear();
  };

  return { token, setToken, username, setUsername, isAdmin, setIsAdmin, logout };
}
