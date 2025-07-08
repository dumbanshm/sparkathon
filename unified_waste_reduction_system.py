import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.decomposition import TruncatedSVD
from scipy.sparse import csr_matrix
from sklearn.preprocessing import StandardScaler, LabelEncoder
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# --- Dynamic Threshold Logic (from dynamic_threshold_system.py) ---
class DynamicThresholdCalculator:
    """
    Calculates dynamic thresholds for dead stock prediction based on multiple factors
    """
    def __init__(self, products_df, transactions_df):
        self.products_df = products_df
        self.transactions_df = transactions_df
        self.category_thresholds = {}
        self.product_thresholds = {}
    def calculate_category_baseline_thresholds(self):
        category_metrics = self.products_df.groupby('category').agg({
            'shelf_life_days': 'mean',
            'product_id': 'count'
        }).rename(columns={'product_id': 'product_count'})
        sales_by_category = self.transactions_df.merge(
            self.products_df[['product_id', 'category']], on='product_id')
        category_velocity = sales_by_category.groupby('category').agg({
            'quantity': 'sum',
            'purchase_date': lambda x: (x.max() - x.min()).days + 1
        }).rename(columns={'purchase_date': 'days_active'})
        category_velocity['avg_daily_sales'] = (
            category_velocity['quantity'] / category_velocity['days_active']
        )
        category_analysis = category_metrics.merge(
            category_velocity[['avg_daily_sales']], left_index=True, right_index=True, how='left')
        for category in category_analysis.index:
            avg_shelf_life = category_analysis.loc[category, 'shelf_life_days']
            avg_velocity = category_analysis.loc[category, 'avg_daily_sales']
            base_threshold = avg_shelf_life * 0.2
            if avg_velocity > 10:
                velocity_factor = 0.7
            elif avg_velocity > 5:
                velocity_factor = 1.0
            else:
                velocity_factor = 1.3
            self.category_thresholds[category] = int(base_threshold * velocity_factor)
        return self.category_thresholds
    def calculate_product_specific_threshold(self, product_id):
        product = self.products_df[self.products_df['product_id'] == product_id].iloc[0]
        category = product['category']
        base_threshold = self.category_thresholds.get(category, 30)
        product_sales = self.transactions_df[
            self.transactions_df['product_id'] == product_id]
        if len(product_sales) > 0:
            days_on_market = (product_sales['purchase_date'].max() - product_sales['purchase_date'].min()).days + 1
            sales_velocity = len(product_sales) / days_on_market
            if sales_velocity > 2:
                velocity_multiplier = 0.5
            elif sales_velocity > 1:
                velocity_multiplier = 0.7
            elif sales_velocity > 0.5:
                velocity_multiplier = 1.0
            else:
                velocity_multiplier = 1.5
        else:
            velocity_multiplier = 2.0
        price = product['price_mrp']
        if price > 300:
            price_multiplier = 1.2
        elif price < 100:
            price_multiplier = 0.8
        else:
            price_multiplier = 1.0
        current_discount = product.get('current_discount_percent', 0)
        if current_discount > 30:
            discount_multiplier = 0.7
        elif current_discount > 0:
            discount_multiplier = 0.9
        else:
            discount_multiplier = 1.0
        current_month = datetime.now().month
        if category in ['Beverages'] and current_month in [6, 7, 8]:
            seasonal_multiplier = 0.8
        elif category in ['Snacks'] and current_month in [12, 1]:
            seasonal_multiplier = 0.9
        else:
            seasonal_multiplier = 1.0
        dynamic_threshold = (base_threshold * velocity_multiplier * price_multiplier * discount_multiplier * seasonal_multiplier)
        min_threshold = max(3, product['shelf_life_days'] * 0.05)
        max_threshold = min(60, product['shelf_life_days'] * 0.4)
        final_threshold = int(np.clip(dynamic_threshold, min_threshold, max_threshold))
        return {
            'product_id': product_id,
            'category': category,
            'base_threshold': base_threshold,
            'dynamic_threshold': final_threshold,
            'factors': {
                'velocity_multiplier': velocity_multiplier,
                'price_multiplier': price_multiplier,
                'discount_multiplier': discount_multiplier,
                'seasonal_multiplier': seasonal_multiplier
            }
        }
    def calculate_all_thresholds(self):
        self.calculate_category_baseline_thresholds()
        thresholds = []
        for product_id in self.products_df['product_id'].unique():
            threshold_info = self.calculate_product_specific_threshold(product_id)
            thresholds.append(threshold_info)
            self.product_thresholds[product_id] = threshold_info['dynamic_threshold']
        return pd.DataFrame(thresholds)
    def get_threshold(self, product_id):
        if product_id in self.product_thresholds:
            return self.product_thresholds[product_id]
        else:
            threshold_info = self.calculate_product_specific_threshold(product_id)
            self.product_thresholds[product_id] = threshold_info['dynamic_threshold']
            return threshold_info['dynamic_threshold']

