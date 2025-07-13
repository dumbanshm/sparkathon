// TypeScript Interfaces for Waste Reduction API

// Base Types
export interface Product {
  product_id: string;
  name: string;
  category: string;
  brand: string;
  diet_type: 'vegan' | 'vegetarian' | 'eggs' | 'non-vegetarian';
  allergens: string[];
  shelf_life_days: number;
  packaging_date: string;
  expiry_date: string;
  days_until_expiry: number;
  weight_grams: number;
  price_mrp: number;
  cost_price: number | null;
  current_discount_percent: number;
  inventory_quantity: number;
  initial_inventory_quantity: number | null;
  total_cost: number | null;
  revenue_generated: number;
  store_location_lat: number;
  store_location_lon: number;
  is_dead_stock_risk: 0 | 1;
}

export interface User {
  id: string;
  name: string;
  diet_type: string;
  allergies: string[];
  prefers_discount: boolean;
}

export interface Recommendation {
  product_id: string;
  product_name: string;
  name: string;
  category: string;
  days_until_expiry: number;
  price: number;
  price_mrp: number;
  discount: number;
  current_discount_percent: number;
  expiry_date: string;
  score: number;
  is_dead_stock_risk: 0 | 1;
}

export interface DeadStockRiskItem {
  product_id: string;
  name: string;
  category: string;
  days_until_expiry: number;
  current_discount_percent: number;
  price_mrp: number;
  inventory_quantity: number;
  expiry_date: string;
  risk_score: number;
  threshold: number;
}

// Request Types
export interface TransactionRequest {
  user_id: string;
  product_id: string;
  quantity: number;
}

export interface ProductsFilterParams {
  category?: string;
  diet_type?: string;
  min_discount?: number;
  max_days_until_expiry?: number;
}

export interface RecommendationsParams {
  n?: number; // default: 10, max: 50
}

// Response Types
export interface HealthResponse {
  status: string;
  model_status: string;
  database_status: string;
  api_version: string;
}

export interface TransactionResponse {
  transaction_id: number;
  user_id: string;
  product_id: string;
  quantity: number;
  price_paid_per_unit: number;
  total_price_paid: number;
  discount_percent: number;
  message: string;
}

export interface DynamicPricingResponse {
  product_id: string;
  product_name: string;
  days_until_expiry: number;
  current_discount: number;
  recommended_discount: number;
  discount_increase: number;
  urgency_score: number;
  reasoning: string;
  current_price: number;
  recommended_price: number;
  savings: number;
  is_dead_stock_risk: boolean;
}

export interface RecommendationsResponse {
  user_id: string;
  recommendations: Recommendation[];
}

export interface ExpiredProductsResponse {
  total_expired_products: number;
  total_expired_value: number;
  category_split: { [category: string]: number };
  category_details: Array<{
    category: string;
    product_count: number;
    total_quantity: number;
    total_value: number;
    percentage_of_total: number;
  }>;
}

export interface CategoriesResponse {
  categories: string[];
}

export interface UsersResponse {
  users: User[];
}

export interface RefreshDataResponse {
  message: string;
  status: string;
}

export interface ErrorResponse {
  detail: string;
}

// API Client Example
export class WasteReductionAPI {
  private baseURL: string;

  constructor(baseURL: string = 'http://localhost:8000') {
    this.baseURL = baseURL;
  }

  async getHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseURL}/health`);
    return response.json();
  }

  async getProducts(filters?: ProductsFilterParams): Promise<Product[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value !== undefined) params.append(key, String(value));
      });
    }
    const response = await fetch(`${this.baseURL}/products?${params}`);
    return response.json();
  }

  async createTransaction(
    transaction: TransactionRequest,
    useDynamicPricing: boolean = true
  ): Promise<TransactionResponse> {
    const response = await fetch(
      `${this.baseURL}/transactions?use_dynamic_pricing=${useDynamicPricing}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(transaction),
      }
    );
    if (!response.ok) {
      throw new Error((await response.json()).detail);
    }
    return response.json();
  }

  async getDynamicPricing(productId: string): Promise<DynamicPricingResponse> {
    const response = await fetch(`${this.baseURL}/dynamic_pricing/${productId}`);
    return response.json();
  }

  async getRecommendations(
    userId: string,
    params?: RecommendationsParams
  ): Promise<RecommendationsResponse> {
    const queryParams = params?.n ? `?n=${params.n}` : '';
    const response = await fetch(
      `${this.baseURL}/recommendations/${userId}${queryParams}`
    );
    return response.json();
  }

  async getDeadStockRisk(category?: string): Promise<DeadStockRiskItem[]> {
    const params = category ? `?category=${category}` : '';
    const response = await fetch(`${this.baseURL}/dead_stock_risk${params}`);
    return response.json();
  }

  async getExpiredProducts(): Promise<ExpiredProductsResponse> {
    const response = await fetch(`${this.baseURL}/expired_products`);
    return response.json();
  }

  async getCategories(): Promise<CategoriesResponse> {
    const response = await fetch(`${this.baseURL}/categories`);
    return response.json();
  }

  async getUsers(): Promise<UsersResponse> {
    const response = await fetch(`${this.baseURL}/users`);
    return response.json();
  }

  async refreshData(): Promise<RefreshDataResponse> {
    const response = await fetch(`${this.baseURL}/refresh_data`, {
      method: 'POST',
    });
    return response.json();
  }
} 