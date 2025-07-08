# Waste Reduction System

A unified waste reduction system that combines content-based and collaborative filtering recommendations with dynamic threshold calculations for dead stock prediction.

## 🚀 Quick Start with Gitpod

Click the button below to start a ready-to-code development environment:

[![Open in Gitpod](https://gitpod.io/button/open-in-gitpod.svg)](https://gitpod.io/#https://github.com/yourusername/yourrepo)

## 📋 Prerequisites

- Python 3.10 or higher
- pip package manager

## 🛠️ Local Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/yourrepo.git
cd yourrepo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## 📁 Project Structure

- `unified_waste_reduction_system.py` - Main system implementation
- `waste_reduction_system.ipynb` - Jupyter notebook with examples
- `datasets/` - Data files directory
- `models/` - Saved model files
- `scripts/` - Utility scripts

## 🎯 Features

- **Dynamic Threshold Calculation**: Adaptive thresholds for dead stock prediction based on product categories, sales velocity, pricing, and seasonality
- **Hybrid Recommendation System**: Combines content-based and collaborative filtering approaches
- **Dietary/Allergy Filtering**: Ensures recommendations respect user dietary preferences and allergies
- **Urgency Boosting**: Prioritizes products approaching expiration dates

## 💻 Usage

### Basic Example

```python
from unified_waste_reduction_system import UnifiedRecommendationSystem

# Initialize the system
system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)

# Build models
system.build_content_similarity_matrix()
system.build_collaborative_filtering_model()

# Get recommendations for a user
recommendations = system.get_hybrid_recommendations(user_id='U0001', n_recommendations=5)
print(recommendations)
```

### Running the Jupyter Notebook

```bash
jupyter notebook waste_reduction_system.ipynb
```

## 📦 Dependencies

See `requirements.txt` for a full list of dependencies. Main packages include:
- pandas & numpy for data processing
- scikit-learn for machine learning
- scipy for scientific computing
- jupyter for interactive notebooks

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📄 License

This project is licensed under the MIT License. 