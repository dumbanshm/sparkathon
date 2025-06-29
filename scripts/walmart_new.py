from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta

fake = Faker()

# Constants
NUM_USERS = 200
NUM_PRODUCTS = 300
NUM_TRANSACTIONS = 1000
DIET_TYPES = ['non-vegetarian', 'eggs', 'vegetarian', 'vegan']
CATEGORIES = ['Snacks', 'Dairy', 'Meat', 'Beverages', 'Spreads', 'Biscuits', 'Sauces', 'Cheese']
ALLERGENS = ['nuts', 'gluten', 'dairy', 'soy', 'eggs']

# Diet hierarchy
DIET_HIERARCHY = {
    "non-vegetarian": 3,
    "eggs": 2,
    "vegetarian": 1,
    "vegan": 0
}

def is_diet_compatible(user_diet, product_diet):
    return DIET_HIERARCHY[product_diet] <= DIET_HIERARCHY[user_diet]

def is_allergen_safe(user_allergies, product_allergens):
    return not any(a in product_allergens for a in user_allergies)

# USERS
users = []
for i in range(NUM_USERS):
    uid = f"U{i:04d}"
    age = random.randint(18, 65)
    diet_type = random.choice(DIET_TYPES)
    allergies = random.sample(ALLERGENS, random.randint(0, 2))
    prefers_discount = fake.boolean(chance_of_getting_true=70)
    gender = random.choice(['Male', 'Female', 'Other'])
    preferred_categories = random.sample(CATEGORIES, random.randint(1, 3))
    users.append({
        "user_id": uid,
        "age": age,
        "gender": gender,
        "diet_type": diet_type,
        "allergies": allergies,
        "prefers_discount": prefers_discount,
        "location_lat": fake.latitude(),
        "location_lon": fake.longitude(),
        "preferred_categories": preferred_categories,
        "last_purchase_date": fake.date_between(start_date='-60d', end_date='today')
    })

users_df = pd.DataFrame(users)

# PRODUCTS
products = []
for i in range(NUM_PRODUCTS):
    pid = f"P{i:04d}"
    category = random.choice(CATEGORIES)
    diet_type = random.choice(DIET_TYPES)
    allergens = random.sample(ALLERGENS, random.randint(0, 2))
    packaging_date = fake.date_between(start_date='-60d', end_date='-5d')
    shelf_life_days = random.randint(30, 180)
    expiry_date = pd.to_datetime(packaging_date) + timedelta(days=shelf_life_days)
    price_mrp = round(random.uniform(50, 500), 2)
    current_discount_percent = random.choice([0, 10, 20, 30, 40, 50])
    products.append({
        "product_id": pid,
        "name": f"{fake.word().capitalize()} {category}",
        "category": category,
        "brand": fake.company(),
        "diet_type": diet_type,
        "allergens": allergens,
        "shelf_life_days": shelf_life_days,
        "packaging_date": packaging_date,
        "expiry_date": expiry_date.date(),
        "weight_grams": random.choice([250, 500, 750, 1000]),
        "price_mrp": price_mrp,
        "current_discount_percent": current_discount_percent,
        "store_location_lat": fake.latitude(),
        "store_location_lon": fake.longitude()
    })

products_df = pd.DataFrame(products)

# TRANSACTIONS
transactions = []
for _ in range(NUM_TRANSACTIONS):
    attempts = 0
    while True:
        user = random.choice(users)
        product = random.choice(products)

        if not is_diet_compatible(user["diet_type"], product["diet_type"]):
            continue
        if not is_allergen_safe(user["allergies"], product["allergens"]):
            continue

        prefers_discount = user["prefers_discount"]
        discount = product["current_discount_percent"]
        if not prefers_discount and discount > 0:
            continue

        break  # valid user-product match

    purchase_date = fake.date_between(start_date='-30d', end_date='today')
    quantity = random.randint(1, 3)
    price_paid = round(product['price_mrp'] * (1 - discount / 100), 2)
    total_price_paid = round(quantity * price_paid, 2)
    expiry = pd.to_datetime(product['expiry_date'])
    purchase = pd.to_datetime(purchase_date)
    days_to_expiry = max((expiry - purchase).days, 0)

    transactions.append({
        "user_id": user["user_id"],
        "product_id": product["product_id"],
        "purchase_date": purchase_date,
        "quantity": quantity,
        "price_paid_per_unit": price_paid,
        "total_price_paid": total_price_paid,
        "discount_percent": discount,
        "product_diet_type": product["diet_type"],
        "user_diet_type": user["diet_type"],
        "days_to_expiry_at_purchase": days_to_expiry,
        "user_engaged_with_deal": random.choices([1, 0], weights=[70, 30])[0]
    })

transactions_df = pd.DataFrame(transactions)

# SAVE
users_df.to_csv("fake_users.csv", index=False)
products_df.to_csv("fake_products.csv", index=False)
transactions_df.to_csv("fake_transactions.csv", index=False)