def calculate_dead_stock_risk_dynamic(row, threshold_calculator):
    threshold = threshold_calculator.get_threshold(row['product_id'])
    if row['days_until_expiry'] <= 0:
        return 1
    if row['days_until_expiry'] <= threshold:
        if row['sales_velocity'] == 0:
            return 1
        projected_sales = row['sales_velocity'] * row['days_until_expiry']
        if projected_sales < 80:
            return 1
    return 0

# --- Dietary/Allergy Filtering Logic (from product_recommendation_model_final.py) ---
def is_compatible_diet_allergy(user, product):
    # Diet compatibility
    diet_hierarchy = {
        "vegan": 0,
        "vegetarian": 1,
        "eggs": 2,
        "dairy": 2,
        "non-vegetarian": 3
    }
    user_diet = user.get('diet_type', 'non-vegetarian').lower()
    product_diet = product.get('diet_type', 'non-vegetarian').lower()
    if diet_hierarchy.get(product_diet, 3) > diet_hierarchy.get(user_diet, 3):
        return False
    # Allergen check
    user_allergies = set()
    if isinstance(user.get('allergies'), str):
        user_allergies = set(a.strip() for a in user['allergies'].split(',') if a.strip())
    elif isinstance(user.get('allergies'), (set, list)):
        user_allergies = set(user['allergies'])
    product_allergens = set()
    if isinstance(product.get('allergens'), str):
        product_allergens = set(a.strip() for a in product['allergens'].split(',') if a.strip())
    elif isinstance(product.get('allergens'), (set, list)):
        product_allergens = set(product['allergens'])
    if user_allergies & product_allergens:
        return False
    return True

