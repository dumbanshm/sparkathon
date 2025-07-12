-- Reset script to prepare for fresh migration with new data structure

-- Step 1: Drop existing data (but keep table structure)
TRUNCATE TABLE transactions CASCADE;
TRUNCATE TABLE products CASCADE;
TRUNCATE TABLE users CASCADE;

-- Step 2: Alter products table to add inventory_quantity if it doesn't exist
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS inventory_quantity INTEGER DEFAULT 200;

-- Step 3: Alter transactions table to drop inventory_quantity if it exists
ALTER TABLE transactions 
DROP COLUMN IF EXISTS inventory_quantity;

-- Step 4: Verify tables are empty
SELECT 
    'users' as table_name,
    COUNT(*) as row_count
FROM users
UNION ALL
SELECT 
    'products' as table_name,
    COUNT(*) as row_count
FROM products
UNION ALL
SELECT 
    'transactions' as table_name,
    COUNT(*) as row_count
FROM transactions;

-- Step 5: Check column structure
SELECT 
    column_name,
    data_type,
    column_default
FROM information_schema.columns
WHERE table_name = 'products'
    AND column_name = 'inventory_quantity';

SELECT 
    column_name
FROM information_schema.columns
WHERE table_name = 'transactions'
ORDER BY ordinal_position; 