#!/bin/bash

echo "Testing Dead Stock Risk endpoint with inventory..."
echo

# Get dead stock risk items and display inventory
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '.[] | {
  product_id: .product_id,
  name: .name,
  inventory_quantity: .inventory_quantity,
  days_until_expiry: .days_until_expiry,
  risk_score: .risk_score
}' | head -20

echo
echo "Getting inventory summary..."
curl -s -X GET "http://localhost:8000/dead_stock_risk" | jq '[.[] | .inventory_quantity] | {
  total_items: length,
  total_inventory: add,
  avg_inventory: (add / length),
  min_inventory: min,
  max_inventory: max
}' 