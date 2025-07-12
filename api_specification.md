# Waste Reduction System API Specification

## Overview

The Waste Reduction System API provides endpoints for personalized product recommendations and dead stock risk analysis to minimize food waste in retail environments.

**Base URL**: `http://localhost:8000`  
**Version**: 1.0.0  
**Protocol**: HTTP/REST  
**Content-Type**: `application/json`

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## CORS Policy

The API supports Cross-Origin Resource Sharing (CORS) with the following configuration:
- **Allowed Origins**: * (all origins)
- **Allowed Methods**: * (all HTTP methods)
- **Allowed Headers**: * (all headers)

## Endpoints

### 1. Health Check

Check the API and model status.

**Endpoint**: `GET /health`

**Response**:
```json
{
  "status": "healthy",
  "model_status": "loaded",
  "api_version": "1.0.0"
}
```

**Status Codes**:
- `200 OK`: Service is healthy
- `500 Internal Server Error`: Service unhealthy

---

### 2. Get Users

Retrieve all available users with their dietary preferences and allergies.

**Endpoint**: `GET /users`

**Response**:
```json
{
  "users": [
    {
      "id": "U0001",
      "name": "User U0001",
      "diet_type": "vegan",
      "allergies": "['nuts', 'dairy']",
      "prefers_discount": true
    },
    {
      "id": "U0002",
      "name": "User U0002",
      "diet_type": "vegetarian",
      "allergies": "['gluten']",
      "prefers_discount": false
    }
  ]
}
```

**Status Codes**:
- `200 OK`: Success
- `500 Internal Server Error`: Model not loaded or processing error

---

### 3. Get Categories

Retrieve all available product categories.

**Endpoint**: `GET /categories`

**Response**:
```json
{
  "categories": [
    "Biscuits",
    "Sauces",
    "Meat",
    "Cheese",
    "Beverages",
    "Dairy",
    "Snacks",
    "Spreads"
  ]
}
```

**Status Codes**:
- `200 OK`: Success
- `500 Internal Server Error`: Model not loaded or processing error

---

### 4. Get Personalized Recommendations

Get personalized product recommendations for a specific user based on their preferences, purchase history, and dietary restrictions.

**Endpoint**: `GET /recommendations/{user_id}`

**Parameters**:
- `user_id` (path, required): The unique identifier of the user (e.g., "U0001")
- `n` (query, optional): Number of recommendations to return (default: 10, min: 1, max: 50)

**Example Request**:
```
GET /recommendations/U0001?n=5
```

**Response**:
```json
{
  "user_id": "U0001",
  "recommendations": [
    {
      "product_id": "P0123",
      "product_name": "Organic Tomato Sauce",
      "name": "Organic Tomato Sauce",
      "category": "Sauces",
      "days_until_expiry": 7,
      "price": 245.50,
      "price_mrp": 245.50,
      "discount": 30.0,
      "current_discount_percent": 30.0,
      "expiry_date": "2024-01-20",
      "score": 8.5,
      "is_dead_stock_risk": 1
    },
    {
      "product_id": "P0124",
      "product_name": "Whole Wheat Biscuits",
      "name": "Whole Wheat Biscuits",
      "category": "Biscuits",
      "days_until_expiry": 15,
      "price": 120.00,
      "price_mrp": 120.00,
      "discount": 20.0,
      "current_discount_percent": 20.0,
      "expiry_date": "2024-01-28",
      "score": 7.2,
      "is_dead_stock_risk": 0
    }
  ]
}
```

**Response Fields**:
- `product_id`: Unique product identifier
- `product_name` / `name`: Product name (both fields contain the same value)
- `category`: Product category
- `days_until_expiry`: Days remaining until product expires
- `price` / `price_mrp`: Current price after discount (in rupees)
- `discount` / `current_discount_percent`: Current discount percentage
- `expiry_date`: Product expiration date
- `score`: Recommendation score (higher is better)
- `is_dead_stock_risk`: Binary flag (1 = at risk, 0 = not at risk)

**Status Codes**:
- `200 OK`: Success (may return empty recommendations array if no suitable products)
- `500 Internal Server Error`: Model not loaded or processing error

---

### 5. Get Dead Stock Risk Items

Retrieve products at risk of becoming dead stock (low sales velocity, approaching expiry).

**Endpoint**: `GET /dead_stock_risk`

**Parameters**:
- `category` (query, optional): Filter by product category

**Example Requests**:
```
GET /dead_stock_risk
GET /dead_stock_risk?category=Dairy
```

**Response**:
```json
[
  {
    "product_id": "P0015",
    "name": "Fresh Milk",
    "category": "Dairy",
    "days_until_expiry": 3,
    "current_discount_percent": 40.0,
    "price_mrp": 65.00,
    "expiry_date": "2024-01-16",
    "risk_score": null,
    "threshold": null
  },
  {
    "product_id": "P0018",
    "name": "Cheddar Cheese",
    "category": "Cheese",
    "days_until_expiry": 5,
    "current_discount_percent": 35.0,
    "price_mrp": 320.00,
    "expiry_date": "2024-01-18",
    "risk_score": null,
    "threshold": null
  }
]
```

**Response Fields**:
- `product_id`: Unique product identifier
- `name`: Product name
- `category`: Product category
- `days_until_expiry`: Days remaining until expiry
- `current_discount_percent`: Current discount applied
- `price_mrp`: Maximum retail price
- `expiry_date`: Product expiration date
- `risk_score`: Risk assessment score (currently null)
- `threshold`: Dynamic threshold for the product (currently null)

**Status Codes**:
- `200 OK`: Success (may return empty array if no items at risk)
- `500 Internal Server Error`: Model not loaded or processing error

## Error Handling

All error responses follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

Common error scenarios:
- Model not loaded (500)
- Invalid user_id (500)
- Invalid category filter (500)
- Server processing errors (500)

## Rate Limiting

Currently, no rate limiting is implemented.

## Notes

1. **Dead Stock Risk**: Products are flagged as dead stock risk based on:
   - Days until expiry
   - Sales velocity
   - Dynamic thresholds per product category

2. **Recommendation Algorithm**: Uses a hybrid approach combining:
   - Content-based filtering (product similarity)
   - Collaborative filtering (user behavior patterns)
   - Urgency scoring (expiry date consideration)
   - Dietary restrictions and allergy filtering

3. **Data Freshness**: The model is loaded once at startup. To reflect new data, the server must be restarted with an updated model.

## OpenAPI Documentation

Interactive API documentation is available at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## Example Usage

### Python (requests)
```python
import requests

# Get recommendations for a user
response = requests.get("http://localhost:8000/recommendations/U0001?n=5")
recommendations = response.json()

# Get dead stock items in Dairy category
response = requests.get("http://localhost:8000/dead_stock_risk?category=Dairy")
at_risk_items = response.json()
```

### JavaScript (fetch)
```javascript
// Get all categories
fetch('http://localhost:8000/categories')
  .then(response => response.json())
  .then(data => console.log(data.categories));

// Get user recommendations
fetch('http://localhost:8000/recommendations/U0001?n=10')
  .then(response => response.json())
  .then(data => console.log(data.recommendations));
```

### cURL
```bash
# Health check
curl http://localhost:8000/health

# Get recommendations
curl "http://localhost:8000/recommendations/U0001?n=5"

# Get dead stock risk items
curl http://localhost:8000/dead_stock_risk
``` 