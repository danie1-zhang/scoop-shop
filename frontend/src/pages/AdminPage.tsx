import { useEffect, useState } from 'react'
import { createFlavor, deleteFlavor, getManagedFlavors, updateFlavor } from '../api'
import { useAuth } from '../auth/useAuth'
import type { Flavor, FlavorCreateRequest } from '../types'

const EMPTY_FORM: FlavorCreateRequest = { name: '', description: '', price: '', available: true }

export function AdminPage() {
  const { token } = useAuth()
  const [flavors, setFlavors] = useState<Flavor[]>([])
  const [form, setForm] = useState(EMPTY_FORM)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [saving, setSaving] = useState(false)

  async function reloadFlavors(authToken: string) {
    setFlavors(await getManagedFlavors(authToken))
  }

  useEffect(() => {
    if (!token) return
    let ignore = false
    async function synchronize() {
      try {
        const response = await getManagedFlavors(token!)
        if (!ignore) setFlavors(response)
      } catch (caught) {
        if (!ignore) setError(caught instanceof Error ? caught.message : 'Unable to load flavors')
      }
    }
    void synchronize()
    return () => { ignore = true }
  }, [token])

  function edit(flavor: Flavor) {
    setEditingId(flavor.id)
    setForm({ name: flavor.name, description: flavor.description, price: flavor.price, available: flavor.available })
    setError(null)
  }

  function reset() { setEditingId(null); setForm(EMPTY_FORM) }

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    if (!token) return
    setSaving(true); setError(null)
    try {
      if (editingId === null) await createFlavor(token, form)
      else await updateFlavor(token, editingId, form)
      reset(); await reloadFlavors(token)
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Unable to save flavor')
    } finally { setSaving(false) }
  }

  async function remove(id: number) {
    if (!token || !window.confirm('Delete this flavor permanently?')) return
    setError(null)
    try { await deleteFlavor(token, id); await reloadFlavors(token) }
    catch (caught) { setError(caught instanceof Error ? caught.message : 'Unable to delete flavor') }
  }

  return <section><h1>Flavor administration</h1><div className="admin-grid"><form className="admin-form panel" onSubmit={(event) => void submit(event)}><h2>{editingId === null ? 'Add flavor' : 'Edit flavor'}</h2><label>Name<input required maxLength={100} value={form.name} onChange={(event) => setForm({ ...form, name: event.target.value })} /></label><label>Description<textarea required maxLength={1000} value={form.description} onChange={(event) => setForm({ ...form, description: event.target.value })} /></label><label>Price<input required min="0.01" step="0.01" type="number" value={form.price} onChange={(event) => setForm({ ...form, price: event.target.value })} /></label><label className="checkbox"><input type="checkbox" checked={form.available} onChange={(event) => setForm({ ...form, available: event.target.checked })} /> Available to customers</label>{error && <p role="alert">{error}</p>}<div className="button-row"><button disabled={saving}>{saving ? 'Saving…' : 'Save flavor'}</button>{editingId !== null && <button className="secondary" type="button" onClick={reset}>Cancel</button>}</div></form><div><h2>All flavors</h2><ul className="manage-list">{flavors.map((flavor) => <li key={flavor.id}><div><strong>{flavor.name}</strong><span>{flavor.available ? 'Available' : 'Unavailable'} · ${flavor.price}</span></div><div className="button-row"><button className="secondary" onClick={() => edit(flavor)}>Edit</button><button className="danger" onClick={() => void remove(flavor.id)}>Delete</button></div></li>)}</ul></div></div></section>
}
