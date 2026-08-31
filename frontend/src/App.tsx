import { useEffect, useState } from 'react'
import { getFlavors } from './api'
import { useAuth } from './auth/useAuth'
import { CartPanel } from './components/CartPanel'
import { FlavorCard } from './components/FlavorCard'
import { LoginForm } from './components/LoginForm'
import { RegisterForm } from './components/RegisterForm'
import type { Flavor } from './types'
import './App.css'

const PAGE_SIZE = 8

function App() {
  const { user, isAuthLoading, login, register, logout } = useAuth()
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login')
  const [flavors, setFlavors] = useState<Flavor[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  useEffect(() => {
    let ignoreResult = false

    async function loadFlavors() {
      setIsLoading(true)
      setError(null)

      try {
        const response = await getFlavors(page, PAGE_SIZE)

        if (!ignoreResult) {
          setFlavors(response.items)
          setTotal(response.total)
        }
      }
      catch {
        if (!ignoreResult) {
          setError('Unable to load flavors. Please try again.')
        }
      }
      finally {
        if (!ignoreResult) {
          setIsLoading(false)
        }
      }
    }

    void loadFlavors()

    return () => {
      ignoreResult = true
    }
  }, [page])

  return (
    <main className="app">
      <header>
        <h1>Goofball's Scoop Shop</h1>
        <p>Amazingly brilliant goofy ice cream shop. Choose your flavor!</p>
      </header>

      <section className="account" aria-labelledby="account-heading">
        <h2 id="account-heading">Account</h2>

        {isAuthLoading && <p>Checking your session...</p>}

        {!isAuthLoading && !user && (
          <>
            <div className="auth-switch" aria-label="Authentication options">
              <button
                type="button"
                aria-pressed={authMode === 'login'}
                onClick={() => setAuthMode('login')}
              >
                Log in
              </button>
              <button
                type="button"
                aria-pressed={authMode === 'register'}
                onClick={() => setAuthMode('register')}
              >
                Create account
              </button>
            </div>

            {authMode === 'login' ? (
              <LoginForm onLogin={login} />
            ) : (
              <RegisterForm onRegister={register} />
            )}
          </>
        )}

        {!isAuthLoading && user && (
          <div className="account-summary">
            <p>
              Signed in as <strong>{user.email}</strong>
            </p>
            <button type="button" onClick={logout}>
              Log out
            </button>
          </div>
        )}
      </section>

      {!isAuthLoading && user && <CartPanel />}

      <section aria-labelledby="flavors-heading">
        <h2 id="flavors-heading">Flavors</h2>

        {isLoading && <p>Loading flavors...</p>}

        {error && <p role="alert">{error}</p>}

        {!isLoading && !error && flavors.length === 0 && (
          <p>No flavors are currently available.</p>
        )}

        {!isLoading && !error && flavors.length > 0 && (
          <ul className="flavor-list">
            {flavors.map((flavor) => (
              <li key={flavor.id}>
                <FlavorCard flavor={flavor} />
              </li>
            ))}
          </ul>
        )}

        {!isLoading && !error && total > 0 && (
          <nav className="pagination" aria-label="Flavor pages">
            <button
              type="button"
              disabled={page === 1}
              onClick={() => setPage((currentPage) => currentPage - 1)}
            >
              Previous
            </button>

            <span>
              Page {page} of {totalPages}
            </span>

            <button
              type="button"
              disabled={page >= totalPages}
              onClick={() => setPage((currentPage) => currentPage + 1)}
            >
              Next
            </button>
          </nav>
        )}
      </section>
    </main>
  )
}

export default App
