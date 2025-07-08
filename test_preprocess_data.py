import pandas as pd
import numpy as np
from unified_waste_reduction_system import UnifiedRecommendationSystem
import sys

def test_preprocess_data():
    """Test the preprocess_data method with the actual data files"""
    try:
        # Load the datasets
        print("Loading datasets...")
        users_df = pd.read_csv('datasets/fake_users.csv')
        products_df = pd.read_csv('datasets/fake_products.csv')
        transactions_df = pd.read_csv('datasets/fake_transactions.csv')
        
        print(f"✓ Users loaded: {len(users_df)} records")
        print(f"✓ Products loaded: {len(products_df)} records")
        print(f"✓ Transactions loaded: {len(transactions_df)} records")
        
        # Create the recommendation system instance
        print("\nInitializing UnifiedRecommendationSystem...")
        system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
        print("✓ System initialized successfully")
        
        # Check if preprocess_data added the expected columns
        expected_columns = [
            'days_until_expiry',
            'total_shelf_life', 
            'shelf_life_remaining_pct',
            'total_quantity_sold',
            'avg_quantity_per_sale',
            'number_of_sales',
            'days_since_last_sale',
            'sales_velocity',
            'is_dead_stock_risk'
        ]
        
        print("\nChecking for expected columns after preprocessing:")
        missing_columns = []
        for col in expected_columns:
            if col in system.products_df.columns:
                print(f"✓ {col} - present")
            else:
                print(f"✗ {col} - MISSING")
                missing_columns.append(col)
        
        if missing_columns:
            print(f"\nERROR: Missing columns: {missing_columns}")
            return False
            
        # Display sample of processed data
        print("\nSample of processed products data:")
        sample_cols = ['product_id', 'name', 'days_until_expiry', 'sales_velocity', 'is_dead_stock_risk']
        print(system.products_df[sample_cols].head())
        
        # Check data types
        print("\nData types of new columns:")
        for col in expected_columns:
            print(f"{col}: {system.products_df[col].dtype}")
        
        # Statistics
        print("\nStatistics:")
        print(f"Products at dead stock risk: {system.products_df['is_dead_stock_risk'].sum()}")
        print(f"Average days until expiry: {system.products_df['days_until_expiry'].mean():.1f}")
        print(f"Products with no sales: {(system.products_df['number_of_sales'] == 0).sum()}")
        
        print("\n✅ All tests passed! The preprocess_data method is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Error occurred: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_preprocess_data()
    sys.exit(0 if success else 1) 