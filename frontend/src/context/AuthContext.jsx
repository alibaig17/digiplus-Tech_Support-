import { createContext, useContext, useState } from "react";

const AuthContext = createContext(null);

// Auth/OTP flow removed — the app now goes straight to the main page.
// A fixed placeholder user is provided so components that read `user`
// (sidebar, Profile page, etc.) keep working without a real login.
const DEFAULT_USER = {
  id: "dev-user",
  name: "Dev User",
  email: "dev@example.com",
  role: "admin",
};

export function AuthProvider({ children }) {
  const [user] = useState(DEFAULT_USER);

  const login = () => {};
  const logout = () => {};

  return (
    <AuthContext.Provider value={{ user, login, logout, loading: false }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
