#!/bin/bash

# Test Dead Stock Risk API Endpoints

echo "=== Testing Dead Stock Risk API ==="
echo

# 1. Get all dead stock risk items
echo "1. Fetching all dead stock risk items:"
curl -X GET "http://localhost:8000/dead_stock_risk" \
  -H "Accept: application/json" | jq '.'

echo
echo "----------------------------------------"
echo

# 2. Get dead stock risk items for a specific category (Meat)
echo "2. Fetching dead stock risk items for Meat category:"
curl -X GET "http://localhost:8000/dead_stock_risk?category=Meat" \
  -H "Accept: application/json" | jq '.'

echo
echo "----------------------------------------"
echo

# 3. Get dead stock risk items for Dairy category
echo "3. Fetching dead stock risk items for Dairy category:"
curl -X GET "http://localhost:8000/dead_stock_risk?category=Dairy" \
  -H "Accept: application/json" | jq '.'

echo
echo "----------------------------------------"
echo

# 4. Get dead stock risk items for Snacks category
echo "4. Fetching dead stock risk items for Snacks category:"
curl -X GET "http://localhost:8000/dead_stock_risk?category=Snacks" \
  -H "Accept: application/json" | jq '.'

echo
echo "----------------------------------------"
echo

# 5. Test with invalid category (should return empty array)
echo "5. Testing with invalid category:"
curl -X GET "http://localhost:8000/dead_stock_risk?category=InvalidCategory" \
  -H "Accept: application/json" | jq '.'

echo
echo "----------------------------------------"
echo

# 6. Get count of dead stock items per category
echo "6. Getting count summary:"
echo "Total items at risk:"
curl -s -X GET "http://localhost:8000/dead_stock_risk" \
  -H "Accept: application/json" | jq '. | length'

echo
echo "=== Testing Complete ===" 