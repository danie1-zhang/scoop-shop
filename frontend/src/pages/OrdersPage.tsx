import { useEffect, useState } from 'react'
import { getOrders } from '../api'
import { useAuth } from '../auth/useAuth'
import type { OrderResponse } from '../types'

const PAGE_SIZE = 5

export function OrdersPage() {
  const { token } = useAuth()
  const [orders, setOrders] = useState<OrderResponse[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(true)
  const [expandedOrderIds, setExpandedOrderIds] = useState<Set<number>>(
    new Set(),
  )
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  useEffect(() => {
    if (!token) return

    const authToken = token
    let ignore = false

    async function load() {
      setLoading(true)
      setError(null)

      try {
        const response = await getOrders(authToken, page, PAGE_SIZE)

        if (!ignore) {
          setOrders(response.items)
          setTotal(response.total)
        }
      } catch (caught) {
        if (!ignore) {
          setError(
            caught instanceof Error
              ? caught.message
              : 'Unable to load orders',
          )
        }
      } finally {
        if (!ignore) setLoading(false)
      }
    }

    void load()

    return () => {
      ignore = true
    }
  }, [page, token])

  function toggleOrder(orderId: number) {
    setExpandedOrderIds((currentIds) => {
      const nextIds = new Set(currentIds)

      if (nextIds.has(orderId)) {
        nextIds.delete(orderId)
      } else {
        nextIds.add(orderId)
      }

      return nextIds
    })
  }

  return (
    <section>
      <h1>Order history</h1>

      {loading && <p>Loading orders...</p>}
      {error && <p role="alert">{error}</p>}
      {!loading && !error && orders.length === 0 && (
        <p>You have not placed an order yet.</p>
      )}

      <div className="order-list">
        {orders.map((order) => {
          const isExpanded = expandedOrderIds.has(order.id)
          const detailsId = `order-${order.id}-details`

          return (
            <article className="order-card" key={order.id}>
              <header>
                <div>
                  <h2>Order #{order.id}</h2>
                  <time>{new Date(order.created_at).toLocaleString()}</time>
                </div>
                <strong>${Number(order.total_price).toFixed(2)}</strong>
              </header>

              <button
                className="order-details-button"
                type="button"
                aria-expanded={isExpanded}
                aria-controls={detailsId}
                onClick={() => toggleOrder(order.id)}
              >
                {isExpanded ? 'Hide details' : 'View details'}
              </button>

              {isExpanded && (
                <div id={detailsId} className="order-details">
                  <ul>
                    {order.items.map((item) => (
                      <li key={item.id}>
                        <span>
                          {item.quantity} × {item.flavor_name_at_purchase}
                        </span>
                        <strong>
                          $
                          {(
                            Number(item.price_at_purchase) * item.quantity
                          ).toFixed(2)}
                        </strong>
                      </li>
                    ))}
                  </ul>
                  <p className="order-total">
                    Total{' '}
                    <strong>${Number(order.total_price).toFixed(2)}</strong>
                  </p>
                </div>
              )}
            </article>
          )
        })}
      </div>

      {total > 0 && (
        <nav className="pagination" aria-label="Order pages">
          <button
            disabled={page === 1}
            onClick={() => setPage((value) => value - 1)}
          >
            Previous
          </button>
          <span>
            Page {page} of {totalPages}
          </span>
          <button
            disabled={page >= totalPages}
            onClick={() => setPage((value) => value + 1)}
          >
            Next
          </button>
        </nav>
      )}
    </section>
  )
}
