import { NavLink, Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './auth/useAuth'
import { useCart } from './cart/useCart'
import { AccountPage } from './pages/AccountPage'
import { AdminPage } from './pages/AdminPage'
import { CartPage } from './pages/CartPage'
import { OrdersPage } from './pages/OrdersPage'
import { ShopPage } from './pages/ShopPage'
import './App.css'

function App() {
  const { user, isAuthLoading, logout } = useAuth()
  const { items } = useCart()
  const itemCount = items.reduce((total, item) => total + item.quantity, 0)

  return (
    <div className="app">
      <header className="site-header">
        <NavLink className="brand" to="/">Goofball&apos;s Scoop Shop</NavLink>
        <nav aria-label="Main navigation">
          <NavLink to="/">Shop</NavLink>
          {user && <NavLink to="/cart">Cart ({itemCount})</NavLink>}
          {user && <NavLink to="/orders">Orders</NavLink>}
          {user?.role === 'admin' && <NavLink to="/admin">Admin</NavLink>}
          <NavLink to="/account">{user ? 'Account' : 'Log in'}</NavLink>
        </nav>
        {!isAuthLoading && user && <button className="link-button" type="button" onClick={logout}>Log out</button>}
      </header>
      <main>
        <Routes>
          <Route path="/" element={<ShopPage />} />
          <Route path="/account" element={<AccountPage />} />
          <Route path="/cart" element={user ? <CartPage /> : <Navigate to="/account" replace />} />
          <Route path="/orders" element={user ? <OrdersPage /> : <Navigate to="/account" replace />} />
          <Route path="/admin" element={user?.role === 'admin' ? <AdminPage /> : <Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  )
}

export default App
