import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import {
  getCurrentUser,
  login as sendLoginRequest,
  register as sendRegisterRequest,
} from '../api'
import type {
  LoginCredentials,
  RegisterCredentials,
  User,
} from '../types'
import { AuthContext } from './AuthContext'

const TOKEN_STORAGE_KEY = 'scoop-shop-token'
const initialToken = localStorage.getItem(TOKEN_STORAGE_KEY)

type AuthProviderProps = {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(initialToken)
  const [isAuthLoading, setIsAuthLoading] = useState(initialToken !== null)

  useEffect(() => {
    if (initialToken === null) {
      return
    }

    const storedToken = initialToken
    let ignoreResult = false

    async function restoreUser() {
      try {
        const currentUser = await getCurrentUser(storedToken)

        if (!ignoreResult) {
          setToken(storedToken)
          setUser(currentUser)
        }
      } catch {
        localStorage.removeItem(TOKEN_STORAGE_KEY)
      } finally {
        if (!ignoreResult) {
          setIsAuthLoading(false)
        }
      }
    }

    void restoreUser()

    return () => {
      ignoreResult = true
    }
  }, [])

  async function login(credentials: LoginCredentials) {
    const tokenResponse = await sendLoginRequest(credentials)
    const currentUser = await getCurrentUser(tokenResponse.access_token)

    localStorage.setItem(
      TOKEN_STORAGE_KEY,
      tokenResponse.access_token,
    )
    setToken(tokenResponse.access_token)
    setUser(currentUser)
  }

  async function register(credentials: RegisterCredentials) {
    await sendRegisterRequest(credentials)

    try {
      await login(credentials)
    } catch {
      throw new Error(
        'Your account was created, but automatic login failed. Please log in.',
      )
    }
  }

  function logout() {
    localStorage.removeItem(TOKEN_STORAGE_KEY)
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthLoading,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}
