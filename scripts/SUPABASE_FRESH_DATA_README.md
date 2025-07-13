# Supabase Fresh Data Setup

This guide explains how to recreate Supabase tables from scratch and populate them with fresh fake data.

## Overview

The process involves two main scripts:
1. `recreate_tables_fresh.py` - Generates SQL to drop and recreate all tables with proper structure, triggers, and views
2. `faker_to_supabase.py` - Generates fake data and inserts it directly into Supabase

## Prerequisites

- Python 3.7+
- Required packages: `supabase`, `faker`, `pandas`
- Supabase project with proper credentials

## Step 1: Recreate Tables Fresh

### Generate the SQL Script

```bash
cd scripts
python recreate_tables_fresh.py
```

This will:
- Prompt for confirmation
- Generate a timestamped SQL file (e.g., `recreate_tables_20240113_123456.sql`)
- Display the SQL script

### Execute in Supabase

1. Go to your [Supabase Dashboard](https://app.supabase.io)
2. Navigate to **SQL Editor**
3. Copy the entire contents of the generated SQL file
4. Paste into the SQL editor
5. **Review carefully** - this will DELETE ALL EXISTING DATA!
6. Click **Run**

The SQL script will:
- Drop all existing views, triggers, functions, and tables
- Create fresh tables with proper constraints
- Set up automatic triggers for inventory and revenue tracking
- Create the inventory analytics view
- Grant necessary permissions

## Step 2: Populate with Fake Data

### Run the Faker Script

```bash
python faker_to_supabase.py
```

This will:
- Connect to Supabase using environment variables or default credentials
- Generate and insert:
  - 200 users with realistic profiles
  - 300 products across 11 categories
  - 1000 transactions
- Verify the data insertion

### Configuration Options

You can modify the data volume in `faker_to_supabase.py`:

```python
NUM_USERS = 200
NUM_PRODUCTS = 300
NUM_TRANSACTIONS = 1000
```

## Data Features

### Users
- Realistic age distribution (18-70)
- Diet preferences (vegan, vegetarian, non-vegetarian, eggitarian)
- **Diet-aware category preferences**: Users only prefer categories compatible with their diet
- Allergies (random distribution)
- Location coordinates
- Discount preferences

### Products
- 11 categories: Dairy, Vegetables, Fruits, Meat, Grains, Snacks, Beverages, Biscuits, Sauces, Spreads, Cheese
- Realistic brand names per category
- **Diet type assignment**: 
  - Meat products are always non-vegetarian
  - Dairy/Cheese can be vegetarian or eggitarian
  - Other categories can be vegan or vegetarian
- Appropriate shelf life by category
- Cost price (40-45% of MRP)
- Dynamic discounts based on expiry
- Inventory tracking fields

### Transactions
- **Diet-compliant purchases**: 
  - Vegans only buy vegan products
  - Vegetarians avoid meat products
  - Eggitarians avoid meat but can buy dairy
  - Non-vegetarians can buy anything
- **Allergy-aware shopping**: Users never purchase products containing their allergens
- Realistic purchase patterns
- Quantity based on product type
- Enhanced discount application logic:
  - Higher chance for discount-preferring users
  - Extra consideration for high-discount items
- Automatic inventory and revenue updates via triggers

## Database Schema

### Tables
- `users` - Customer profiles
- `products` - Product catalog with pricing and inventory
- `transactions` - Purchase history

### Automatic Features
- Inventory deduction on transaction
- Revenue tracking on transaction
- User's last purchase date update
- Inventory analytics view
- Product profitability functions

## Verification

After running both scripts, verify the setup:

```bash
# Check the data via API
curl -X GET "http://localhost:8000/products" | jq '. | length'
curl -X GET "http://localhost:8000/users" | jq '. | length'
curl -X GET "http://localhost:8000/expired_products"
curl -X GET "http://localhost:8000/inventory_analytics"
```

## Troubleshooting

### Permission Issues
If you get permission errors, ensure your Supabase anon key has appropriate permissions.

### Data Insertion Failures
- Check table constraints (the script validates most data)
- Ensure tables were created successfully
- Check Supabase logs for detailed errors

### Connection Issues
- Verify SUPABASE_URL and SUPABASE_KEY
- Check network connectivity
- Ensure Supabase project is active

## Notes

- The scripts use realistic data distributions based on retail patterns
- Expired products are intentionally included for testing
- Triggers automatically maintain data consistency
- All monetary values are in INR (₹)

## Safety

⚠️ **WARNING**: The recreation script DROPS ALL EXISTING DATA. Always backup before running! 