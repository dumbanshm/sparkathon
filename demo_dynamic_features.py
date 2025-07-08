import pandas as pd
import numpy as np
from unified_waste_reduction_system import UnifiedRecommendationSystem

# Load data
print("Loading data...")
users_df = pd.read_csv('datasets/fake_users.csv')
products_df = pd.read_csv('datasets/fake_products.csv')
transactions_df = pd.read_csv('datasets/fake_transactions.csv')

# Convert dates
products_df['expiry_date'] = pd.to_datetime(products_df['expiry_date'])
transactions_df['purchase_date'] = pd.to_datetime(transactions_df['purchase_date'])

# Initialize system
print("Initializing system...")
system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
system.build_content_similarity_matrix()
system.build_collaborative_filtering_model()

print("\n" + "="*70)
print("DYNAMIC URGENCY AND DISCOUNT DEMONSTRATION")
print("="*70)

# 1. Show dynamic pricing recommendations
print("\n1. DYNAMIC PRICING RECOMMENDATIONS")
print("-" * 70)
pricing_recs = system.get_dynamic_pricing_recommendations(min_urgency=0.3, limit=5)

if not pricing_recs.empty:
    for idx, rec in pricing_recs.iterrows():
        print(f"\nProduct: {rec['product_name']} ({rec['category']})")
        print(f"  Days until expiry: {rec['days_until_expiry']}")
        print(f"  Urgency Score: {rec['urgency_score']:.3f}")
        print(f"  Current → Recommended Discount: {rec['current_discount']}% → {rec['recommended_discount']}%")
        print(f"  Price Impact: ₹{rec['current_price']:.2f} → ₹{rec['recommended_price']:.2f}")
        print(f"  Reasoning: {rec['reasoning']}")

# 2. Compare recommendations with and without urgency
print("\n\n2. URGENCY IMPACT ON RECOMMENDATIONS")
print("-" * 70)

# Pick a user
test_user = users_df.iloc[0]['user_id']
print(f"User: {test_user}")

# Get recommendations
recs = system.get_hybrid_recommendations(test_user, n_recommendations=5)
print("\nTop 5 recommendations with dynamic urgency:")

for idx, rec in recs.iterrows():
    urgency_impact = (rec['hybrid_score'] - rec.get('base_score', rec['hybrid_score'])) / rec.get('base_score', 1) * 100
    print(f"\n  {idx+1}. {rec['product_name']}")
    print(f"     Base Score: {rec.get('base_score', rec['hybrid_score']):.3f}")
    print(f"     Urgency Score: {rec.get('urgency_score', 0):.3f}")
    print(f"     Final Score: {rec['hybrid_score']:.3f} (+{urgency_impact:.1f}% from urgency)")
    print(f"     Days to expiry: {rec['days_until_expiry']}")

# 3. Category urgency analysis
print("\n\n3. CATEGORY URGENCY ANALYSIS")
print("-" * 70)

category_urgency = {}
for category in products_df['category'].unique():
    cat_products = products_df[
        (products_df['category'] == category) & 
        (products_df['days_until_expiry'] > 0)
    ]
    
    if not cat_products.empty:
        urgency_scores = [
            system.pricing_engine.calculate_dynamic_urgency_score(row) 
            for _, row in cat_products.iterrows()
        ]
        category_urgency[category] = {
            'avg': np.mean(urgency_scores),
            'max': np.max(urgency_scores),
            'high_urgency': sum(1 for u in urgency_scores if u > 0.5)
        }

# Sort by average urgency
for cat, stats in sorted(category_urgency.items(), key=lambda x: x[1]['avg'], reverse=True)[:5]:
    print(f"\n{cat}:")
    print(f"  Avg Urgency: {stats['avg']:.3f}")
    print(f"  Max Urgency: {stats['max']:.3f}")
    print(f"  High Urgency Products: {stats['high_urgency']}")

print("\n" + "="*70)
print("Dynamic features are now active!")
print("- Urgency scores adapt based on category, sales velocity, and thresholds")
print("- Discount recommendations consider multiple factors")
print("- Dead stock items get higher priority automatically")
print("="*70) 