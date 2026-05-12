/**
 * AuthContext — single source of truth for authentication state.
 *
 * Why Context API instead of prop drilling:
 *   Any component at any depth can read `useAuth()` without
 *   passing user/token through every parent in the tree.
 *
 * Why localStorage for the token:
 *   Survives page refresh. In a higher-security app, use httpOnly cookies instead.
 *
 * Pattern: Context + custom hook (useAuth).
 *   Components never import AuthContext directly — they call useAuth().
 *   This means the implementation can change without touching consumers.
 */
import { createContext, useContext, useState, useCallback } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('access_token'))
  const [user, setUser] = useState(() => localStorage.getItem('user_email'))

  const login = useCallback((accessToken, email) => {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('user_email', email)
    setToken(accessToken)
    setUser(email)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_email')
    setToken(null)
    setUser(null)
  }, [])

  return (
    <AuthContext.Provider value={{ token, user, login, logout, isAuthenticated: !!token }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside <AuthProvider>')
  return ctx
}
