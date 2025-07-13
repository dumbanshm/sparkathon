# Frontend API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently no authentication required (add if needed)

---

## 1. Health Check

### Request
```http
GET /health
```

### Response
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "database_status": "connected",
  "api_version": "3.0.0"
}
```

---

## 2. Products

### Get All Products
#### Request
```http
GET /products
```

#### Query Parameters (all optional)
- `category` (string): Filter by category (e.g., "Meat", "Dairy", "Snacks")
- `diet_type` (string): Filter by diet type (e.g., "vegan", "vegetarian", "non-vegetarian")
- `min_discount` (number): Minimum discount percentage (0-100)
- `max_days_until_expiry` (number): Maximum days until expiry

#### Example Request
```http
GET /products?category=Dairy&min_discount=20&max_days_until_expiry=7
```

#### Response
```json
[
  {
    "product_id": "P0001",
    "name": "Fresh Milk",
    "category": "Dairy",
    "brand": "Amul",
    "diet_type": "vegetarian",
    "allergens": ["dairy"],
    "shelf_life_days": 7,
    "packaging_date": "2025-01-10",
    "expiry_date": "2025-01-17",
    "days_until_expiry": 4,
    "weight_grams": 500,
    "price_mrp": 45.0,
    "cost_price": 19.13,
    "current_discount_percent": 30.0,
    "inventory_quantity": 150,
    "revenue_generated": 2500.50,
    "store_location_lat": 28.6139,
    "store_location_lon": 77.2090,
    "is_dead_stock_risk": 1
  }
]
```

---

## 3. Create Transaction (Purchase)

### Request
```http
POST /transactions
```

#### Headers
```
Content-Type: application/json
```

#### Request Body
```json
{
  "user_id": "U0001",
  "product_id": "P0001",
  "quantity": 2
}
```

#### Query Parameters (optional)
- `use_dynamic_pricing` (boolean): Default is `true`. Set to `false` for static pricing

#### Response
```json
{
  "transaction_id": 1234,
  "user_id": "U0001",
  "product_id": "P0001",
  "quantity": 2,
  "price_paid_per_unit": 31.50,
  "total_price_paid": 63.00,
  "discount_percent": 30.0,
  "message": "Transaction created successfully with dynamic pricing. Inventory and revenue updated automatically."
}
```

#### Error Responses
- **404 Not Found**: User or product not found
```json
{
  "detail": "Product P9999 not found"
}
```

- **400 Bad Request**: Insufficient inventory
```json
{
  "detail": "Insufficient inventory. Available: 5"
}
```

---

## 4. Dynamic Pricing Check

### Request
```http
GET /dynamic_pricing/{product_id}
```

#### Example
```http
GET /dynamic_pricing/P0001
```

#### Response
```json
{
  "product_id": "P0001",
  "product_name": "Fresh Milk",
  "days_until_expiry": 4,
  "current_discount": 30.0,
  "recommended_discount": 45.0,
  "discount_increase": 15.0,
  "urgency_score": 0.75,
  "reasoning": "Approaching expiry, Low sales velocity",
  "current_price": 31.50,
  "recommended_price": 24.75,
  "savings": 6.75,
  "is_dead_stock_risk": true
}
```

---

## 5. Personalized Recommendations

### Request
```http
GET /recommendations/{user_id}
```

#### Query Parameters
- `n` (number): Number of recommendations (default: 10, max: 50)

#### Example
```http
GET /recommendations/U0001?n=5
```

#### Response
```json
{
  "user_id": "U0001",
  "recommendations": [
    {
      "product_id": "P0023",
      "product_name": "Organic Yogurt",
      "name": "Organic Yogurt",
      "category": "Dairy",
      "days_until_expiry": 5,
      "price": 120.0,
      "price_mrp": 120.0,
      "discount": 35.0,
      "current_discount_percent": 35.0,
      "expiry_date": "2025-01-18",
      "score": 0.85,
      "is_dead_stock_risk": 1
    }
  ]
}
```

---

## 6. Dead Stock Risk Items

### Request
```http
GET /dead_stock_risk
```

#### Query Parameters
- `category` (string): Filter by category (optional)

#### Example
```http
GET /dead_stock_risk?category=Meat
```

#### Response
```json
[
  {
    "product_id": "P0045",
    "name": "Chicken Breast",
    "category": "Meat",
    "days_until_expiry": 2,
    "current_discount_percent": 50.0,
    "price_mrp": 250.0,
    "inventory_quantity": 80,
    "expiry_date": "2025-01-15",
    "risk_score": 0.95,
    "threshold": 5
  }
]
```

---

## 7. Expired Products Summary

### Request
```http
GET /expired_products
```

#### Response
```json
{
  "total_expired_products": 16,
  "total_expired_value": 736175.80,
  "category_split": {
    "Snacks": 20.44,
    "Biscuits": 20.11,
    "Dairy": 19.99,
    "Cheese": 15.73,
    "Sauces": 12.20,
    "Beverages": 7.04,
    "Meat": 4.48
  },
  "category_details": [
    {
      "category": "Snacks",
      "product_count": 3,
      "total_quantity": 605,
      "total_value": 150488.66,
      "percentage_of_total": 20.44
    }
  ]
}
```

---

## 8. Categories

### Request
```http
GET /categories
```

#### Response
```json
{
  "categories": [
    "Beverages",
    "Biscuits",
    "Cheese",
    "Dairy",
    "Meat",
    "Sauces",
    "Snacks",
    "Spreads"
  ]
}
```

---

## 9. Users

### Request
```http
GET /users
```

#### Response
```json
{
  "users": [
    {
      "id": "U0001",
      "name": "User U0001",
      "diet_type": "vegetarian",
      "allergies": ["nuts", "dairy"],
      "prefers_discount": true
    }
  ]
}
```

---

## 10. Refresh Data

### Request
```http
POST /refresh_data
```

#### Response
```json
{
  "message": "Data refreshed successfully",
  "status": "success"
}
```

---

## Data Types Reference

### Product Fields
- `product_id`: string (e.g., "P0001")
- `name`: string
- `category`: string (one of: "Beverages", "Biscuits", "Cheese", "Dairy", "Meat", "Sauces", "Snacks", "Spreads")
- `brand`: string
- `diet_type`: string (one of: "vegan", "vegetarian", "eggs", "non-vegetarian")
- `allergens`: array of strings (e.g., ["nuts", "dairy"])
- `price_mrp`: number (Maximum Retail Price)
- `cost_price`: number (Cost price, ~40-45% of MRP)
- `current_discount_percent`: number (0-100)
- `days_until_expiry`: number (can be negative if expired)
- `inventory_quantity`: number (current inventory)
- `initial_inventory_quantity`: number (original inventory when product was added)
- `total_cost`: number (initial investment = initial_inventory_quantity × cost_price)
- `revenue_generated`: number (total sales revenue)
- `is_dead_stock_risk`: number (0 or 1)

### User Fields
- `user_id`: string (e.g., "U0001")
- `diet_type`: string
- `allergies`: array of strings
- `prefers_discount`: boolean

### Transaction Fields
- `transaction_id`: number (auto-generated)
- `user_id`: string
- `product_id`: string
- `quantity`: number (minimum: 1)
- `price_paid_per_unit`: number
- `total_price_paid`: number
- `discount_percent`: number

---

## Frontend Integration Tips

1. **Product Listing**: Use `/products` with filters for category pages
2. **Homepage**: Show `/dead_stock_risk` items with urgency badges
3. **User Dashboard**: Use `/recommendations/{user_id}` for personalized suggestions
4. **Product Details**: Use `/dynamic_pricing/{product_id}` to show potential savings
5. **Checkout**: POST to `/transactions` with dynamic pricing enabled
6. **Analytics**: Use `/expired_products` for waste metrics dashboard

## Error Handling

All errors follow this format:
```json
{
  "detail": "Error message here"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request (e.g., validation error)
- 404: Not Found
- 500: Internal Server Error 