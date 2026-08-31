import { useEffect, useState } from 'react'
import type { ReactNode } from 'react'
import {
  addCartItem,
  createOrder,
  getCartItems,
  updateCartItem as sendCartItemUpdate,
} from '../api'
import { useAuth } from '../auth/useAuth'
import type { CartItemResponse } from '../types'
import { CartContext } from './CartContext'

type CartProviderProps = {
  children: ReactNode
}

export function CartProvider({ children }: CartProviderProps) {
  const { token } = useAuth()

  const [items, setItems] = useState<CartItemResponse[]>([])
  const [isCartLoading, setIsCartLoading] = useState(false)
  const [cartError, setCartError] = useState<string | null>(null)

  async function refreshCart() {
    if (token === null) {
      setItems([])
      setCartError(null)
      setIsCartLoading(false)
      return
    }

    setIsCartLoading(true)
    setCartError(null)

    try {
      const cartItems = await getCartItems(token)
      setItems(cartItems)
    } catch {
      setCartError('Failed to load cart')
    } finally {
      setIsCartLoading(false)
    }
  }

  useEffect(() => {
    let ignoreResult = false

    async function synchronizeCart() {
      if (token === null) {
        if (!ignoreResult) {
          setItems([])
          setCartError(null)
          setIsCartLoading(false)
        }
        return
      }

      setIsCartLoading(true)
      setCartError(null)

      try {
        const cartItems = await getCartItems(token)

        if (!ignoreResult) {
          setItems(cartItems)
        }
      } catch {
        if (!ignoreResult) {
          setCartError('Failed to load cart')
        }
      } finally {
        if (!ignoreResult) {
          setIsCartLoading(false)
        }
      }
    }

    void synchronizeCart()

    return () => {
      ignoreResult = true
    }
  }, [token])

  async function addItem(flavorId: number) {
    if (token === null) {
      throw new Error('You must log in before adding items to your cart.')
    }

    setCartError(null)

    try {
      const updatedItem = await addCartItem(token, {
        flavor_id: flavorId,
        quantity: 1,
      })

      setItems((currentItems) => {
        const itemAlreadyExists = currentItems.some(
          (item) => item.id === updatedItem.id,
        )

        if (itemAlreadyExists) {
          return currentItems.map((item) =>
            item.id === updatedItem.id ? updatedItem : item,
          )
        }

        return [...currentItems, updatedItem]
      })
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : 'Unable to add item to cart.'

      setCartError(message)
      throw caughtError
    }
  }

  async function updateQuantity(
    cartItemId: number,
    quantity: number,
  ) {
    if (token === null) {
      throw new Error('You must log in before updating your cart.')
    }

    setCartError(null)

    try {
      const updatedItem = await sendCartItemUpdate(
        token,
        cartItemId,
        { quantity },
      )

      setItems((currentItems) =>
        currentItems.map((item) =>
          item.id === updatedItem.id ? updatedItem : item,
        ),
      )
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : 'Unable to update cart item.'

      setCartError(message)
      throw caughtError
    }
  }

  async function checkout() {
    if (token === null) {
      throw new Error('You must log in before checking out.')
    }

    setCartError(null)

    try {
      const order = await createOrder(token)
      setItems([])
      return order
    } catch (caughtError) {
      const message =
        caughtError instanceof Error
          ? caughtError.message
          : 'Unable to create order.'

      setCartError(message)
      throw caughtError
    }
  }

  return (
    <CartContext.Provider
      value={{
        items,
        isCartLoading,
        cartError,
        addItem,
        updateQuantity,
        refreshCart,
        checkout,
      }}
    >
      {children}
    </CartContext.Provider>
  )
}
