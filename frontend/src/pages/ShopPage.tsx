import { useEffect, useState } from 'react'
import { getFlavors } from '../api'
import { FlavorCard } from '../components/FlavorCard'
import type { Flavor } from '../types'

const PAGE_SIZE = 8

export function ShopPage() {
  const [flavors, setFlavors] = useState<Flavor[]>([])
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE))

  useEffect(() => {
    let ignore = false
    async function load() {
      setIsLoading(true)
      setError(null)
      try {
        const response = await getFlavors(page, PAGE_SIZE)
        if (!ignore) { setFlavors(response.items); setTotal(response.total) }
      } catch {
        if (!ignore) setError('Unable to load flavors. Please try again.')
      } finally {
        if (!ignore) setIsLoading(false)
      }
    }
    void load()
    return () => { ignore = true }
  }, [page])

  return <>
    <section className="hero"><p className="eyebrow">Small-batch happiness</p><h1>Pick something deliciously goofy.</h1><p>Fresh scoops, cheerful flavors, and absolutely no serious business.</p></section>
    <section aria-labelledby="flavors-heading">
      <h2 id="flavors-heading">Available flavors</h2>
      {isLoading && <p>Loading flavors...</p>}
      {error && <p role="alert">{error}</p>}
      {!isLoading && !error && flavors.length === 0 && <p>No flavors are currently available.</p>}
      {!isLoading && !error && flavors.length > 0 && <ul className="flavor-list">{flavors.map((flavor) => <li key={flavor.id}><FlavorCard flavor={flavor} /></li>)}</ul>}
      {!isLoading && !error && total > 0 && <nav className="pagination" aria-label="Flavor pages"><button disabled={page === 1} onClick={() => setPage((value) => value - 1)}>Previous</button><span>Page {page} of {totalPages}</span><button disabled={page >= totalPages} onClick={() => setPage((value) => value + 1)}>Next</button></nav>}
    </section>
  </>
}
