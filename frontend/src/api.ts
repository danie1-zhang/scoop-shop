import type {
  CartItemRequest,
  CartItemResponse,
  CartItemUpdateRequest,
  FlavorListResponse,
  LoginCredentials,
  OrderResponse,
  RegisterCredentials,
  TokenResponse,
  User,
} from './types'

const API_URL = import.meta.env.VITE_API_URL

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
    throw new Error('Unable to add item to cart')
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
    throw new Error('Unable to update cart item')
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
    let message = 'Unable to create order'

    try {
      const errorBody = (await response.json()) as { detail?: string }
      message = errorBody.detail ?? message
    } catch {
      // Keep the generic message when the server does not return JSON.
    }

    throw new Error(message)
  }

  return response.json()
}
