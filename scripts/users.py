from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta

fake = Faker()
num_users = 300

# Categories that match your products
categories = ['Dairy', 'Vegetables', 'Fruits', 'Meat', 'Grains', 'Snacks', 'Beverages']
common_allergens = ['nuts', 'dairy', 'gluten', 'soy', 'eggs', 'shellfish']

user_data = []
for i in range(num_users):
    uid = f"U{i:04d}"
    gender = random.choice(['Male', 'Female', 'Other'])
    age = random.randint(18, 70)
    
    # Use diet types that match your frontend expectations
    diet_type = random.choices(['vegetarian', 'eggitarian', 'non-vegetarian'], 
                              weights=[0.4, 0.2, 0.4], k=1)[0]
    
    # Generate allergies (some users have none)
    user_allergies = []
    if random.random() < 0.3:  # 30% of users have allergies
        num_allergies = random.randint(1, 2)
        user_allergies = random.sample(common_allergens, num_allergies)
    
    # Generate preferred categories (users typically prefer 2-4 categories)
    num_preferred = random.randint(2, 4)
    preferred_categories = random.sample(categories, num_preferred)
    
    # Last purchase date (within last 6 months)
    last_purchase = fake.date_between(start_date='-180d', end_date='today')

    user_data.append({
        'user_id': uid,
        'name': fake.name_male() if gender == 'Male' else fake.name_female() if gender == 'Female' else fake.name(),
        'age': age,
        'gender': gender,
        'diet_type': diet_type,
        'allergies': ','.join(user_allergies) if user_allergies else '',
        'prefers_discount': random.choice([True, False]),
        'location_lat': fake.latitude(),
        'location_lon': fake.longitude(),
        'preferred_categories': ','.join(preferred_categories),
        'last_purchase_date': last_purchase
    })

users_df = pd.DataFrame(user_data)
print(f"Generated {len(users_df)} users")
print(f"Diet types: {users_df['diet_type'].value_counts().to_dict()}")
print(f"Users with allergies: {len(users_df[users_df['allergies'] != ''])}")
print(users_df.head())
users_df.to_csv("users.csv", index=False)