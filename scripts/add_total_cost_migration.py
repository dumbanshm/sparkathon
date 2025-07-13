#!/usr/bin/env python3
"""
Migration script to add total_cost column to products table
total_cost = initial inventory_quantity × cost_price
"""

import os
from supabase import create_client, Client
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bwysarrweyooqtjkowzp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3eXNhcnJ3ZXlvb3F0amtvd3pwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzNTIzODEsImV4cCI6MjA2NzkyODM4MX0.cfOrT6MXZ9XHAjYC0K1rri1C4-jGmBbE9q0RQLpR3d8")

def generate_migration_sql():
    """Generate SQL commands for the migration"""
    
    sql_commands = """
-- Add total_cost column to products table
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS total_cost DECIMAL(12, 2);

-- Add initial_inventory_quantity column to track original inventory
ALTER TABLE products
ADD COLUMN IF NOT EXISTS initial_inventory_quantity INTEGER;

-- Update initial_inventory_quantity for existing products
-- If not set, use current inventory_quantity as initial
UPDATE products
SET initial_inventory_quantity = inventory_quantity
WHERE initial_inventory_quantity IS NULL;

-- Calculate total_cost for existing products
-- total_cost = initial_inventory_quantity × cost_price
UPDATE products
SET total_cost = ROUND(initial_inventory_quantity * cost_price, 2)
WHERE total_cost IS NULL AND cost_price IS NOT NULL;

-- Add comment to explain the field
COMMENT ON COLUMN products.total_cost IS 'Initial inventory investment: initial_inventory_quantity × cost_price. Does not change with transactions.';
COMMENT ON COLUMN products.initial_inventory_quantity IS 'Original inventory quantity when product was added. Used for total_cost calculation.';

-- Create a view for inventory analytics
CREATE OR REPLACE VIEW inventory_analytics AS
SELECT 
    p.product_id,
    p.name,
    p.category,
    p.initial_inventory_quantity,
    p.inventory_quantity as current_inventory,
    (p.initial_inventory_quantity - p.inventory_quantity) as units_sold,
    p.cost_price,
    p.price_mrp,
    p.total_cost as initial_investment,
    p.revenue_generated,
    p.revenue_generated - (p.cost_price * (p.initial_inventory_quantity - p.inventory_quantity)) as gross_profit,
    CASE 
        WHEN p.revenue_generated > 0 
        THEN ((p.revenue_generated - (p.cost_price * (p.initial_inventory_quantity - p.inventory_quantity))) / p.revenue_generated * 100)
        ELSE 0 
    END as profit_margin,
    p.days_until_expiry,
    p.current_discount_percent
FROM products p
ORDER BY p.revenue_generated DESC;
"""
    
    return sql_commands

def verify_migration():
    """Check if migration has been applied"""
    try:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("Connected to Supabase successfully")
        
        # Check a sample product
        sample = supabase.table('products').select("*").limit(1).execute()
        
        if sample.data:
            product = sample.data[0]
            if 'total_cost' in product and 'initial_inventory_quantity' in product:
                logger.info("✅ Migration appears to be already applied!")
                
                # Get some stats
                stats = supabase.table('products').select("category, count, total_cost").execute()
                if stats.data:
                    logger.info(f"Found {len(stats.data)} products with total_cost data")
                    
            else:
                logger.warning("⚠️  Migration not yet applied. Please run the SQL commands.")
                
    except Exception as e:
        logger.error(f"Error: {e}")

def main():
    print("\n" + "="*60)
    print("MIGRATION: Add Total Cost to Products")
    print("="*60)
    print("\nThis migration adds:")
    print("1. total_cost field = initial_inventory_quantity × cost_price")
    print("2. initial_inventory_quantity field to track original inventory")
    print("3. inventory_analytics view for profitability analysis")
    
    sql = generate_migration_sql()
    
    print("\n--- SQL COMMANDS TO RUN IN SUPABASE ---")
    print(sql)
    print("--- END SQL COMMANDS ---\n")
    
    print("After running the SQL, you can verify with:")
    print("SELECT product_id, name, initial_inventory_quantity, cost_price, total_cost")
    print("FROM products LIMIT 5;")
    print("\nAnd check analytics with:")
    print("SELECT * FROM inventory_analytics LIMIT 10;")
    
    # Verify current status
    verify_migration()

if __name__ == "__main__":
    main() 