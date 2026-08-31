import { createContext } from 'react'
import type { CartItemResponse, OrderResponse } from '../types'

export type CartContextValue = {
  items: CartItemResponse[]
  isCartLoading: boolean
  cartError: string | null
  addItem: (flavorId: number) => Promise<void>
  refreshCart: () => Promise<void>
  updateQuantity: (
    cartItemId: number,
    quantity: number,
  ) => Promise<void>
  removeItem: (cartItemId: number) => Promise<void>
  checkout: () => Promise<OrderResponse>
}

export const CartContext = createContext<CartContextValue | undefined>(
  undefined,
)
