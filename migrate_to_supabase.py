import pandas as pd
import os
import sys
from datetime import datetime
import json
from supabase import create_client, Client
import argparse
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SupabaseMigration:
    def __init__(self, supabase_url: str, supabase_key: str):
        """Initialize Supabase client"""
        self.supabase: Client = create_client(supabase_url, supabase_key)
        logger.info("Connected to Supabase")
    
    def create_tables(self):
        """Create tables in Supabase if they don't exist"""
        logger.info("Creating tables...")
        
        # SQL commands to create tables
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(10) PRIMARY KEY,
            age INTEGER,
            gender VARCHAR(10),
            diet_type VARCHAR(20),
            allergies JSONB,
            prefers_discount BOOLEAN,
            location_lat DECIMAL(10, 7),
            location_lon DECIMAL(10, 7),
            preferred_categories JSONB,
            last_purchase_date DATE,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        create_products_table = """
        CREATE TABLE IF NOT EXISTS products (
            product_id VARCHAR(10) PRIMARY KEY,
            name VARCHAR(200),
            category VARCHAR(50),
            brand VARCHAR(100),
            diet_type VARCHAR(20),
            allergens TEXT[],
            shelf_life_days INTEGER,
            packaging_date DATE,
            expiry_date DATE,
            weight_grams INTEGER,
            price_mrp DECIMAL(10, 2),
            cost_price DECIMAL(10, 2),
            current_discount_percent DECIMAL(5, 2),
            inventory_quantity INTEGER DEFAULT 200,
            initial_inventory_quantity INTEGER,
            total_cost DECIMAL(12, 2),
            revenue_generated DECIMAL(12, 2) DEFAULT 0,
            store_location_lat DECIMAL(10, 8),
            store_location_lon DECIMAL(11, 8),
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        create_transactions_table = """
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id SERIAL PRIMARY KEY,
            user_id VARCHAR(10) REFERENCES users(user_id),
            product_id VARCHAR(10) REFERENCES products(product_id),
            purchase_date DATE,
            quantity INTEGER,
            price_paid_per_unit DECIMAL(10, 2),
            total_price_paid DECIMAL(10, 2),
            discount_percent DECIMAL(5, 2),
            product_diet_type VARCHAR(20),
            user_diet_type VARCHAR(20),
            days_to_expiry_at_purchase INTEGER,
            user_engaged_with_deal INTEGER,
            created_at TIMESTAMP DEFAULT NOW()
        );
        """
        
        # Create indexes for better performance
        create_indexes = """
        CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_product_id ON transactions(product_id);
        CREATE INDEX IF NOT EXISTS idx_transactions_purchase_date ON transactions(purchase_date);
        CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
        CREATE INDEX IF NOT EXISTS idx_products_diet_type ON products(diet_type);
        CREATE INDEX IF NOT EXISTS idx_users_diet_type ON users(diet_type);
        """
        
        # Note: Supabase doesn't support direct SQL execution through the Python client
        # You'll need to run these SQL commands in the Supabase SQL editor
        logger.info("Please run the following SQL commands in your Supabase SQL editor:")
        print("\n--- COPY AND PASTE THESE SQL COMMANDS IN SUPABASE SQL EDITOR ---\n")
        print(create_users_table)
        print(create_products_table)
        print(create_transactions_table)
        print(create_indexes)
        print("\n--- END OF SQL COMMANDS ---\n")
        
        return True
    
    def parse_list_field(self, value: str) -> List[str]:
        """Parse string representation of list to actual list"""
        if pd.isna(value) or value == '[]' or value == '':
            return []
        
        # Handle different list formats
        if value.startswith('[') and value.endswith(']'):
            # It's already in list format, use eval (safe in this context)
            try:
                return eval(value)
            except:
                return []
        else:
            # It's comma-separated
            return [item.strip() for item in value.split(',') if item.strip()]
    
    def migrate_users(self, csv_path: str) -> bool:
        """Migrate users data from CSV to Supabase"""
        logger.info(f"Migrating users from {csv_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Found {len(df)} users to migrate")
            
            # Transform data
            users_data = []
            for _, row in df.iterrows():
                user = {
                    'user_id': row['user_id'],
                    'age': int(row['age']),
                    'gender': row['gender'],
                    'diet_type': row['diet_type'],
                    'allergies': self.parse_list_field(row['allergies']),
                    'prefers_discount': bool(row['prefers_discount']),
                    'location_lat': float(row['location_lat']),
                    'location_lon': float(row['location_lon']),
                    'preferred_categories': self.parse_list_field(row['preferred_categories']),
                    'last_purchase_date': row['last_purchase_date']
                }
                users_data.append(user)
            
            # Insert in batches
            batch_size = 100
            for i in range(0, len(users_data), batch_size):
                batch = users_data[i:i + batch_size]
                response = self.supabase.table('users').insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1} of {len(users_data)//batch_size + 1}")
            
            logger.info(f"Successfully migrated {len(users_data)} users")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating users: {e}")
            return False
    
    def migrate_products(self, csv_path: str) -> bool:
        """Migrate products data from CSV to Supabase"""
        logger.info(f"Migrating products from {csv_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Found {len(df)} products to migrate")
            
            # Transform data
            products_data = []
            for _, row in df.iterrows():
                # Get inventory quantity (use default if not present)
                inventory_qty = int(row.get('inventory_quantity', 200))
                cost_price = float(row['cost_price']) if 'cost_price' in row else float(row['price_mrp']) * 0.425
                
                product = {
                    'product_id': row['product_id'],
                    'name': row['name'],
                    'category': row['category'],
                    'brand': row['brand'],
                    'diet_type': row['diet_type'],
                    'allergens': self.parse_list_field(row['allergens']),
                    'shelf_life_days': int(row['shelf_life_days']),
                    'packaging_date': row['packaging_date'],
                    'expiry_date': row['expiry_date'],
                    'weight_grams': int(row['weight_grams']),
                    'price_mrp': float(row['price_mrp']),
                    'cost_price': cost_price,
                    'current_discount_percent': float(row['current_discount_percent']),
                    'inventory_quantity': inventory_qty,
                    'initial_inventory_quantity': int(row.get('initial_inventory_quantity', inventory_qty)),
                    'total_cost': float(row['total_cost']) if 'total_cost' in row else round(inventory_qty * cost_price, 2),
                    'revenue_generated': float(row.get('revenue_generated', 0)),
                    'store_location_lat': float(row['store_location_lat']),
                    'store_location_lon': float(row['store_location_lon'])
                }
                products_data.append(product)
            
            # Insert in batches
            batch_size = 100
            for i in range(0, len(products_data), batch_size):
                batch = products_data[i:i + batch_size]
                response = self.supabase.table('products').insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1} of {len(products_data)//batch_size + 1}")
            
            logger.info(f"Successfully migrated {len(products_data)} products")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating products: {e}")
            return False
    
    def migrate_transactions(self, csv_path: str) -> bool:
        """Migrate transactions data from CSV to Supabase"""
        logger.info(f"Migrating transactions from {csv_path}")
        
        try:
            # Read CSV
            df = pd.read_csv(csv_path)
            logger.info(f"Found {len(df)} transactions to migrate")
            
            # Transform data
            transactions_data = []
            for _, row in df.iterrows():
                transaction = {
                    'user_id': row['user_id'],
                    'product_id': row['product_id'],
                    'purchase_date': row['purchase_date'],
                    'quantity': int(row['quantity']),
                    'price_paid_per_unit': float(row['price_paid_per_unit']),
                    'total_price_paid': float(row['total_price_paid']),
                    'discount_percent': float(row['discount_percent']),
                    'product_diet_type': row['product_diet_type'],
                    'user_diet_type': row['user_diet_type'],
                    'days_to_expiry_at_purchase': int(row['days_to_expiry_at_purchase']),
                    'user_engaged_with_deal': int(row['user_engaged_with_deal'])
                }
                transactions_data.append(transaction)
            
            # Insert in batches
            batch_size = 100
            for i in range(0, len(transactions_data), batch_size):
                batch = transactions_data[i:i + batch_size]
                response = self.supabase.table('transactions').insert(batch).execute()
                logger.info(f"Inserted batch {i//batch_size + 1} of {len(transactions_data)//batch_size + 1}")
            
            logger.info(f"Successfully migrated {len(transactions_data)} transactions")
            return True
            
        except Exception as e:
            logger.error(f"Error migrating transactions: {e}")
            return False
    
    def verify_migration(self):
        """Verify that data was migrated successfully"""
        logger.info("Verifying migration...")
        
        try:
            # Count records in each table
            users_count = len(self.supabase.table('users').select("*", count='exact').execute().data)
            products_count = len(self.supabase.table('products').select("*", count='exact').execute().data)
            transactions_count = len(self.supabase.table('transactions').select("*", count='exact').execute().data)
            
            logger.info(f"Users in Supabase: {users_count}")
            logger.info(f"Products in Supabase: {products_count}")
            logger.info(f"Transactions in Supabase: {transactions_count}")
            
            # Test some queries
            logger.info("\nTesting some queries...")
            
            # Get vegan users
            vegan_users = self.supabase.table('users').select("*").eq('diet_type', 'vegan').execute()
            logger.info(f"Found {len(vegan_users.data)} vegan users")
            
            # Get meat products
            meat_products = self.supabase.table('products').select("*").eq('category', 'Meat').execute()
            logger.info(f"Found {len(meat_products.data)} meat products")
            
            # Get recent transactions
            recent_transactions = self.supabase.table('transactions').select("*").limit(10).execute()
            logger.info(f"Retrieved {len(recent_transactions.data)} recent transactions")
            
            return True
            
        except Exception as e:
            logger.error(f"Error verifying migration: {e}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Migrate CSV data to Supabase')
    parser.add_argument('--url', required=True, help='Supabase project URL')
    parser.add_argument('--key', required=True, help='Supabase anon key')
    parser.add_argument('--datasets-path', default='datasets', help='Path to datasets folder')
    parser.add_argument('--create-tables', action='store_true', help='Show SQL to create tables')
    parser.add_argument('--skip-users', action='store_true', help='Skip migrating users')
    parser.add_argument('--skip-products', action='store_true', help='Skip migrating products')
    parser.add_argument('--skip-transactions', action='store_true', help='Skip migrating transactions')
    parser.add_argument('--verify-only', action='store_true', help='Only verify existing data')
    
    args = parser.parse_args()
    
    # Initialize migration
    migration = SupabaseMigration(args.url, args.key)
    
    if args.create_tables:
        migration.create_tables()
        print("\nAfter creating tables in Supabase, run this script again without --create-tables flag")
        return
    
    if args.verify_only:
        migration.verify_migration()
        return
    
    # Perform migration
    success = True
    
    if not args.skip_users:
        users_path = os.path.join(args.datasets_path, 'fake_users.csv')
        if os.path.exists(users_path):
            success &= migration.migrate_users(users_path)
        else:
            logger.error(f"Users file not found: {users_path}")
            success = False
    
    if not args.skip_products:
        products_path = os.path.join(args.datasets_path, 'fake_products.csv')
        if os.path.exists(products_path):
            success &= migration.migrate_products(products_path)
        else:
            logger.error(f"Products file not found: {products_path}")
            success = False
    
    if not args.skip_transactions:
        transactions_path = os.path.join(args.datasets_path, 'fake_transactions.csv')
        if os.path.exists(transactions_path):
            success &= migration.migrate_transactions(transactions_path)
        else:
            logger.error(f"Transactions file not found: {transactions_path}")
            success = False
    
    if success:
        logger.info("\nMigration completed successfully!")
        migration.verify_migration()
    else:
        logger.error("\nMigration failed. Please check the errors above.")

if __name__ == "__main__":
    main() 