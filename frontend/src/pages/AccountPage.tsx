import { useState } from 'react'
import { useAuth } from '../auth/useAuth'
import { LoginForm } from '../components/LoginForm'
import { RegisterForm } from '../components/RegisterForm'

export function AccountPage() {
  const { user, isAuthLoading, login, register, logout } = useAuth()
  const [mode, setMode] = useState<'login' | 'register'>('login')
  if (isAuthLoading) return <p>Checking your session...</p>
  if (user) return <section className="panel"><h1>Your account</h1><p>Signed in as <strong>{user.email}</strong></p><p>Role: {user.role}</p><button onClick={logout}>Log out</button></section>
  return <section className="panel auth-page"><div className="auth-switch"><button aria-pressed={mode === 'login'} onClick={() => setMode('login')}>Log in</button><button aria-pressed={mode === 'register'} onClick={() => setMode('register')}>Create account</button></div>{mode === 'login' ? <LoginForm onLogin={login} /> : <RegisterForm onRegister={register} />}</section>
}
