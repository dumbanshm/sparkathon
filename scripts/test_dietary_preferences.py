import pandas as pd
import sys

def test_dietary_preferences(csv_file):
    """Test that user dietary preferences are correctly aligned with preferred categories"""
    try:
        # Load the users data
        users_df = pd.read_csv(csv_file)
        print(f"\nTesting {csv_file}...")
        print(f"Total users: {len(users_df)}")
        
        # Check if preferred_categories column exists and handle both list and string formats
        if 'preferred_categories' not in users_df.columns:
            print("ERROR: preferred_categories column not found!")
            return
        
        violations = []
        
        for idx, user in users_df.iterrows():
            diet_type = user['diet_type']
            
            # Handle both list and comma-separated string formats
            if isinstance(user['preferred_categories'], str):
                preferred_cats = [cat.strip() for cat in user['preferred_categories'].split(',')]
            else:
                preferred_cats = user['preferred_categories']
            
            # Check for violations
            if diet_type == 'vegan':
                forbidden = ['Dairy', 'Cheese', 'Meat']
                for cat in preferred_cats:
                    if cat in forbidden:
                        violations.append(f"User {user['user_id']} (vegan) prefers {cat}")
            
            elif diet_type in ['vegetarian', 'eggs', 'eggitarian']:
                forbidden = ['Meat']
                for cat in preferred_cats:
                    if cat in forbidden:
                        violations.append(f"User {user['user_id']} ({diet_type}) prefers {cat}")
        
        # Report results
        if violations:
            print(f"\n❌ FAILED: Found {len(violations)} dietary preference violations:")
            for v in violations[:10]:  # Show first 10 violations
                print(f"   - {v}")
            if len(violations) > 10:
                print(f"   ... and {len(violations) - 10} more violations")
        else:
            print("\n✅ PASSED: All users have dietary-appropriate category preferences!")
        
        # Show statistics
        print("\nDiet type distribution:")
        print(users_df['diet_type'].value_counts())
        
        # Show category preferences by diet type
        print("\nSample preferences by diet type:")
        for diet in users_df['diet_type'].unique():
            diet_users = users_df[users_df['diet_type'] == diet]
            sample_user = diet_users.iloc[0]
            print(f"  {diet}: {sample_user['preferred_categories']}")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test different user files
    files_to_test = [
        'users.csv',
        'fake_users.csv',
        '../datasets/fake_users.csv'
    ]
    
    for file in files_to_test:
        try:
            test_dietary_preferences(file)
        except FileNotFoundError:
            print(f"\nFile {file} not found, skipping...") 