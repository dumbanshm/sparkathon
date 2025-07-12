-- Migration script to move inventory_quantity from transactions to products

-- Step 1: Add inventory_quantity column to products table if it doesn't exist
ALTER TABLE products 
ADD COLUMN IF NOT EXISTS inventory_quantity INTEGER DEFAULT 200;

-- Step 2: Update products with the most recent inventory quantity from transactions
-- This gets the latest inventory reading for each product
UPDATE products p
SET inventory_quantity = COALESCE(
    (SELECT t.inventory_quantity
     FROM transactions t
     WHERE t.product_id = p.product_id
       AND t.inventory_quantity IS NOT NULL
     ORDER BY t.purchase_date DESC, t.transaction_id DESC
     LIMIT 1),
    200  -- Default value if no inventory data exists
);

-- Step 3: Calculate the current inventory by subtracting sales since last inventory update
WITH latest_inventory AS (
    -- Get the most recent transaction with inventory data for each product
    SELECT DISTINCT ON (product_id)
        product_id,
        purchase_date as inventory_date,
        inventory_quantity
    FROM transactions
    WHERE inventory_quantity IS NOT NULL
    ORDER BY product_id, purchase_date DESC, transaction_id DESC
),
sales_since_inventory AS (
    -- Calculate total sold since the last inventory update
    SELECT 
        li.product_id,
        li.inventory_quantity as last_inventory,
        li.inventory_date,
        COALESCE(SUM(t.quantity), 0) as sold_since_inventory
    FROM latest_inventory li
    LEFT JOIN transactions t ON 
        t.product_id = li.product_id 
        AND t.purchase_date > li.inventory_date
    GROUP BY li.product_id, li.inventory_quantity, li.inventory_date
)
UPDATE products p
SET inventory_quantity = GREATEST(0, ssi.last_inventory - ssi.sold_since_inventory)
FROM sales_since_inventory ssi
WHERE p.product_id = ssi.product_id;

-- Step 4: Drop the inventory_quantity column from transactions table
ALTER TABLE transactions 
DROP COLUMN IF EXISTS inventory_quantity;

-- Step 5: Verify the migration
SELECT 
    'Products with inventory' as check_type,
    COUNT(*) as count
FROM products
WHERE inventory_quantity IS NOT NULL
UNION ALL
SELECT 
    'Products with zero inventory' as check_type,
    COUNT(*) as count
FROM products
WHERE inventory_quantity = 0; 