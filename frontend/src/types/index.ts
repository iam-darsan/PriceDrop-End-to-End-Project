export interface User {
  id: number;
  email: string;
  name?: string;
  google_id: string;
  profile_picture?: string;
  created_at: string;
}

export interface Product {
  id: number;
  user_id: number;
  url: string;
  name?: string;
  current_price?: number;
  currency?: string;
  image_url?: string;
  is_active: boolean;
  check_interval_minutes: number;
  last_checked_at?: string;
  created_at: string;
  updated_at: string;
  alert_count?: number;
}

export interface ProductCreate {
  url: string;
  target_price: number;
  check_interval_minutes?: number;
  manual_price?: number;
  manual_name?: string;
  manual_currency?: string;
}

export interface ProductUpdate {
  check_interval_minutes?: number;
  is_active?: boolean;
}

export interface PriceAlert {
  id: number;
  product_id: number;
  target_price: number;
  is_active: boolean;
  triggered_at?: string;
  created_at: string;
}

export interface AlertCreate {
  target_price: number;
}

export interface AlertUpdate {
  target_price?: number;
  is_active?: boolean;
}

export interface PriceHistory {
  id: number;
  product_id: number;
  price: number;
  recorded_at: string;
}

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  isLoading: boolean;
}
