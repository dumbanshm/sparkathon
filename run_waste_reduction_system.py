import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import the unified system
from unified_waste_reduction_system import (
    UnifiedRecommendationSystem,
    DynamicThresholdCalculator,
    calculate_dead_stock_risk_dynamic
)

def load_datasets():
    """Load all required datasets"""
    print("Loading datasets...")
    try:
        users_df = pd.read_csv('datasets/fake_users.csv')
        products_df = pd.read_csv('datasets/fake_products.csv')
        transactions_df = pd.read_csv('datasets/fake_transactions.csv')
        
        # Convert date columns to datetime
        date_columns = {
            'products_df': ['packaging_date', 'expiry_date'],
            'transactions_df': ['purchase_date']
        }
        
        for col in date_columns['products_df']:
            if col in products_df.columns:
                products_df[col] = pd.to_datetime(products_df[col])
        
        for col in date_columns['transactions_df']:
            if col in transactions_df.columns:
                transactions_df[col] = pd.to_datetime(transactions_df[col])
        
        print(f"✓ Loaded {len(users_df)} users")
        print(f"✓ Loaded {len(products_df)} products")
        print(f"✓ Loaded {len(transactions_df)} transactions")
        
        return users_df, products_df, transactions_df
    
    except Exception as e:
        print(f"Error loading datasets: {e}")
        return None, None, None

def analyze_data(users_df, products_df, transactions_df):
    """Basic data analysis"""
    print("\n" + "="*50)
    print("DATA ANALYSIS")
    print("="*50)
    
    # User analysis
    print("\nUser Demographics:")
    print(f"- Total users: {len(users_df)}")
    print(f"- Diet types: {users_df['diet_type'].value_counts().to_dict()}")
    
    # Product analysis
    print("\nProduct Categories:")
    print(products_df['category'].value_counts())
    
    current_date = pd.Timestamp.now()
    products_df['days_until_expiry'] = (products_df['expiry_date'] - current_date).dt.days
    
    print(f"\nExpiry Status:")
    print(f"- Expired products: {(products_df['days_until_expiry'] <= 0).sum()}")
    print(f"- Expiring in 7 days: {((products_df['days_until_expiry'] > 0) & (products_df['days_until_expiry'] <= 7)).sum()}")
    print(f"- Expiring in 30 days: {((products_df['days_until_expiry'] > 0) & (products_df['days_until_expiry'] <= 30)).sum()}")
    
    # Transaction analysis
    print(f"\nTransaction Summary:")
    print(f"- Total transactions: {len(transactions_df)}")
    print(f"- Unique users who made purchases: {transactions_df['user_id'].nunique()}")
    print(f"- Average discount given: {transactions_df['discount_percent'].mean():.2f}%")
    print(f"- Deal engagement rate: {transactions_df['user_engaged_with_deal'].mean():.2%}")

def calculate_dead_stock_analysis(products_df, transactions_df, threshold_calculator):
    """Analyze dead stock risk using dynamic thresholds"""
    print("\n" + "="*50)
    print("DEAD STOCK RISK ANALYSIS")
    print("="*50)
    
    # Calculate sales velocity for each product
    current_date = pd.Timestamp.now()
    products_df['days_until_expiry'] = (products_df['expiry_date'] - current_date).dt.days
    
    sales_velocity = transactions_df.groupby('product_id').agg({
        'quantity': 'sum',
        'purchase_date': ['min', 'max']
    }).reset_index()
    
    sales_velocity.columns = ['product_id', 'total_sold', 'first_sale', 'last_sale']
    sales_velocity['days_on_market'] = (sales_velocity['last_sale'] - sales_velocity['first_sale']).dt.days + 1
    sales_velocity['sales_velocity'] = sales_velocity['total_sold'] / sales_velocity['days_on_market']
    
    # Merge with products
    products_enhanced = products_df.merge(sales_velocity[['product_id', 'sales_velocity']], 
                                         on='product_id', how='left')
    products_enhanced['sales_velocity'].fillna(0, inplace=True)
    
    # Calculate dead stock risk
    products_enhanced['is_dead_stock_risk'] = products_enhanced.apply(
        lambda row: calculate_dead_stock_risk_dynamic(row, threshold_calculator), axis=1
    )
    
    # Get thresholds for all products
    threshold_df = threshold_calculator.calculate_all_thresholds()
    
    # Analysis
    at_risk_products = products_enhanced[products_enhanced['is_dead_stock_risk'] == 1]
    print(f"\nTotal products at risk: {len(at_risk_products)} ({len(at_risk_products)/len(products_enhanced)*100:.1f}%)")
    
    print("\nRisk by Category:")
    risk_by_category = at_risk_products.groupby('category').size()
    for category, count in risk_by_category.items():
        total_in_category = (products_enhanced['category'] == category).sum()
        print(f"- {category}: {count}/{total_in_category} ({count/total_in_category*100:.1f}%)")
    
    print("\nTop 10 Products at Risk (with lowest days until expiry):")
    top_risk = at_risk_products.nsmallest(10, 'days_until_expiry')[
        ['product_id', 'name', 'category', 'days_until_expiry', 'current_discount_percent']
    ]
    for idx, row in top_risk.iterrows():
        threshold = threshold_calculator.get_threshold(row['product_id'])
        print(f"- {row['name']} ({row['category']}): {row['days_until_expiry']} days left, "
              f"threshold: {threshold} days, current discount: {row['current_discount_percent']}%")
    
    return products_enhanced

