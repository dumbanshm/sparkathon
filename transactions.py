from faker import Faker
import pandas as pd
import random
from datetime import datetime

fake = Faker()

#Assuming products_df and users_df are already loaded from previous code
products_df = pd.read_csv('/Users/devansh/Devansh/DevDaddy/sparkathon/products.csv')
users_df = pd.read_csv('/Users/devansh/Devansh/DevDaddy/sparkathon/users.csv')

products_df['expiry_date'] = pd.to_datetime(products_df['expiry_date']).dt.date
products_df['packaging_date'] = pd.to_datetime(products_df['packaging_date']).dt.date

num_transactions = 8000
transaction_data = []

for _ in range(num_transactions):
    # Pick a random user
    user = users_df.sample(1).iloc[0]
    user_diet = user['diet_type']

    # Filter products that match or are below the user's diet type
    if user_diet == 'green':
        allowed_products = products_df[products_df['diet_type'] == 'green']
    elif user_diet == 'yellow':
        allowed_products = products_df[products_df['diet_type'].isin(['green', 'yellow'])]
    else:
        allowed_products = products_df  # red can buy anything

    if allowed_products.empty:
        continue  # skip if no match

    product = allowed_products.sample(1).iloc[0]

    purchase_date = fake.date_between(
        start_date=product['packaging_date'],
        end_date=min(product['expiry_date'], datetime.today().date())
    )

    quantity = random.randint(1, 3)
    discount = product['current_discount_percent']
    mrp = product['price_mrp']
    price_paid = round(mrp * (1 - discount / 100), 2)

    transaction_data.append({
        'user_id': user['user_id'],
        'product_id': product['product_id'],
        'purchase_date': purchase_date,
        'quantity': quantity,
        'price_paid_per_unit': price_paid,
        'total_price_paid': round(price_paid * quantity, 2),
        'discount_percent': discount,
        'product_diet_type': product['diet_type'],
        'user_diet_type': user_diet
    })

transactions_df = pd.DataFrame(transaction_data)
print(transactions_df.head()) 
transactions_df.to_csv('transactions.csv', index=False)
