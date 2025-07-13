import requests
import json
from typing import Dict, List

def test_products_endpoint():
    """Test the new products endpoint with various filters"""
    
    base_url = "http://localhost:8000"
    
    print("=== Testing Products API Endpoint ===\n")
    
    # Test 1: Get all products
    print("1. Getting all products...")
    response = requests.get(f"{base_url}/products")
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Total products: {len(products)}")
        if products:
            print(f"  Sample product: {products[0]['name']} (ID: {products[0]['product_id']})")
    else:
        print(f"✗ Error: {response.status_code}")
    
    # Test 2: Filter by category
    print("\n2. Getting products by category (Meat)...")
    response = requests.get(f"{base_url}/products", params={"category": "Meat"})
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Meat products: {len(products)}")
        for i, product in enumerate(products[:3]):
            print(f"  - {product['name']} (Diet: {product['diet_type']}, Inventory: {product['inventory_quantity']})")
    
    # Test 3: Filter by diet type
    print("\n3. Getting vegan products...")
    response = requests.get(f"{base_url}/products", params={"diet_type": "vegan"})
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Vegan products: {len(products)}")
        categories = {}
        for product in products:
            categories[product['category']] = categories.get(product['category'], 0) + 1
        print("  Categories distribution:")
        for cat, count in sorted(categories.items()):
            print(f"    - {cat}: {count}")
    
    # Test 4: Products with discounts
    print("\n4. Getting products with at least 30% discount...")
    response = requests.get(f"{base_url}/products", params={"min_discount": 30})
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Discounted products: {len(products)}")
        if products:
            avg_discount = sum(p['current_discount_percent'] for p in products) / len(products)
            print(f"  Average discount: {avg_discount:.1f}%")
    
    # Test 5: Products expiring soon
    print("\n5. Getting products expiring in next 7 days...")
    response = requests.get(f"{base_url}/products", params={"max_days_until_expiry": 7})
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Products expiring soon: {len(products)}")
        if products:
            total_inventory = sum(p['inventory_quantity'] for p in products)
            print(f"  Total inventory at risk: {total_inventory} units")
    
    # Test 6: Combined filters
    print("\n6. Getting vegan products with discount expiring in 14 days...")
    params = {
        "diet_type": "vegan",
        "min_discount": 20,
        "max_days_until_expiry": 14
    }
    response = requests.get(f"{base_url}/products", params=params)
    if response.status_code == 200:
        products = response.json()
        print(f"✓ Matching products: {len(products)}")
    
    # Test 7: Product analysis
    print("\n7. Product inventory analysis...")
    response = requests.get(f"{base_url}/products")
    if response.status_code == 200:
        products = response.json()
        inventories = [p['inventory_quantity'] for p in products]
        print(f"  Min inventory: {min(inventories)} units")
        print(f"  Max inventory: {max(inventories)} units")
        print(f"  Avg inventory: {sum(inventories) / len(inventories):.1f} units")
        
        # Products with high inventory
        high_inventory = [p for p in products if p['inventory_quantity'] > 250]
        print(f"  Products with > 250 units: {len(high_inventory)}")
    
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    try:
        test_products_endpoint()
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}") 