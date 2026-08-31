import type {
  CartItemRequest,
  CartItemResponse,
  CartItemUpdateRequest,
  Flavor,
  FlavorListResponse,
  FlavorCreateRequest,
  FlavorUpdateRequest,
  LoginCredentials,
  OrderResponse,
  OrderListResponse,
  RegisterCredentials,
  TokenResponse,
  User,
} from './types'

const API_URL = import.meta.env.VITE_API_URL

async function getErrorMessage(response: Response, fallback: string) {
  try {
    const body = (await response.json()) as { detail?: string }
    return body.detail ?? fallback
  } catch {
    return fallback
  }
}

export async function getFlavors(
  page: number = 1,
  pageSize: number = 5,
): Promise<FlavorListResponse> {
  const response = await fetch(
    `${API_URL}/api/flavors?page=${page}&page_size=${pageSize}`,
  )

  if (!response.ok) {
    throw new Error('Unable to load flavors')
  }

  return response.json()
}

export async function login(
  credentials: LoginCredentials,
): Promise<TokenResponse> {
  const response = await fetch(`${API_URL}/api/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    throw new Error('Invalid email or password')
  }

  return response.json()
}

export async function register(
  credentials: RegisterCredentials,
): Promise<User> {
  const response = await fetch(`${API_URL}/api/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(credentials),
  })

  if (!response.ok) {
    if (response.status === 409) {
      throw new Error('An account with this email already exists')
    }

    throw new Error('Unable to create account')
  }

  return response.json()
}

export async function getCurrentUser(token: string): Promise<User> {
  const response = await fetch(`${API_URL}/api/me`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Unable to load current user')
  }

  return response.json()
}

export async function addCartItem(
  token: string,
  item: CartItemRequest,
): Promise<CartItemResponse> {
  const response = await fetch(`${API_URL}/api/cart/items`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(item),
  })

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to add item to cart'))
  }

  return response.json()
}

export async function getCartItems(token: string): Promise<CartItemResponse[]> {
  const response = await fetch(`${API_URL}/api/cart`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error('Unable to load cart items')
  }

  return response.json()
}

export async function updateCartItem(
  token: string,
  cartItemId: number,
  update: CartItemUpdateRequest,
): Promise<CartItemResponse> {
  const response = await fetch(`${API_URL}/api/cart/items/${cartItemId}`, {
    method: 'PATCH',
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(update),
  })

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to update cart item'))
  }

  return response.json()
}

export async function createOrder(token: string): Promise<OrderResponse> {
  const response = await fetch(`${API_URL}/api/orders`, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  })

  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to create order'))
  }

  return response.json()
}

export async function deleteCartItem(token: string, cartItemId: number) {
  const response = await fetch(`${API_URL}/api/cart/items/${cartItemId}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to remove cart item'))
  }
}

export async function getOrders(
  token: string,
  page = 1,
  pageSize = 5,
): Promise<OrderListResponse> {
  const response = await fetch(
    `${API_URL}/api/orders?page=${page}&page_size=${pageSize}`,
    { headers: { Authorization: `Bearer ${token}` } },
  )
  if (!response.ok) {
    throw new Error(await getErrorMessage(response, 'Unable to load orders'))
  }
  return response.json()
}

export async function getManagedFlavors(token: string): Promise<Flavor[]> {
  const response = await fetch(`${API_URL}/api/flavors/manage`, {
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) throw new Error(await getErrorMessage(response, 'Unable to load flavors'))
  return response.json()
}

export async function createFlavor(token: string, data: FlavorCreateRequest): Promise<Flavor> {
  const response = await fetch(`${API_URL}/api/flavors`, {
    method: 'POST',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(await getErrorMessage(response, 'Unable to create flavor'))
  return response.json()
}

export async function updateFlavor(token: string, id: number, data: FlavorUpdateRequest): Promise<Flavor> {
  const response = await fetch(`${API_URL}/api/flavors/${id}`, {
    method: 'PATCH',
    headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  })
  if (!response.ok) throw new Error(await getErrorMessage(response, 'Unable to update flavor'))
  return response.json()
}

export async function deleteFlavor(token: string, id: number) {
  const response = await fetch(`${API_URL}/api/flavors/${id}`, {
    method: 'DELETE',
    headers: { Authorization: `Bearer ${token}` },
  })
  if (!response.ok) throw new Error(await getErrorMessage(response, 'Unable to delete flavor'))
}
