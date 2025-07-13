# API Curl Commands

## Products Endpoint

### 1. Get all products
```bash
curl -X GET "http://localhost:8000/products"
```

### 2. Get all products (with pretty JSON)
```bash
curl -X GET "http://localhost:8000/products" | jq '.'
```

### 3. Filter products by category
```bash
curl -X GET "http://localhost:8000/products?category=Meat"
```

### 4. Filter products by diet type
```bash
curl -X GET "http://localhost:8000/products?diet_type=vegan"
```

### 5. Filter products by minimum discount
```bash
curl -X GET "http://localhost:8000/products?min_discount=30"
```

### 6. Filter products expiring soon
```bash
curl -X GET "http://localhost:8000/products?max_days_until_expiry=7"
```

### 7. Combine multiple filters
```bash
curl -X GET "http://localhost:8000/products?category=Dairy&min_discount=20&max_days_until_expiry=14"
```

### 8. Get product count
```bash
curl -s -X GET "http://localhost:8000/products" | jq 'length'
```

## Dead Stock Risk API

### Basic Requests

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

## Expired Products API

### 1. Get expired products summary
```bash
curl -X GET "http://localhost:8000/expired_products"
```

### 2. Get expired products summary (with pretty JSON)
```bash
curl -X GET "http://localhost:8000/expired_products" | jq '.'
```

### 3. Get only the category split percentages
```bash
curl -s -X GET "http://localhost:8000/expired_products" | jq '.category_split'
```

### 4. Get category details sorted by value
```bash
curl -s -X GET "http://localhost:8000/expired_products" | jq '.category_details'
```

### 5. Get total expired products count and value
```bash
curl -s -X GET "http://localhost:8000/expired_products" | jq '{total_products: .total_expired_products, total_value: .total_expired_value}'
```

### Response Format

The expired products endpoint returns:
```json
{
  "total_expired_products": 25,
  "total_expired_value": 37500.50,
  "category_split": {
    "Meat": 35.5,
    "Dairy": 28.3,
    "Snacks": 20.1,
    "Beverages": 10.2,
    "Sauces": 5.9
  },
  "category_details": [
    {
      "category": "Meat",
      "product_count": 8,
      "total_quantity": 450,
      "total_value": 13312.88,
      "percentage_of_total": 35.5
    },
    {
      "category": "Dairy",
      "product_count": 6,
      "total_quantity": 380,
      "total_value": 10612.65,
      "percentage_of_total": 28.3
    }
    // ... more categories
  ]
}
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

## Transaction API

### 1. Create a transaction (dynamic pricing - default)
```bash
curl -X POST "http://localhost:8000/transactions" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "U0001",
    "product_id": "P0123",
    "quantity": 2
  }'
```

### 2. Create transaction with static pricing (optional)
```bash
curl -X POST "http://localhost:8000/transactions?use_dynamic_pricing=false" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "U0001",
    "product_id": "P0001",
    "quantity": 1
  }'
```

### 3. Check dynamic pricing for a product (without buying)
```bash
curl -X GET "http://localhost:8000/dynamic_pricing/P0001"
```

### Response Format - Transaction
```json
{
  "transaction_id": 1234,
  "user_id": "U0001",
  "product_id": "P0123",
  "quantity": 2,
  "price_paid_per_unit": 135.0,
  "total_price_paid": 270.0,
  "discount_percent": 35.0,
  "message": "Transaction created successfully with dynamic pricing. Inventory and revenue updated automatically."
}
```

### Response Format - Dynamic Pricing Check
```json
{
  "product_id": "P0001",
  "product_name": "Fresh Milk",
  "days_until_expiry": 5,
  "current_discount": 10.0,
  "recommended_discount": 35.0,
  "discount_increase": 25.0,
  "urgency_score": 0.85,
  "reasoning": "Approaching expiry, Low sales velocity, High dead stock risk",
  "current_price": 45.0,
  "recommended_price": 32.5,
  "savings": 12.5,
  "is_dead_stock_risk": true
}
```

### Dynamic Pricing Factors

The dynamic pricing engine considers:
- **Expiry urgency**: Higher discounts as expiry approaches
- **Sales velocity**: More discount for slow-moving items
- **Inventory pressure**: Higher discounts if stock won't clear before expiry
- **Category factors**: Perishables get more aggressive pricing
- **Current discount effectiveness**: Increases if current discount isn't working
- **Dead stock risk**: Extra urgency for at-risk products

## Product Profitability (Supabase SQL Query)

After running the migration, you can use this SQL query in Supabase:

```sql
-- Get product profitability report
SELECT * FROM get_product_profitability();

-- Get top 10 revenue generating products
SELECT * FROM get_product_profitability() LIMIT 10;

-- Get profitability by category
SELECT 
    category,
    COUNT(*) as product_count,
    SUM(revenue_generated) as total_revenue,
    SUM(gross_profit) as total_profit,
    AVG(profit_margin) as avg_margin
FROM get_product_profitability()
GROUP BY category
ORDER BY total_revenue DESC;
```

## Inventory Analytics API

### 1. Get all inventory analytics
```bash
curl -X GET "http://localhost:8000/inventory_analytics"
```

### 2. Get analytics by category
```bash
curl -X GET "http://localhost:8000/inventory_analytics?category=Dairy"
```

### 3. Get products with minimum profit margin
```bash
curl -X GET "http://localhost:8000/inventory_analytics?min_profit_margin=20"
```

### Response Format
```json
{
  "total_initial_investment": 1250000.50,
  "total_revenue_generated": 450000.25,
  "total_gross_profit": 125000.75,
  "average_profit_margin": 27.8,
  "total_units_sold": 3500,
  "products_analyzed": 150,
  "products": [
    {
      "product_id": "P0001",
      "name": "Fresh Milk",
      "category": "Dairy",
      "initial_inventory_quantity": 200,
      "current_inventory": 50,
      "units_sold": 150,
      "cost_price": 19.13,
      "price_mrp": 45.0,
      "initial_investment": 3826.0,
      "revenue_generated": 4725.0,
      "gross_profit": 1855.5,
      "profit_margin": 39.3,
      "days_until_expiry": 5,
      "current_discount_percent": 30
    }
  ]
}
```

## Response Format

The dead stock risk endpoint returns an array of items with this structure:
```json
[
  {
    "product_id": "P0001",
    "name": "Product A",
    "inventory_quantity": 100,
    "days_until_expiry": 15,
    "current_discount_percent": 10.5,
    "category": "Meat"
  },
  {
    "product_id": "P0002",
    "name": "Product B",
    "inventory_quantity": 200,
    "days_until_expiry": 5,
    "current_discount_percent": 5.0,
    "category": "Dairy"
  }
]
```