import pandas as pd
from unified_waste_reduction_system import UnifiedRecommendationSystem

# Load data
users_df = pd.read_csv('datasets/fake_users.csv')
products_df = pd.read_csv('datasets/fake_products.csv')
transactions_df = pd.read_csv('datasets/fake_transactions.csv')

# Convert dates
products_df['expiry_date'] = pd.to_datetime(products_df['expiry_date'])
transactions_df['purchase_date'] = pd.to_datetime(transactions_df['purchase_date'])

# Initialize system
system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
system.build_content_similarity_matrix()
system.build_collaborative_filtering_model()

# Test 1: User with no purchase history
users_no_history = set(users_df['user_id']) - set(transactions_df['user_id'].unique())
if users_no_history:
    test_user = list(users_no_history)[0]
    user_info = users_df[users_df['user_id'] == test_user].iloc[0]
    print(f"Test 1: User {test_user} with no purchase history")
    print(f"Diet: {user_info['diet_type']}, Allergies: {user_info['allergies']}")
    
    try:
        recs = system.get_hybrid_recommendations(test_user, n_recommendations=5)
        print(f"Got {len(recs)} recommendations")
        print("Columns:", list(recs.columns))
        if not recs.empty:
            print("\nFirst recommendation:")
            print(recs.iloc[0].to_dict())
        print("✅ Test 1 PASSED\n")
    except Exception as e:
        print(f"❌ Test 1 FAILED: {e}\n")

# Test 2: Vegan user
vegan_users = users_df[users_df['diet_type'] == 'vegan']
if not vegan_users.empty:
    test_user = vegan_users.iloc[0]['user_id']
    print(f"Test 2: Vegan user {test_user}")
    
    try:
        recs = system.get_hybrid_recommendations(test_user, n_recommendations=5)
        print(f"Got {len(recs)} recommendations")
        # Check if all recommendations are vegan-friendly
        all_vegan = True
        for _, rec in recs.iterrows():
            product = products_df[products_df['product_id'] == rec['product_id']].iloc[0]
            if product['diet_type'] not in ['vegan']:
                all_vegan = False
                print(f"❌ Non-vegan product recommended: {product['name']} ({product['diet_type']})")
        
        if all_vegan:
            print("✅ Test 2 PASSED - All recommendations are vegan-friendly\n")
        else:
            print("❌ Test 2 FAILED - Non-vegan products recommended\n")
    except Exception as e:
        print(f"❌ Test 2 FAILED: {e}\n")

print("Testing complete!") 