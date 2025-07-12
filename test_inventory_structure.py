import pandas as pd
from unified_waste_reduction_system import UnifiedRecommendationSystem, DynamicThresholdCalculator

# Load the new data
users_df = pd.read_csv('datasets/fake_users.csv')
products_df = pd.read_csv('datasets/fake_products.csv')
transactions_df = pd.read_csv('datasets/fake_transactions.csv')

print("=== Data Structure Verification ===")
print(f"\nProducts columns: {list(products_df.columns)}")
print(f"Has inventory_quantity in products: {'inventory_quantity' in products_df.columns}")
print(f"\nTransactions columns: {list(transactions_df.columns)}")
print(f"Has inventory_quantity in transactions: {'inventory_quantity' in transactions_df.columns}")

print("\n=== Sample Products with Inventory ===")
sample_products = products_df[['product_id', 'name', 'category', 'inventory_quantity']].head(5)
print(sample_products)

print("\n=== Testing Recommendation System ===")
# Initialize the recommendation system
threshold_calculator = DynamicThresholdCalculator(products_df, transactions_df)
recommender = UnifiedRecommendationSystem(users_df, products_df, transactions_df)

# Test with a vegan user
test_user = "U0000"
user = users_df[users_df['user_id'] == test_user].iloc[0]
print(f"\nTest user {test_user}:")
print(f"- Diet type: {user['diet_type']}")
print(f"- Allergies: {user['allergies']}")

# Get recommendations
recommendations = recommender.get_hybrid_recommendations(test_user, n_recommendations=3)
print(f"\nRecommendations for {test_user}:")
print(f"Columns in recommendations: {list(recommendations.columns)}")
for _, rec in recommendations.iterrows():
    product = products_df[products_df['product_id'] == rec['product_id']].iloc[0]
    print(f"- {product['name']} (Category: {product['category']}, Diet: {product['diet_type']}, Inventory: {product['inventory_quantity']})")

print("\n=== Testing Dead Stock Risk Calculation ===")
# Get products with dead stock risk from the processed dataframe
at_risk = recommender.products_df[recommender.products_df['is_dead_stock_risk'] == 1]
print(f"\nTotal products at risk: {len(at_risk)}")
if len(at_risk) > 0:
    print("\nSample at-risk products:")
    risk_sample = at_risk[['product_id', 'name', 'days_until_expiry', 'inventory_quantity', 'sales_velocity']].head(3)
    print(risk_sample)

print("\n✓ All tests completed successfully!") 