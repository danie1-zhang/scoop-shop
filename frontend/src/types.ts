export type Flavor = {
    id: number
    name: string
    description: string
    price: string
    available: boolean
    created_at: string
}

export type FlavorListResponse = {
    items: Flavor[]
    page: number
    page_size: number
    total: number
}

export type FlavorCreateRequest = {
  name: string
  description: string
  price: string
  available: boolean
}

export type FlavorUpdateRequest = Partial<FlavorCreateRequest>

export type UserRole = 'customer' | 'admin'

export type User = {
  id: number
  email: string
  role: UserRole
  created_at: string
}

export type LoginCredentials = {
  email: string
  password: string
}

export type RegisterCredentials = {
  email: string
  password: string
}

export type TokenResponse = {
  access_token: string
  token_type: string
}

export type CartItemRequest = {
  flavor_id: number
  quantity: number
}

export type CartItemUpdateRequest = {
  quantity: number
}

export type CartItemResponse = {
  id: number
  user_id: number
  flavor_id: number
  quantity: number
  created_at: string
  flavor: Flavor
}

export type OrderItemResponse = {
  id: number
  order_id: number
  flavor_id: number
  flavor_name_at_purchase: string
  quantity: number
  price_at_purchase: string
}

export type OrderResponse = {
  id: number
  user_id: number
  total_price: string
  created_at: string
  items: OrderItemResponse[]
}

export type OrderListResponse = {
  items: OrderResponse[]
  page: number
  page_size: number
  total: number
}
