import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { expect, test, vi } from 'vitest'
import { CartContext } from '../cart/CartContext'
import { CartPanel } from './CartPanel'

const cartItem = {
  id: 1,
  user_id: 10,
  flavor_id: 3,
  quantity: 2,
  created_at: '2026-08-31T12:00:00Z',
  flavor: {
    id: 3,
    name: 'Chocolate',
    description: 'Rich chocolate ice cream',
    price: '4.50',
    available: true,
    created_at: '2026-08-31T12:00:00Z',
  },
}

const completedOrder = {
  id: 42,
  user_id: 10,
  total_price: '9.00',
  created_at: '2026-08-31T12:05:00Z',
  items: [
    {
      id: 100,
      order_id: 42,
      flavor_id: 3,
      flavor_name_at_purchase: 'Chocolate',
      quantity: 2,
      price_at_purchase: '4.50',
    },
  ],
}

test('checks out the cart and displays the order confirmation', async () => {
  const user = userEvent.setup()
  const checkout = vi.fn().mockResolvedValue(completedOrder)

  render(
    <CartContext.Provider
      value={{
        items: [cartItem],
        isCartLoading: false,
        cartError: null,
        addItem: vi.fn(),
        updateQuantity: vi.fn(),
        refreshCart: vi.fn(),
        checkout,
      }}
    >
      <CartPanel />
    </CartContext.Provider>,
  )

  await user.click(screen.getByRole('button', { name: 'Checkout' }))

  expect(checkout).toHaveBeenCalledOnce()

  expect(
    await screen.findByText(
      'Order #42 was created successfully for $9.00.',
    ),
  ).toBeInTheDocument()
})
