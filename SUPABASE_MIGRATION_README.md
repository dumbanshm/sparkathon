# Supabase Migration Guide

This guide explains how to migrate your waste reduction system data from CSV files to Supabase.

## Prerequisites

1. **Supabase Project**: Create a project at [supabase.com](https://supabase.com)
2. **Python 3.7+**: Ensure Python is installed
3. **CSV Files**: Have your data files ready in the `datasets/` folder:
   - `fake_users.csv`
   - `fake_products.csv`
   - `fake_transactions.csv`

## Installation

1. Install required packages:
```bash
pip install supabase pandas
```

## Migration Steps

### Step 1: Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to Settings → API
3. Copy:
   - **Project URL**: `https://[PROJECT_ID].supabase.co`
   - **Anon Public Key**: Your public API key

### Step 2: Create Tables in Supabase

Run the migration script to generate SQL commands:

```bash
python migrate_to_supabase.py --url YOUR_SUPABASE_URL --key YOUR_ANON_KEY --create-tables
```

This will output SQL commands. Copy them and:
1. Go to your Supabase dashboard
2. Navigate to SQL Editor
3. Paste and run the SQL commands

### Step 3: Run the Migration

After creating tables, migrate your data:

```bash
python migrate_to_supabase.py --url YOUR_SUPABASE_URL --key YOUR_ANON_KEY
```

### Step 4: Verify Migration

Check if data was migrated successfully:

```bash
python migrate_to_supabase.py --url YOUR_SUPABASE_URL --key YOUR_ANON_KEY --verify-only
```

## Command Options

- `--url`: Your Supabase project URL (required)
- `--key`: Your Supabase anon key (required)
- `--datasets-path`: Path to CSV files (default: 'datasets')
- `--create-tables`: Show SQL commands to create tables
- `--skip-users`: Skip migrating users table
- `--skip-products`: Skip migrating products table
- `--skip-transactions`: Skip migrating transactions table
- `--verify-only`: Only verify existing data

## Table Schemas

### Users Table
- `user_id` (VARCHAR): Primary key
- `age` (INTEGER)
- `gender` (VARCHAR)
- `diet_type` (VARCHAR): vegan, vegetarian, eggs, non-vegetarian
- `allergies` (JSONB): Array of allergens
- `prefers_discount` (BOOLEAN)
- `location_lat`, `location_lon` (DECIMAL)
- `preferred_categories` (JSONB): Array of categories
- `last_purchase_date` (DATE)

### Products Table
- `product_id` (VARCHAR): Primary key
- `name` (VARCHAR)
- `category` (VARCHAR): Meat, Dairy, Cheese, etc.
- `brand` (VARCHAR)
- `diet_type` (VARCHAR)
- `allergens` (JSONB): Array of allergens
- `shelf_life_days` (INTEGER)
- `packaging_date`, `expiry_date` (DATE)
- `weight_grams` (INTEGER)
- `price_mrp` (DECIMAL)
- `current_discount_percent` (DECIMAL)
- `store_location_lat`, `store_location_lon` (DECIMAL)

### Transactions Table
- `transaction_id` (SERIAL): Primary key
- `user_id` (VARCHAR): Foreign key to users
- `product_id` (VARCHAR): Foreign key to products
- `purchase_date` (DATE)
- `quantity` (INTEGER)
- `price_paid_per_unit`, `total_price_paid` (DECIMAL)
- `discount_percent` (DECIMAL)
- `product_diet_type`, `user_diet_type` (VARCHAR)
- `days_to_expiry_at_purchase` (INTEGER)
- `user_engaged_with_deal` (INTEGER)

## Using Supabase in Your Application

After migration, update your application to use Supabase:

```python
from supabase import create_client, Client

# Initialize client
supabase: Client = create_client(url, key)

# Example queries
# Get all vegan users
vegan_users = supabase.table('users').select("*").eq('diet_type', 'vegan').execute()

# Get products expiring soon
expiring_products = supabase.table('products').select("*").lte('expiry_date', '2025-08-01').execute()

# Get user transactions
user_transactions = supabase.table('transactions').select("*").eq('user_id', 'U0000').execute()
```

## Troubleshooting

1. **Authentication Error**: Check your Supabase URL and key
2. **Table Not Found**: Ensure you created tables using the SQL commands
3. **Data Type Errors**: Check CSV data formats match expected types
4. **Foreign Key Violations**: Migrate in order: users → products → transactions

## Next Steps

1. Set up Row Level Security (RLS) policies in Supabase
2. Create database functions for complex queries
3. Set up real-time subscriptions for live updates
4. Configure backup and recovery policies
5. Update your FastAPI backend to use Supabase instead of CSV files 