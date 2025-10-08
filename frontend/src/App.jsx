import { useEffect } from "react";
import { useAuth } from "./hooks/useAuth";
import LoginPage from "./pages/LoginPage";
import AdminDashboard from "./pages/AdminDashboard";
import UserDashboard from "./pages/UserDashboard";

export default function App() {
  const { token, setToken, username, setUsername, isAdmin, setIsAdmin, logout } = useAuth();

  return (
    <div className="app-root">
      <header className="topbar">
        <h1 className="brand">Meeting Agent</h1>
        <div className="header-right">
          {token && (
            <>
              <div className="who">
                {username} {isAdmin && "(Admin)"}
              </div>
              <button className="btn small" onClick={logout}>Logout</button>
            </>
          )}
        </div>
      </header>

      <main className="container">
        {!token && <LoginPage setToken={setToken} setUsername={setUsername} setIsAdmin={setIsAdmin} />}
        {token && isAdmin && <AdminDashboard token={token} />}
        {token && !isAdmin && <UserDashboard token={token} />}
      </main>

      <footer className="footer">Meeting Agent — AI-Powered Task Management © 2024</footer>
    </div>
  );
}
