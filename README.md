# Unified Waste Reduction System

A comprehensive system for reducing waste in retail environments through intelligent product recommendations and dynamic dead stock prediction.

## Features

- **Hybrid Recommendation System**: Combines content-based and collaborative filtering approaches
- **Dynamic Threshold Calculation**: Adapts dead stock thresholds based on product category, sales velocity, pricing, and seasonality
- **Dietary & Allergy Filtering**: Ensures recommendations respect user dietary preferences and allergies
- **Urgency-Based Scoring**: Prioritizes products nearing expiry
- **Comprehensive Analytics**: Provides insights into product risk levels and waste reduction strategies

## Installation
//source venv/bin/activate
1. Install required dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure your datasets are in the `datasets/` folder:
   - `fake_users.csv`
   - `fake_products.csv`
   - `fake_transactions.csv`

## Usage

### Quick Start

Run the driver code to see the system in action:

```bash
python run_waste_reduction_system.py
```

This will:
1. Load and analyze the datasets
2. Initialize the recommendation system
3. Build content and collaborative filtering models
4. Perform dead stock risk analysis
5. Generate sample recommendations for users
6. Display waste reduction strategies

### Programmatic Usage

```python
from unified_waste_reduction_system import UnifiedRecommendationSystem
import pandas as pd

# Load your data
users_df = pd.read_csv('datasets/fake_users.csv')
products_df = pd.read_csv('datasets/fake_products.csv')
transactions_df = pd.read_csv('datasets/fake_transactions.csv')

# Initialize the system
system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)

# Build models
system.build_content_similarity_matrix()
system.build_collaborative_filtering_model()

# Get recommendations for a user
recommendations = system.get_hybrid_recommendations(
    user_id='U0001',
    n_recommendations=10,
    content_weight=0.4,
    collaborative_weight=0.6
)
```

## System Components

### 1. Dynamic Threshold Calculator
- Calculates category-based baseline thresholds
- Adjusts thresholds based on:
  - Sales velocity
  - Product pricing
  - Current discount levels
  - Seasonal factors

### 2. Recommendation Engine
- **Content-Based**: Finds similar products based on features
- **Collaborative Filtering**: Uses user purchase patterns
- **Hybrid Approach**: Combines both methods for best results

### 3. Dead Stock Risk Analysis
- Identifies products at risk of becoming dead stock
- Provides actionable insights for inventory management
- Suggests discount strategies

## Output Example

The driver code provides comprehensive output including:

1. **Data Analysis**: Overview of users, products, and transactions
2. **Dead Stock Risk Analysis**: Products at risk with dynamic thresholds
3. **Personalized Recommendations**: Tailored suggestions for each user
4. **Waste Reduction Strategies**: Actionable insights for reducing waste

## Customization

You can customize the system behavior by adjusting:

- Recommendation weights (content vs collaborative)
- Number of recommendations
- Threshold calculation parameters
- Urgency boost factors

## Data Requirements

The system expects CSV files with the following structure:

- **users.csv**: user_id, diet_type, allergies
- **products.csv**: product_id, name, category, price_mrp, expiry_date, packaging_date, diet_type, allergens, etc.
- **transactions.csv**: user_id, product_id, quantity, purchase_date, discount_percent, user_engaged_with_deal 