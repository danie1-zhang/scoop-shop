import { createContext } from 'react'
import type {
  LoginCredentials,
  RegisterCredentials,
  User,
} from '../types'

export type AuthContextValue = {
  user: User | null
  token: string | null
  isAuthLoading: boolean
  login: (credentials: LoginCredentials) => Promise<void>
  register: (credentials: RegisterCredentials) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
)