# --- Hybrid Recommendation System (from dynamic_recommendation_system.py, with improved compatibility logic) ---
class UnifiedRecommendationSystem:
    """
    Combines content-based and collaborative filtering, uses dynamic thresholds, and robust dietary/allergy filtering.
    """
    def __init__(self, users_df, products_df, transactions_df):
        self.users_df = users_df
        self.products_df = products_df
        self.transactions_df = transactions_df
        self.le_diet = LabelEncoder()
        self.le_category = LabelEncoder()
        self.content_similarity_matrix = None
        self.user_item_matrix = None
        self.user_factors = None
        self.item_factors = None
        self.product_features = None
        self.threshold_calculator = DynamicThresholdCalculator(products_df, transactions_df)
        self.threshold_calculator.calculate_category_baseline_thresholds()
        
        # Preprocess data to add calculated features
        self.preprocess_data()
    def preprocess_data(self):
        current_date = pd.Timestamp.now()
        
        # Ensure date columns are in datetime format
        if not pd.api.types.is_datetime64_any_dtype(self.products_df['expiry_date']):
            self.products_df['expiry_date'] = pd.to_datetime(self.products_df['expiry_date'])
        if not pd.api.types.is_datetime64_any_dtype(self.products_df['packaging_date']):
            self.products_df['packaging_date'] = pd.to_datetime(self.products_df['packaging_date'])
        if not pd.api.types.is_datetime64_any_dtype(self.transactions_df['purchase_date']):
            self.transactions_df['purchase_date'] = pd.to_datetime(self.transactions_df['purchase_date'])

        # Add days until expiry for each product
        self.products_df['days_until_expiry'] = (self.products_df['expiry_date'] - current_date).dt.days
        self.products_df['total_shelf_life'] = (self.products_df['expiry_date'] - self.products_df['packaging_date']).dt.days
        self.products_df['shelf_life_remaining_pct'] = self.products_df['days_until_expiry'] / self.products_df['total_shelf_life'] * 100

        # Remove already expired products
        self.products_df = self.products_df[self.products_df['days_until_expiry'] > 0].copy()

        # Calculate sales metrics for each product
        sales_metrics = self.transactions_df.groupby('product_id').agg({
            'quantity': ['sum', 'mean', 'count'],
            'purchase_date': ['min', 'max'],
            'discount_percent': 'mean',
            'user_engaged_with_deal': 'mean'
        }).reset_index()

        # Flatten column names
        sales_metrics.columns = ['product_id', 'total_quantity_sold', 'avg_quantity_per_sale', 
                                'number_of_sales', 'first_sale_date', 'last_sale_date',
                                'avg_discount_given', 'avg_user_engagement']

        # Calculate days since last sale
        sales_metrics['days_since_last_sale'] = (current_date - sales_metrics['last_sale_date']).dt.days

        # Calculate sales velocity (units sold per day)
        sales_metrics['days_on_market'] = (sales_metrics['last_sale_date'] - sales_metrics['first_sale_date']).dt.days + 1
        sales_metrics['sales_velocity'] = sales_metrics['total_quantity_sold'] / sales_metrics['days_on_market']

        # Merge sales metrics with products
        self.products_df = self.products_df.merge(sales_metrics, on='product_id', how='left')

        # Fill NaN values for products with no sales
        self.products_df['total_quantity_sold'].fillna(0, inplace=True)
        self.products_df['number_of_sales'].fillna(0, inplace=True)
        self.products_df['sales_velocity'].fillna(0, inplace=True)
        self.products_df['days_since_last_sale'].fillna(999, inplace=True)
        
        # Calculate dead stock risk for each product using the threshold calculator
        self.products_df['is_dead_stock_risk'] = self.products_df.apply(
            lambda row: calculate_dead_stock_risk_dynamic(row, self.threshold_calculator), axis=1
        )
    def prepare_content_features(self):
        products = self.products_df.copy()
        products['content_text'] = (
            products['name'] + ' ' +
            products['category'] + ' ' +
            products['diet_type'] + ' ' +
            products['brand'] + ' ' +
            'price_' + pd.cut(products['price_mrp'], bins=5, labels=['very_low', 'low', 'medium', 'high', 'very_high']).astype(str) + ' '
        )
        products['allergen_text'] = products['allergens'].apply(
            lambda x: ' '.join(eval(x)) if isinstance(x, str) and x != '[]' else ''
        )
        products['content_text'] += ' ' + products['allergen_text']
        products['diet_encoded'] = self.le_diet.fit_transform(products['diet_type'])
        products['category_encoded'] = self.le_category.fit_transform(products['category'])
        self.product_features = products
        return products
    def build_content_similarity_matrix(self):
        products = self.prepare_content_features()
        tfidf = TfidfVectorizer(max_features=100, stop_words='english')
        tfidf_matrix = tfidf.fit_transform(products['content_text'])
        numerical_features = ['price_mrp', 'weight_grams', 'shelf_life_days', 'current_discount_percent', 'diet_encoded', 'category_encoded']
        scaler = StandardScaler()
        numerical_matrix = scaler.fit_transform(products[numerical_features].fillna(0))
        combined_features = np.hstack([
            tfidf_matrix.toarray() * 0.6,
            numerical_matrix * 0.4
        ])
        self.content_similarity_matrix = cosine_similarity(combined_features)
        return self.content_similarity_matrix
    def build_collaborative_filtering_model(self, n_factors=50):
        pivot_table = self.transactions_df.pivot_table(
            index='user_id', columns='product_id', values='quantity', aggfunc='sum', fill_value=0)
        engagement_pivot = self.transactions_df.pivot_table(
            index='user_id', columns='product_id', values='user_engaged_with_deal', aggfunc='mean', fill_value=0)
        self.user_item_matrix = pivot_table + 0.5 * engagement_pivot
        sparse_matrix = csr_matrix(self.user_item_matrix.values)
        svd = TruncatedSVD(n_components=n_factors, random_state=42)
        self.user_factors = svd.fit_transform(sparse_matrix)
        self.item_factors = svd.components_.T
        return self.user_factors, self.item_factors
    def get_hybrid_recommendations(self, user_id, n_recommendations=10, content_weight=0.4, collaborative_weight=0.6):
        user_products = self.transactions_df[
            self.transactions_df['user_id'] == user_id
        ]['product_id'].unique()
        if len(user_products) == 0:
            return self.get_popular_expiring_products(n_recommendations)
        collab_recs = self.get_collaborative_recommendations(user_id, n_recommendations * 2)
        content_recs_list = []
        for product_id in user_products[-3:]:
            content_recs = self.get_content_based_recommendations(product_id, n_recommendations)
            content_recs_list.append(content_recs)
        if content_recs_list:
            content_recs_combined = pd.concat(content_recs_list).groupby('product_id').agg({
                'final_score': 'mean',
                'product_name': 'first',
                'days_until_expiry': 'first',
                'category': 'first',
                'price': 'first',
                'discount': 'first'
            }).reset_index()
        else:
            content_recs_combined = pd.DataFrame()
        all_products = set()
        if not collab_recs.empty:
            all_products.update(collab_recs['product_id'].tolist())
        if not content_recs_combined.empty:
            all_products.update(content_recs_combined['product_id'].tolist())
        hybrid_scores = []
        user = self.users_df[self.users_df['user_id'] == user_id].iloc[0].to_dict()
        for product_id in all_products:
            score = 0
            if not collab_recs.empty and product_id in collab_recs['product_id'].values:
                collab_score = collab_recs[collab_recs['product_id'] == product_id]['final_score'].iloc[0]
                score += collaborative_weight * collab_score
            if not content_recs_combined.empty and product_id in content_recs_combined['product_id'].values:
                content_score = content_recs_combined[content_recs_combined['product_id'] == product_id]['final_score'].iloc[0]
                score += content_weight * content_score
            product_row = self.products_df[self.products_df['product_id'] == product_id]
            if product_row.empty:
                continue  # Skip if product not found (e.g., filtered out as expired)
            product = product_row.iloc[0].to_dict()
            if not is_compatible_diet_allergy(user, product):
                continue
            hybrid_scores.append({
                'product_id': product_id,
                'product_name': product['name'],
                'hybrid_score': score,
                'days_until_expiry': product['days_until_expiry'],
                'category': product['category'],
                'price': product['price_mrp'],
                'discount': product['current_discount_percent'],
                'is_dead_stock_risk': product.get('is_dead_stock_risk', 0)
            })
        hybrid_df = pd.DataFrame(hybrid_scores)
        return hybrid_df.nlargest(n_recommendations, 'hybrid_score')
    def get_content_based_recommendations(self, product_id, n_recommendations=10, filter_expired=True, urgency_boost=True):
        if self.content_similarity_matrix is None:
            self.build_content_similarity_matrix()
        product_row = self.products_df[self.products_df['product_id'] == product_id]
        if product_row.empty:
            return pd.DataFrame()  # Product not found, return empty
        product_idx = product_row.index[0]
        sim_scores = list(enumerate(self.content_similarity_matrix[product_idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        similar_products = []
        for idx, score in sim_scores[1:]:
            product = self.products_df.iloc[idx]
            if filter_expired and product['days_until_expiry'] <= 0:
                continue
            recommendation = {
                'product_id': product['product_id'],
                'product_name': product['name'],
                'similarity_score': score,
                'days_until_expiry': product['days_until_expiry'],
                'category': product['category'],
                'price': product['price_mrp'],
                'discount': product['current_discount_percent']
            }
            if urgency_boost and product['days_until_expiry'] <= 30:
                urgency_factor = 1 + (30 - product['days_until_expiry']) / 30 * 0.5
                recommendation['final_score'] = score * urgency_factor
            else:
                recommendation['final_score'] = score
            similar_products.append(recommendation)
            if len(similar_products) >= n_recommendations:
                break
        return pd.DataFrame(similar_products).sort_values('final_score', ascending=False)
    def get_collaborative_recommendations(self, user_id, n_recommendations=10, filter_purchased=True, focus_on_expiring=True):
        if self.user_factors is None:
            self.build_collaborative_filtering_model()
        if user_id not in self.user_item_matrix.index:
            return self.get_popular_expiring_products(n_recommendations)
        user_idx = self.user_item_matrix.index.get_loc(user_id)
        user_vector = self.user_factors[user_idx]
        predicted_ratings = np.dot(user_vector, self.item_factors.T)
        product_ids = self.user_item_matrix.columns
        recommendations = []
        user = self.users_df[self.users_df['user_id'] == user_id].iloc[0].to_dict()
        for idx, rating in enumerate(predicted_ratings):
            product_id = product_ids[idx]
            if filter_purchased and self.user_item_matrix.iloc[user_idx, idx] > 0:
                continue
            product_row = self.products_df[self.products_df['product_id'] == product_id]
            if product_row.empty:
                continue  # Skip if product not found (e.g., filtered out as expired)
            product = product_row.iloc[0].to_dict()
            if product['days_until_expiry'] <= 0:
                continue
            if not is_compatible_diet_allergy(user, product):
                continue
            recommendation = {
                'product_id': product_id,
                'product_name': product['name'],
                'predicted_rating': rating,
                'days_until_expiry': product['days_until_expiry'],
                'category': product['category'],
                'price': product['price_mrp'],
                'discount': product['current_discount_percent']
            }
            if focus_on_expiring and product['days_until_expiry'] <= 30:
                urgency_factor = 1 + (30 - product['days_until_expiry']) / 30 * 0.5
                recommendation['final_score'] = rating * urgency_factor
            else:
                recommendation['final_score'] = rating
            recommendations.append(recommendation)
        recommendations_df = pd.DataFrame(recommendations)
        return recommendations_df.nlargest(n_recommendations, 'final_score')
    def get_popular_expiring_products(self, n_recommendations=10):
        expiring_products = self.products_df[(self.products_df['days_until_expiry'] > 0) & (self.products_df['days_until_expiry'] <= 30)].copy()
        product_popularity = self.transactions_df.groupby('product_id').agg({
            'quantity': 'sum',
            'user_id': 'nunique'
        }).rename(columns={'user_id': 'unique_buyers'})
        expiring_products = expiring_products.merge(
            product_popularity, left_on='product_id', right_index=True, how='left')
        expiring_products['urgency_score'] = (30 - expiring_products['days_until_expiry']) / 30
        expiring_products['recommendation_score'] = (
            expiring_products['quantity'].fillna(0) * 0.4 +
            expiring_products['unique_buyers'].fillna(0) * 0.3 +
            expiring_products['urgency_score'] * 0.3
        )
        
        # Add is_dead_stock_risk flag if not already present
        if 'is_dead_stock_risk' not in expiring_products.columns:
            expiring_products['is_dead_stock_risk'] = expiring_products.apply(
                lambda row: calculate_dead_stock_risk_dynamic(row, self.threshold_calculator), axis=1
            )
        
        return expiring_products.nlargest(n_recommendations, 'recommendation_score')[[
            'product_id', 'name', 'category', 'days_until_expiry', 'price_mrp', 'current_discount_percent', 'recommendation_score', 'is_dead_stock_risk'
        ]].rename(columns={
            'name': 'product_name',
            'recommendation_score': 'hybrid_score',
            'price_mrp': 'price',
            'current_discount_percent': 'discount'
        })

# --- Example Usage ---
if __name__ == "__main__":
    print("Unified Waste Reduction System Example")
    print("="*50)
    # Example: Load your dataframes here (users_df, products_df, transactions_df)
    # users_df = pd.read_csv('users.csv')
    # products_df = pd.read_csv('products.csv')
    # transactions_df = pd.read_csv('transactions.csv')
    # system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
    # system.build_content_similarity_matrix()
    # system.build_collaborative_filtering_model()
    # recs = system.get_hybrid_recommendations(user_id='U0001', n_recommendations=5)
    # print(recs) 