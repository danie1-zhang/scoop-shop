import { useState } from 'react'
import { useAuth } from '../auth/useAuth'
import { useCart } from '../cart/useCart'
import type { Flavor } from '../types'

type FlavorCardProps = {
  flavor: Flavor
}

export function FlavorCard({ flavor }: FlavorCardProps) {
  const { user } = useAuth()
  const { addItem } = useCart()
  const [isAdding, setIsAdding] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleAddToCart() {
    setIsAdding(true)
    setError(null)

    try {
      await addItem(flavor.id)
    } catch (caughtError) {
      setError(
        caughtError instanceof Error
          ? caughtError.message
          : 'Unable to add item to cart.',
      )
    } finally {
      setIsAdding(false)
    }
  }

  return (
    <article className="flavor-card">
      <h3>{flavor.name}</h3>
      <p className="flavor-description">{flavor.description}</p>
      <p className="flavor-price">${flavor.price}</p>

      {error && <p role="alert">{error}</p>}

      <button
        type="button"
        disabled={user === null || isAdding}
        onClick={handleAddToCart}
      >
        {user === null
          ? 'Log in to add'
          : isAdding
            ? 'Adding...'
            : 'Add to cart'}
      </button>
    </article>
  )
}
