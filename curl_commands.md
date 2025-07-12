# Dead Stock Risk API - Curl Commands

## Basic Requests

### 1. Get all dead stock risk items
```bash
curl -X GET "http://localhost:8000/dead_stock_risk"
```

### 2. Get all dead stock risk items (with pretty JSON output)
```bash
curl -X GET "http://localhost:8000/dead_stock_risk" | jq '.'
```

### 3. Get dead stock risk items for a specific category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Meat"
```

### 4. Get dead stock risk items with headers
```bash
curl -X GET "http://localhost:8000/dead_stock_risk" \
  -H "Accept: application/json" \
  -H "Content-Type: application/json"
```

## Category-Specific Requests

### Meat Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Meat"
```

### Dairy Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Dairy"
```

### Snacks Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Snacks"
```

### Beverages Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Beverages"
```

### Biscuits Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Biscuits"
```

### Sauces Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Sauces"
```

### Spreads Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Spreads"
```

### Cheese Category
```bash
curl -X GET "http://localhost:8000/dead_stock_risk?category=Cheese"
```

## Advanced Queries

### Get count of items at risk
```bash
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '. | length'
```

### Get only product IDs, names and inventory
```bash
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '.[] | {product_id, name, inventory_quantity}'
```

### Get items sorted by days until expiry
```bash
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq 'sort_by(.days_until_expiry)'
```

### Get items with less than 7 days until expiry
```bash
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '.[] | select(.days_until_expiry < 7)'
```

### Get items with high inventory (> 200 units)
```bash
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '.[] | select(.inventory_quantity > 200)'
```

### Get summary statistics
```bash
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '{
  total_items: length,
  avg_days_until_expiry: (map(.days_until_expiry) | add / length),
  avg_discount: (map(.current_discount_percent) | add / length),
  total_inventory_at_risk: (map(.inventory_quantity) | add),
  avg_inventory: (map(.inventory_quantity) | add / length),
  categories: (group_by(.category) | map({category: .[0].category, count: length, total_inventory: (map(.inventory_quantity) | add)}))
}'
```

## Other Endpoints

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```

### Get Categories
```bash
curl -X GET "http://localhost:8000/categories"
```

### Get Recommendations for a User
```bash
curl -X GET "http://localhost:8000/recommendations/U0000?n=5"
```

### Get Users
```bash
curl -X GET "http://localhost:8000/users"
```

### Refresh Data from Supabase
```bash
curl -X POST "http://localhost:8000/refresh_data"
```

## Response Format

The dead stock risk endpoint returns an array of items with this structure:
```json
{
  "product_id": "P0123",
  "name": "Product Name",
  "category": "Meat",
  "days_until_expiry": 5,
  "current_discount_percent": 30.0,
  "price_mrp": 150.0,
  "inventory_quantity": 250,
  "expiry_date": "2025-07-17",
  "risk_score": 0.8,
  "threshold": 10
}
```

## Notes

- Replace `localhost:8000` with your actual API URL if different
- The API returns JSON responses
- Use `jq` for pretty-printing and filtering JSON output
- The `category` parameter is case-sensitive and must match exactly
- The `inventory_quantity` field shows current inventory levels for each at-risk product 