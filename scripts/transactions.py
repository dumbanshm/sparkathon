from faker import Faker
import pandas as pd
import random
from datetime import datetime

fake = Faker()

# Load the corrected CSV files
products_df = pd.read_csv('products.csv')
users_df = pd.read_csv('users.csv')

# Convert date columns
products_df['expiry_date'] = pd.to_datetime(products_df['expiry_date']).dt.date
products_df['packaging_date'] = pd.to_datetime(products_df['packaging_date']).dt.date
users_df['last_purchase_date'] = pd.to_datetime(users_df['last_purchase_date']).dt.date

num_transactions = 8000
transaction_data = []

for _ in range(num_transactions):
    # Pick a random user
    user = users_df.sample(1).iloc[0]
    user_diet = user['diet_type']
    user_allergies = user['allergies'].split(',') if user['allergies'] else []
    
    # Filter products based on user's diet type and allergies
    allowed_products = products_df.copy()
    
    # Diet type filtering
    if user_diet == 'vegetarian':
        allowed_products = allowed_products[allowed_products['diet_type'] == 'vegetarian']
    elif user_diet == 'eggitarian':
        allowed_products = allowed_products[allowed_products['diet_type'].isin(['vegetarian', 'eggitarian'])]
    # non-vegetarian users can buy anything
    
    # Allergy filtering - exclude products with user's allergens
    for allergy in user_allergies:
        if allergy:  # Check if allergy is not empty
            allowed_products = allowed_products[~allowed_products['allergens'].str.contains(allergy, na=False)]
    
    if allowed_products.empty:
        continue  # skip if no matching products
    
    # Users are more likely to buy discounted products if they prefer discounts
    if user['prefers_discount']:
        discounted_products = allowed_products[allowed_products['current_discount_percent'] > 0]
        if not discounted_products.empty and random.random() < 0.7:  # 70% chance to pick discounted
            product = discounted_products.sample(1).iloc[0]
        else:
            product = allowed_products.sample(1).iloc[0]
    else:
        product = allowed_products.sample(1).iloc[0]
    
    # Generate purchase date (between packaging and expiry, but not future)
    max_purchase_date = min(product['expiry_date'], datetime.today().date())
    purchase_date = fake.date_between(
        start_date=product['packaging_date'],
        end_date=max_purchase_date
    )
    
    # Calculate days to expiry at time of purchase
    days_to_expiry_at_purchase = (product['expiry_date'] - purchase_date).days
    
    quantity = random.randint(1, 3)
    discount = product['current_discount_percent']
    mrp = product['price_mrp']
    price_paid = round(mrp * (1 - discount / 100), 2)
    
    # User engagement with deal (higher for discount-preferring users and good deals)
    user_engaged_with_deal = 0
    if discount > 0:
        engagement_prob = 0.3
        if user['prefers_discount']:
            engagement_prob += 0.4
        if discount >= 30:
            engagement_prob += 0.2
        user_engaged_with_deal = 1 if random.random() < engagement_prob else 0

    transaction_data.append({
        'user_id': user['user_id'],
        'product_id': product['product_id'],
        'purchase_date': purchase_date,
        'quantity': quantity,
        'price_paid_per_unit': price_paid,
        'total_price_paid': round(price_paid * quantity, 2),
        'discount_percent': discount,
        'product_diet_type': product['diet_type'],
        'user_diet_type': user_diet,
        'days_to_expiry_at_purchase': days_to_expiry_at_purchase,
        'user_engaged_with_deal': user_engaged_with_deal
    })

transactions_df = pd.DataFrame(transaction_data)
print(f"Generated {len(transactions_df)} transactions")
print(f"Transactions with discounts: {len(transactions_df[transactions_df['discount_percent'] > 0])}")
print(f"User engagement with deals: {transactions_df['user_engaged_with_deal'].sum()}")
print(transactions_df.head())
transactions_df.to_csv('transactions.csv', index=False)