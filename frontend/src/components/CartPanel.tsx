import { useState } from 'react'
import { useCart } from '../cart/useCart'
import type { OrderResponse } from '../types'


export function CartPanel() {
  const {
    items,
    isCartLoading,
    cartError,
    updateQuantity,
    removeItem,
    checkout,
  } = useCart()
  const [updatingItemId, setUpdatingItemId] = useState<number | null>(null)
  const [isCheckingOut, setIsCheckingOut] = useState(false)
  const [removingItemId, setRemovingItemId] = useState<number | null>(null)
  const [completedOrder, setCompletedOrder] = useState<OrderResponse | null>(
    null,
  )
  const cartTotal = items.reduce(
    (total, item) => total + Number(item.flavor.price) * item.quantity,
    0,
  )

  async function handleQuantityChange(
    cartItemId: number,
    quantity: number,
  ) {
    setUpdatingItemId(cartItemId)

    try {
      await updateQuantity(cartItemId, quantity)
    } catch {
      return
    } finally {
      setUpdatingItemId(null)
    }
  }

  async function handleCheckout() {
    setIsCheckingOut(true)
    setCompletedOrder(null)

    try {
      const order = await checkout()
      setCompletedOrder(order)
    } catch {
      return
    } finally {
      setIsCheckingOut(false)
    }
  }

  async function handleRemove(cartItemId: number) {
    setRemovingItemId(cartItemId)
    try { await removeItem(cartItemId) }
    catch { return }
    finally { setRemovingItemId(null) }
  }

  return (
    <section className="cart-panel" aria-labelledby="cart-heading">
      <div className="cart-heading-row">
        <h2 id="cart-heading">Your cart</h2>
        <span>
          {items.length} {items.length === 1 ? 'item' : 'items'}
        </span>
      </div>

      {isCartLoading && <p>Loading your cart...</p>}

      {cartError && <p role="alert">{cartError}</p>}

      {completedOrder && (
        <p role="status">
          Order #{completedOrder.id} was created successfully for $
          {Number(completedOrder.total_price).toFixed(2)}.
        </p>
      )}

      {!isCartLoading && !cartError && items.length === 0 && (
        <p>Your cart is empty.</p>
      )}

      {!isCartLoading && items.length > 0 && (
        <>
          <ul className="cart-list">
            {items.map((item) => {
              const lineTotal = Number(item.flavor.price) * item.quantity

              return (
                <li key={item.id}>
                  <div className="cart-item-info">
                    <h3>{item.flavor.name}</h3>
                    <p>${item.flavor.price} each</p>
                  </div>

                  <div
                    className="quantity-control"
                    aria-label={`${item.flavor.name} quantity`}
                  >
                    <button
                      type="button"
                      aria-label={`Decrease ${item.flavor.name} quantity`}
                      disabled={
                        item.quantity <= 1 || updatingItemId !== null
                      }
                      onClick={() =>
                        void handleQuantityChange(
                          item.id,
                          item.quantity - 1,
                        )
                      }
                    >
                      −
                    </button>
                    <span aria-live="polite">
                      {updatingItemId === item.id ? '…' : item.quantity}
                    </span>
                    <button
                      type="button"
                      aria-label={`Increase ${item.flavor.name} quantity`}
                      disabled={
                        item.quantity >= 100 || updatingItemId !== null
                      }
                      onClick={() =>
                        void handleQuantityChange(
                          item.id,
                          item.quantity + 1,
                        )
                      }
                    >
                      +
                    </button>
                  </div>

                  <strong>${lineTotal.toFixed(2)}</strong>
                  <button
                    className="remove-button"
                    type="button"
                    disabled={removingItemId !== null || updatingItemId !== null}
                    onClick={() => void handleRemove(item.id)}
                  >
                    {removingItemId === item.id ? 'Removing…' : 'Remove'}
                  </button>
                </li>
              )
            })}
          </ul>

          <div className="cart-total">
            <span>Total</span>
            <strong>${cartTotal.toFixed(2)}</strong>
          </div>

          <button
            className="checkout-button"
            type="button"
            disabled={isCheckingOut || updatingItemId !== null}
            onClick={() => void handleCheckout()}
          >
            {isCheckingOut ? 'Checking out…' : 'Checkout'}
          </button>
        </>
      )}
    </section>
  )
}
