#!/bin/bash

# Test Products API Endpoints

echo "=== Testing Products API ===="
echo

# 1. Get all products
echo "1. Fetching all products:"
curl -X GET "http://localhost:8000/products" \
  -H "Accept: application/json" | jq '.[0:3]'  # Show first 3 products

echo
echo "----------------------------------------"
echo

# 2. Get products by category
echo "2. Fetching products in Meat category:"
curl -X GET "http://localhost:8000/products?category=Meat" \
  -H "Accept: application/json" | jq '.[0:3]'

echo
echo "----------------------------------------"
echo

# 3. Get products by diet type
echo "3. Fetching vegan products:"
curl -X GET "http://localhost:8000/products?diet_type=vegan" \
  -H "Accept: application/json" | jq '.[0:3]'

echo
echo "----------------------------------------"
echo

# 4. Get products with minimum discount
echo "4. Fetching products with at least 30% discount:"
curl -X GET "http://localhost:8000/products?min_discount=30" \
  -H "Accept: application/json" | jq '.[0:3]'

echo
echo "----------------------------------------"
echo

# 5. Get products expiring soon
echo "5. Fetching products expiring in next 7 days:"
curl -X GET "http://localhost:8000/products?max_days_until_expiry=7" \
  -H "Accept: application/json" | jq '.[0:3]'

echo
echo "----------------------------------------"
echo

# 6. Combined filters
echo "6. Fetching vegan products with discount expiring soon:"
curl -X GET "http://localhost:8000/products?diet_type=vegan&min_discount=20&max_days_until_expiry=14" \
  -H "Accept: application/json" | jq '.[0:3]'

echo
echo "----------------------------------------"
echo

# 7. Count products by category
echo "7. Product count by category:"
curl -s -X GET "http://localhost:8000/products" | jq 'group_by(.category) | map({category: .[0].category, count: length})'

echo
echo "----------------------------------------"
echo

# 8. Get products with high inventory
echo "8. Products with inventory > 250 units:"
curl -s -X GET "http://localhost:8000/products" | jq '.[] | select(.inventory_quantity > 250) | {product_id, name, inventory_quantity}' | head -20 