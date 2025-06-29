from faker import Faker
import pandas as pd
import random
from datetime import timedelta

fake = Faker()
num_products = 500

product_data = []
for i in range(num_products):
    pid = f"P{i:04d}"
    shelf_life = random.randint(7, 140)  # 1 to 20 weeks
    packaging_date = fake.date_between(start_date='-60d', end_date='today')
    expiry_date = packaging_date + timedelta(days=shelf_life)

    diet_type = random.choices(['green', 'yellow', 'red'], weights=[0.4, 0.2, 0.4], k=1)[0]

    product_data.append({
        'product_id': pid,
        'name': fake.word().capitalize() + " " + fake.word(),
        'category': random.choice(['Biscuits', 'Cheese', 'Spreads', 'Mayonnaise', 'Snacks', 'Sauces']),
        'diet_type': diet_type,
        'shelf_life_days': shelf_life,
        'packaging_date': packaging_date,
        'expiry_date': expiry_date,
        'weight_grams': random.choice([250, 500, 750, 1000]),
        'price_mrp': round(random.uniform(50, 500), 2),
        'current_discount_percent': random.choice([0, 10, 20, 30, 40, 50]),
        'store_location_lat': fake.latitude(),
        'store_location_lon': fake.longitude()
    })

products_df = pd.DataFrame(product_data)
# products_df.to_csv('products.csv', index=False)
print(products_df.head())  # show first 5 rows
products_df.to_csv("products.csv", index=False)
