from faker import Faker
import pandas as pd
import random
from datetime import timedelta, datetime

fake = Faker()
num_products = 500

# Define categories that match your frontend
categories = ['Dairy', 'Vegetables', 'Fruits', 'Meat', 'Grains', 'Snacks', 'Beverages']

# Define brands for each category
brands_by_category = {
    'Dairy': ['Amul', 'Mother Dairy', 'Nestle', 'Britannia'],
    'Vegetables': ['Fresh Farm', 'Green Valley', 'Organic Plus', 'Nature Fresh'],
    'Fruits': ['Sweet Harvest', 'Garden Fresh', 'Tropical Delight', 'Pure Fruit'],
    'Meat': ['Fresh Cuts', 'Premium Meats', 'Farm Fresh', 'Quality Cuts'],
    'Grains': ['Golden Harvest', 'Farm Pride', 'Healthy Grains', 'Nature Mills'],
    'Snacks': ['Lay\'s', 'Haldiram\'s', 'Bikano', 'Kurkure'],
    'Beverages': ['Coca Cola', 'Pepsi', 'Tropicana', 'Real']
}

# Define allergens
common_allergens = ['nuts', 'dairy', 'gluten', 'soy', 'eggs', 'shellfish']

product_data = []
for i in range(num_products):
    pid = f"P{i:04d}"
    category = random.choice(categories)
    brand = random.choice(brands_by_category[category])
    
    # Generate appropriate shelf life based on category
    if category in ['Dairy', 'Meat', 'Vegetables', 'Fruits']:
        shelf_life = random.randint(3, 14)  # Perishable items: 3-14 days
    elif category in ['Beverages']:
        shelf_life = random.randint(30, 365)  # Beverages: 1 month to 1 year
    else:  # Grains, Snacks
        shelf_life = random.randint(60, 730)  # Non-perishable: 2 months to 2 years
    
    packaging_date = fake.date_between(start_date='-60d', end_date='today')
    expiry_date = packaging_date + timedelta(days=shelf_life)
    
    # Calculate days until expiry
    days_until_expiry = (expiry_date - datetime.today().date()).days
    
    # Set diet type based on category
    if category == 'Meat':
        diet_type = 'non-vegetarian'
    elif category in ['Dairy']:
        diet_type = random.choice(['vegetarian', 'eggitarian'])
    else:
        diet_type = 'vegetarian'
    
    # Generate allergens based on category
    category_allergens = []
    if category == 'Dairy':
        category_allergens.append('dairy')
    if category == 'Grains':
        if random.random() < 0.3:  # 30% chance of gluten
            category_allergens.append('gluten')
    if category == 'Snacks':
        if random.random() < 0.4:  # 40% chance of nuts
            category_allergens.append('nuts')
    
    # Add random additional allergens
    if random.random() < 0.2:  # 20% chance of additional allergen
        additional_allergen = random.choice([a for a in common_allergens if a not in category_allergens])
        category_allergens.append(additional_allergen)
    
    # Determine if product is at risk (expires in next 7 days and low discount)
    is_dead_stock_risk = 0
    if days_until_expiry <= 7:
        is_dead_stock_risk = 1
    
    # Generate price_mrp first
    price_mrp = round(random.uniform(20, 500), 2)
    
    # Higher discount for items close to expiry
    if days_until_expiry <= 3:
        current_discount = random.choice([30, 40, 50, 60])
    elif days_until_expiry <= 7:
        current_discount = random.choice([20, 30, 40])
    else:
        current_discount = random.choice([0, 0, 0, 10, 15, 20])  # Most items have no discount
    
    # Calculate cost price (40-45% of MRP)
    cost_price_percentage = random.uniform(0.40, 0.45)
    cost_price = round(price_mrp * cost_price_percentage, 2)
    
    # Calculate total cost (initial inventory * cost price)
    total_cost = round(inventory_quantity * cost_price, 2)

    product_data.append({
        'product_id': pid,
        'name': f"{brand} {fake.word().capitalize()} {category[:-1] if category.endswith('s') else category}",
        'category': category,
        'brand': brand,
        'diet_type': diet_type,
        'allergens': ','.join(category_allergens) if category_allergens else '',
        'shelf_life_days': shelf_life,
        'packaging_date': packaging_date,
        'expiry_date': expiry_date,
        'days_until_expiry': days_until_expiry,
        'weight_grams': random.choice([100, 250, 500, 750, 1000, 1500, 2000]),
        'price_mrp': price_mrp,
        'cost_price': cost_price,
        'current_discount_percent': current_discount,
        'inventory_quantity': inventory_quantity,
        'initial_inventory_quantity': inventory_quantity,  # Same as inventory for new products
        'total_cost': total_cost,
        'revenue_generated': 0.0,  # Initialize to 0
        'is_dead_stock_risk': is_dead_stock_risk,
        'store_location_lat': fake.latitude(),
        'store_location_lon': fake.longitude()
    })

products_df = pd.DataFrame(product_data)
print(f"Generated {len(products_df)} products")
print(f"Categories: {products_df['category'].value_counts().to_dict()}")
print(f"At-risk products: {products_df['is_dead_stock_risk'].sum()}")
print(products_df.head())

import os
os.makedirs("../datasets", exist_ok=True)
products_df.to_csv("../datasets/products.csv", index=False)
print("File saved to ../datasets/products.csv")