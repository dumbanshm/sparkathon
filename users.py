from faker import Faker
import pandas as pd
import random

fake = Faker()
num_users = 300

user_data = []
for i in range(num_users):
    uid = f"U{i:04d}"
    gender = random.choice(['Male', 'Female', 'Other'])
    age = random.randint(18, 70)
    diet_type = random.choices(['green', 'yellow', 'red'], weights=[0.4, 0.2, 0.4], k=1)[0]

    user_data.append({
        'user_id': uid,
        'name': fake.name_male() if gender == 'Male' else fake.name_female() if gender == 'Female' else fake.name(),
        'gender': gender,
        'age': age,
        'diet_type': diet_type,
        'allergies': random.choice([[], ['nuts'], ['dairy'], ['gluten']]),
        'prefers_discount': random.choice([True, False]),
        'diet_tags': random.choice([[], ['vegan'], ['gluten-free'], ['low-carb']]),
        'location_lat': fake.latitude(),
        'location_lon': fake.longitude()
    })

users_df = pd.DataFrame(user_data)
# users_df.to_csv('users.csv', index=False)
print(users_df.head())  # show first 5 rows
users_df.to_csv("users.csv", index=False)
