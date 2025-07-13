#!/usr/bin/env python3
"""
Migration script to add cost_price and revenue_generated columns to products table
"""

import os
import sys
from supabase import create_client, Client
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bwysarrweyooqtjkowzp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3eXNhcnJ3ZXlvb3F0amtvd3pwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzNTIzODEsImV4cCI6MjA2NzkyODM4MX0.cfOrT6MXZ9XHAjYC0K1rri1C4-jGmBbE9q0RQLpR3d8")

def run_migration():
    """Run the migration to add new columns and update data"""
    
    # SQL commands to add new columns
    sql_commands = """
-- Add cost_price column (40-45% of MRP)
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS cost_price DECIMAL(10, 2);

-- Add revenue_generated column (initialized to 0)
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS revenue_generated DECIMAL(12, 2) DEFAULT 0;

-- Update cost_price for existing products (using 42.5% as average of 40-45%)
UPDATE products 
SET cost_price = ROUND(price_mrp * 0.425, 2)
WHERE cost_price IS NULL;

-- Create index on revenue_generated for performance
CREATE INDEX IF NOT EXISTS idx_products_revenue ON products(revenue_generated);

-- Create a function to update inventory and revenue when transactions are inserted
CREATE OR REPLACE FUNCTION update_product_inventory_revenue()
RETURNS TRIGGER AS $$
BEGIN
    -- Update inventory quantity (decrease by transaction quantity)
    UPDATE products 
    SET inventory_quantity = inventory_quantity - NEW.quantity
    WHERE product_id = NEW.product_id;
    
    -- Update revenue generated (increase by transaction total)
    UPDATE products 
    SET revenue_generated = revenue_generated + NEW.total_price_paid
    WHERE product_id = NEW.product_id;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update inventory and revenue on new transactions
DROP TRIGGER IF EXISTS trigger_update_inventory_revenue ON transactions;
CREATE TRIGGER trigger_update_inventory_revenue
AFTER INSERT ON transactions
FOR EACH ROW
EXECUTE FUNCTION update_product_inventory_revenue();

-- Create a function to get product profitability
CREATE OR REPLACE FUNCTION get_product_profitability()
RETURNS TABLE (
    product_id VARCHAR,
    name VARCHAR,
    category VARCHAR,
    cost_price DECIMAL,
    revenue_generated DECIMAL,
    gross_profit DECIMAL,
    profit_margin DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.product_id,
        p.name,
        p.category,
        p.cost_price,
        p.revenue_generated,
        p.revenue_generated - (p.cost_price * (SELECT COALESCE(SUM(t.quantity), 0) FROM transactions t WHERE t.product_id = p.product_id)) as gross_profit,
        CASE 
            WHEN p.revenue_generated > 0 
            THEN ((p.revenue_generated - (p.cost_price * (SELECT COALESCE(SUM(t.quantity), 0) FROM transactions t WHERE t.product_id = p.product_id))) / p.revenue_generated * 100)
            ELSE 0 
        END as profit_margin
    FROM products p
    WHERE p.revenue_generated > 0
    ORDER BY p.revenue_generated DESC;
END;
$$ LANGUAGE plpgsql;
"""
    
    print("\n" + "="*60)
    print("SUPABASE MIGRATION: Add Cost Price and Revenue Tracking")
    print("="*60)
    print("\nPlease run the following SQL commands in your Supabase SQL Editor:")
    print("\n--- START SQL COMMANDS ---")
    print(sql_commands)
    print("--- END SQL COMMANDS ---\n")
    
    # Connect to Supabase to verify and update Python side
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase successfully")
        
        # Fetch current products to check if migration is needed
        products_response = supabase.table('products').select("*").limit(1).execute()
        if products_response.data:
            sample_product = products_response.data[0]
            
            if 'cost_price' in sample_product and 'revenue_generated' in sample_product:
                logger.info("✅ Migration appears to be already applied!")
                
                # Show some statistics
                stats_response = supabase.table('products').select("count", count="exact").execute()
                total_products = stats_response.count
                
                revenue_response = supabase.table('products').select("revenue_generated").gt('revenue_generated', 0).execute()
                products_with_revenue = len(revenue_response.data)
                
                print(f"\nCurrent Statistics:")
                print(f"- Total Products: {total_products}")
                print(f"- Products with Revenue: {products_with_revenue}")
                
            else:
                logger.warning("⚠️  Migration not yet applied. Please run the SQL commands above.")
                
    except Exception as e:
        logger.error(f"Error connecting to Supabase: {e}")
        print("\n⚠️  Could not verify migration status. Please ensure the SQL commands are run.")

def update_existing_transactions():
    """Update inventory and revenue for existing transactions (if migration wasn't retroactive)"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Get all transactions
        transactions = supabase.table('transactions').select("*").execute()
        transactions_df = pd.DataFrame(transactions.data)
        
        if len(transactions_df) > 0:
            # Group by product_id to calculate totals
            product_stats = transactions_df.groupby('product_id').agg({
                'quantity': 'sum',
                'total_price_paid': 'sum'
            }).reset_index()
            
            print(f"\nUpdating {len(product_stats)} products based on {len(transactions_df)} transactions...")
            
            for _, row in product_stats.iterrows():
                # Update each product
                response = supabase.table('products').update({
                    'inventory_quantity': supabase.raw(f"inventory_quantity - {row['quantity']}"),
                    'revenue_generated': float(row['total_price_paid'])
                }).eq('product_id', row['product_id']).execute()
                
            print("✅ Successfully updated inventory and revenue for all products!")
            
    except Exception as e:
        logger.error(f"Error updating existing transactions: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Migrate products table to add CP and revenue tracking')
    parser.add_argument('--update-transactions', action='store_true', 
                       help='Update inventory and revenue based on existing transactions')
    
    args = parser.parse_args()
    
    # Run migration
    run_migration()
    
    # Optionally update based on existing transactions
    if args.update_transactions:
        print("\n" + "="*60)
        print("UPDATING BASED ON EXISTING TRANSACTIONS")
        print("="*60)
        update_existing_transactions() 