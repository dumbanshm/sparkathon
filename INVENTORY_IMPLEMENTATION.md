# Inventory-Aware Recommendation System

## Summary of Changes

I've successfully updated the waste reduction recommendation system to consider inventory levels when making recommendations and calculating dead stock risk.

### 1. Data Generation Updates

#### Modified `scripts/walmart_new.py`:
- Added `inventory_quantity` field to transactions (random value between 100-300)
- This represents the total inventory count for each product at the time of transaction

### 2. Database Schema Updates

#### Modified `migrate_to_supabase.py`:
- Added `inventory_quantity INTEGER DEFAULT 200` column to the transactions table
- Migration script now handles the inventory field when importing data

### 3. Recommendation System Updates

#### Modified `unified_waste_reduction_system.py`:

##### A. Inventory Calculation:
- Added logic to calculate current inventory levels by:
  - Taking the most recent inventory reading from transactions
  - Subtracting all sales that occurred after that reading
  - Result is stored in `current_inventory` field on products

##### B. Dead Stock Risk Calculation:
```python
# Now considers inventory levels
if projected_sales < current_inventory * 0.5:
    return 1  # Dead stock risk if can't sell 50% of inventory before expiry
```

##### C. Dynamic Urgency Score:
Added inventory pressure factor that increases urgency when:
- Days to clear inventory exceeds days until expiry
- No sales velocity with high inventory

### 4. How It Works

1. **Inventory Tracking**: Each transaction records the inventory quantity at that time
2. **Current Inventory**: System calculates current inventory by tracking sales since last update
3. **Risk Assessment**: Products with high inventory relative to sales velocity get higher urgency scores
4. **Dynamic Pricing**: Recommended discounts increase for products with inventory pressure

### 5. Example Impact

A product with:
- 200 units in inventory
- 2 units/day sales velocity
- 10 days until expiry
- Would need 100 days to clear inventory

This product will:
- Be flagged as dead stock risk
- Receive higher urgency score (inventory multiplier of 1.5)
- Get more aggressive discount recommendations

### 6. API Usage

The system works seamlessly with existing endpoints:

```bash
# Get recommendations (now considers inventory)
curl http://localhost:8000/recommendations/U0000

# Get dead stock risk items (now uses inventory in calculation)
curl http://localhost:8000/dead_stock_risk

# All responses include inventory-aware scoring
```

### 7. Benefits

1. **More Accurate Risk Assessment**: Products with excess inventory are prioritized
2. **Better Discount Strategies**: Pricing considers inventory pressure
3. **Reduced Waste**: Helps move products before they expire with excess stock
4. **Data-Driven Decisions**: Real inventory levels inform recommendations

The system now provides a more holistic view of product risk by considering not just expiry dates and sales velocity, but also current inventory levels. 