def demonstrate_recommendations(system, users_df):
    """Demonstrate different types of recommendations"""
    print("\n" + "="*50)
    print("RECOMMENDATION DEMONSTRATIONS")
    print("="*50)
    
    # Select a few users for demonstration
    demo_users = users_df.sample(min(3, len(users_df)))
    
    for _, user in demo_users.iterrows():
        print(f"\n{'='*30}")
        print(f"Recommendations for User: {user['user_id']}")
        print(f"Diet: {user['diet_type']}, Allergies: {user['allergies']}")
        print(f"{'='*30}")
        
        # Hybrid recommendations
        print("\n1. HYBRID RECOMMENDATIONS (Best Overall):")
        hybrid_recs = system.get_hybrid_recommendations(
            user['user_id'], 
            n_recommendations=5,
            content_weight=0.4,
            collaborative_weight=0.6
        )
        
        if not hybrid_recs.empty:
            for idx, rec in hybrid_recs.iterrows():
                print(f"   - {rec['product_name']} ({rec['category']})")
                print(f"     Score: {rec['hybrid_score']:.3f}, Days until expiry: {rec['days_until_expiry']}, "
                      f"Price: ₹{rec['price']}, Discount: {rec['discount']}%")
                if rec.get('is_dead_stock_risk', 0) == 1:
                    print(f"     ⚠️  AT RISK OF BECOMING DEAD STOCK")
        else:
            print("   No recommendations available")
        
        # Get user's purchase history
        user_products = system.transactions_df[
            system.transactions_df['user_id'] == user['user_id']
        ]['product_id'].unique()
        
        if len(user_products) > 0:
            # Content-based recommendations
            print("\n2. CONTENT-BASED RECOMMENDATIONS (Similar to your purchases):")
            last_product = user_products[-1]
            product_name = system.products_df[
                system.products_df['product_id'] == last_product
            ]['name'].iloc[0]
            print(f"   Based on your purchase of: {product_name}")
            
            content_recs = system.get_content_based_recommendations(
                last_product,
                n_recommendations=3,
                urgency_boost=True
            )
            
            for idx, rec in content_recs.iterrows():
                print(f"   - {rec['product_name']} ({rec['category']})")
                print(f"     Similarity: {rec['similarity_score']:.3f}, Days until expiry: {rec['days_until_expiry']}")

def demonstrate_waste_reduction_strategies(products_enhanced, threshold_calculator):
    """Show waste reduction strategies"""
    print("\n" + "="*50)
    print("WASTE REDUCTION STRATEGIES")
    print("="*50)
    
    # Products needing immediate action
    urgent_products = products_enhanced[
        (products_enhanced['days_until_expiry'] > 0) & 
        (products_enhanced['days_until_expiry'] <= 7) &
        (products_enhanced['is_dead_stock_risk'] == 1)
    ].sort_values('days_until_expiry')
    
    print(f"\n1. URGENT ACTION REQUIRED ({len(urgent_products)} products):")
    for idx, product in urgent_products.head(5).iterrows():
        threshold = threshold_calculator.get_threshold(product['product_id'])
        suggested_discount = min(50, product['current_discount_percent'] + 20)
        print(f"\n   Product: {product['name']}")
        print(f"   - Days until expiry: {product['days_until_expiry']}")
        print(f"   - Current discount: {product['current_discount_percent']}%")
        print(f"   - Suggested discount: {suggested_discount}%")
        print(f"   - Dynamic threshold: {threshold} days")
    
    # Category-wise recommendations
    print("\n2. CATEGORY-WISE OPTIMIZATION:")
    category_thresholds = threshold_calculator.category_thresholds
    for category, threshold in sorted(category_thresholds.items(), key=lambda x: x[1]):
        category_products = products_enhanced[products_enhanced['category'] == category]
        at_risk = category_products[category_products['is_dead_stock_risk'] == 1]
        print(f"\n   {category}:")
        print(f"   - Base threshold: {threshold} days")
        print(f"   - Products at risk: {len(at_risk)}/{len(category_products)}")
        print(f"   - Avg days to expiry for at-risk: {at_risk['days_until_expiry'].mean():.1f}")

def main():
    """Main driver function"""
    print("="*50)
    print("UNIFIED WASTE REDUCTION SYSTEM")
    print("="*50)
    
    # Load datasets
    users_df, products_df, transactions_df = load_datasets()
    if users_df is None:
        print("Failed to load datasets. Exiting.")
        return
    
    # Basic data analysis
    analyze_data(users_df, products_df, transactions_df)
    
    # Initialize the unified recommendation system
    print("\nInitializing Unified Recommendation System...")
    system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
    
    # Preprocess data
    system.preprocess_data()
    
    # Build models
    print("Building content similarity matrix...")
    system.build_content_similarity_matrix()
    
    print("Building collaborative filtering model...")
    system.build_collaborative_filtering_model(n_factors=50)
    
    # Dead stock analysis
    products_enhanced = calculate_dead_stock_analysis(
        products_df, transactions_df, system.threshold_calculator
    )
    
    # Update products_df in system with enhanced data
    system.products_df = products_enhanced
    
    # Demonstrate recommendations
    demonstrate_recommendations(system, users_df)
    
    # Show waste reduction strategies
    demonstrate_waste_reduction_strategies(products_enhanced, system.threshold_calculator)
    
    print("\n" + "="*50)
    print("SYSTEM READY FOR USE")
    print("="*50)
    print("\nThe unified waste reduction system is now initialized and ready.")
    print("You can use the 'system' object to generate recommendations for any user.")
    print("\nExample usage:")
    print("  recommendations = system.get_hybrid_recommendations('U0001', n_recommendations=10)")
    
    return system, products_enhanced

if __name__ == "__main__":
    system, products_enhanced = main() 