import os
import sys
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from pydantic import BaseModel
import pandas as pd
import logging
from datetime import datetime
from supabase import create_client, Client

# Import the existing UnifiedRecommendationSystem
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from unified_waste_reduction_system import UnifiedRecommendationSystem

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://bwysarrweyooqtjkowzp.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJ3eXNhcnJ3ZXlvb3F0amtvd3pwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTIzNTIzODEsImV4cCI6MjA2NzkyODM4MX0.cfOrT6MXZ9XHAjYC0K1rri1C4-jGmBbE9q0RQLpR3d8")

# Load all data from Supabase at startup
try:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
    logger.info("Connected to Supabase successfully")
    
    # Fetch all users
    users_response = supabase.table('users').select("*").execute()
    users_df = pd.DataFrame(users_response.data)
    logger.info(f"Loaded {len(users_df)} users from Supabase")
    
    # Fetch all products
    products_response = supabase.table('products').select("*").execute()
    products_df = pd.DataFrame(products_response.data)
    
    # Convert date strings to datetime objects
    products_df['packaging_date'] = pd.to_datetime(products_df['packaging_date'])
    products_df['expiry_date'] = pd.to_datetime(products_df['expiry_date'])
    
    logger.info(f"Loaded {len(products_df)} products from Supabase")
    
    # Fetch all transactions
    transactions_response = supabase.table('transactions').select("*").execute()
    transactions_df = pd.DataFrame(transactions_response.data)
    
    # Convert date strings to datetime objects
    transactions_df['purchase_date'] = pd.to_datetime(transactions_df['purchase_date'])
    
    logger.info(f"Loaded {len(transactions_df)} transactions from Supabase")
    
    # Initialize the UnifiedRecommendationSystem with the loaded data
    system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
    logger.info("UnifiedRecommendationSystem initialized successfully")
    
except Exception as e:
    logger.error(f"Failed to initialize system: {e}")
    system = None

app = FastAPI(
    title="Unified Waste Reduction API (Supabase)",
    description="API for waste reduction recommendations using Supabase data with original model logic",
    version="3.0.0"
)

# Enhanced CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Pydantic models for responses (same as original)
class Recommendation(BaseModel):
    product_id: str
    product_name: str
    name: str
    category: str
    days_until_expiry: int
    price: float
    price_mrp: float
    discount: float
    current_discount_percent: float
    expiry_date: Optional[str] = None
    score: Optional[float] = None
    is_dead_stock_risk: Optional[int] = None

class RecommendationsResponse(BaseModel):
    user_id: str
    recommendations: List[Recommendation]

class DeadStockRiskItem(BaseModel):
    product_id: str
    name: str
    category: str
    days_until_expiry: int
    current_discount_percent: float
    price_mrp: float
    inventory_quantity: Optional[int] = None
    expiry_date: Optional[str] = None
    risk_score: Optional[float] = None
    threshold: Optional[int] = None

class Product(BaseModel):
    product_id: str
    name: str
    category: str
    brand: str
    diet_type: str
    allergens: List[str]
    shelf_life_days: int
    packaging_date: str
    expiry_date: str
    days_until_expiry: int
    weight_grams: int
    price_mrp: float
    current_discount_percent: float
    inventory_quantity: int
    store_location_lat: float
    store_location_lon: float
    is_dead_stock_risk: Optional[int] = None

class ApiResponse(BaseModel):
    message: str
    status: str = "success"

@app.get("/", response_model=ApiResponse)
def root():
    return ApiResponse(
        message="Unified Waste Reduction System API (Supabase) is running.",
        status="success"
    )

@app.get("/health")
def health_check():
    """Health check endpoint"""
    model_status = "loaded" if system is not None else "not_loaded"
    db_status = "connected" if supabase is not None else "disconnected"
    return {
        "status": "healthy",
        "model_status": model_status,
        "database_status": db_status,
        "api_version": "3.0.0"
    }

@app.get("/recommendations/{user_id}", response_model=RecommendationsResponse)
def get_recommendations(user_id: str, n: int = Query(10, ge=1, le=50)):
    """Get personalized recommendations for a user"""
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    try:
        logger.info(f"Generating recommendations for user: {user_id}")
        recs = system.get_hybrid_recommendations(user_id, n_recommendations=n)
        
        if recs.empty:
            logger.warning(f"No recommendations found for user: {user_id}")
            return RecommendationsResponse(user_id=user_id, recommendations=[])
        
        # Convert DataFrame to list of Recommendation
        recommendations = []
        for _, row in recs.iterrows():
            try:
                recommendation = Recommendation(
                    product_id=str(row.get("product_id", "")),
                    product_name=str(row.get("product_name", "")),
                    name=str(row.get("product_name", "")),
                    category=str(row.get("category", "")),
                    days_until_expiry=int(row.get("days_until_expiry", 0)),
                    price=float(row.get("price", 0)),
                    price_mrp=float(row.get("price", 0)),
                    discount=float(row.get("discount", 0)),
                    current_discount_percent=float(row.get("discount", 0)),
                    expiry_date="",
                    score=float(row.get("hybrid_score", row.get("recommendation_score", 0))),
                    is_dead_stock_risk=int(row.get("is_dead_stock_risk", 0)),
                )
                recommendations.append(recommendation)
            except Exception as row_error:
                logger.error(f"Error processing recommendation row: {row_error}")
                continue
        
        logger.info(f"Successfully generated {len(recommendations)} recommendations for user: {user_id}")
        return RecommendationsResponse(user_id=user_id, recommendations=recommendations)
        
    except Exception as e:
        logger.error(f"Error generating recommendations for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {str(e)}")

@app.get("/dead_stock_risk", response_model=List[DeadStockRiskItem])
def get_dead_stock_risk(category: Optional[str] = None):
    """Get items at risk of becoming dead stock"""
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    try:
        logger.info(f"Fetching dead stock risk items for category: {category}")
        df = system.products_df.copy()
        
        if category:
            df = df[df["category"] == category]
            
        at_risk = df[df["is_dead_stock_risk"] == 1]
        
        items = []
        for _, row in at_risk.iterrows():
            try:
                # Calculate risk score from the threshold calculator
                threshold = system.threshold_calculator.get_threshold(row['product_id'])
                days_left = row['days_until_expiry']
                risk_score = max(0, min(1, (threshold - days_left) / threshold)) if threshold > 0 else 0
                
                item = DeadStockRiskItem(
                    product_id=str(row.get("product_id", "")),
                    name=str(row.get("name", "")),
                    category=str(row.get("category", "")),
                    days_until_expiry=int(row.get("days_until_expiry", 0)),
                    current_discount_percent=float(row.get("current_discount_percent", 0)),
                    price_mrp=float(row.get("price_mrp", 0)),
                    inventory_quantity=int(row.get("inventory_quantity", 0)),
                    expiry_date=str(row.get("expiry_date", "")),
                    risk_score=risk_score,
                    threshold=threshold,
                )
                items.append(item)
            except Exception as row_error:
                logger.error(f"Error processing dead stock risk row: {row_error}")
                continue
        
        logger.info(f"Successfully fetched {len(items)} dead stock risk items")
        
        # Sort by days_until_expiry (ascending) so most urgent items appear first
        items_sorted = sorted(items, key=lambda x: x.days_until_expiry)
        
        return items_sorted
        
    except Exception as e:
        logger.error(f"Error fetching dead stock risk: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching dead stock risk: {str(e)}")

@app.get("/categories")
def get_categories():
    """Get all available product categories"""
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    try:
        categories = system.products_df["category"].unique().tolist()
        return {"categories": categories}
    except Exception as e:
        logger.error(f"Error fetching categories: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@app.get("/products", response_model=List[Product])
def get_products(
    category: Optional[str] = Query(None, description="Filter by category"),
    diet_type: Optional[str] = Query(None, description="Filter by diet type"),
    min_discount: Optional[float] = Query(None, ge=0, le=100, description="Minimum discount percentage"),
    max_days_until_expiry: Optional[int] = Query(None, ge=0, description="Maximum days until expiry")
):
    """Get all products with optional filters"""
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    try:
        logger.info("Fetching products with filters: " + 
                   f"category={category}, diet_type={diet_type}, " +
                   f"min_discount={min_discount}, max_days_until_expiry={max_days_until_expiry}")
        
        # Start with all products
        df = system.products_df.copy()
        
        # Apply filters
        if category:
            df = df[df["category"] == category]
        
        if diet_type:
            df = df[df["diet_type"] == diet_type]
        
        if min_discount is not None:
            df = df[df["current_discount_percent"] >= min_discount]
        
        if max_days_until_expiry is not None:
            df = df[df["days_until_expiry"] <= max_days_until_expiry]
        
        # Convert to Product models
        products = []
        for _, row in df.iterrows():
            try:
                # Handle allergens - could be a list or string
                allergens = row.get("allergens", [])
                if isinstance(allergens, str):
                    # If it's a comma-separated string, split it
                    allergens = [a.strip() for a in allergens.split(",")] if allergens else []
                elif not isinstance(allergens, list):
                    allergens = []
                
                product = Product(
                    product_id=str(row.get("product_id", "")),
                    name=str(row.get("name", "")),
                    category=str(row.get("category", "")),
                    brand=str(row.get("brand", "")),
                    diet_type=str(row.get("diet_type", "")),
                    allergens=allergens,
                    shelf_life_days=int(row.get("shelf_life_days", 0)),
                    packaging_date=str(row.get("packaging_date", "")),
                    expiry_date=str(row.get("expiry_date", "")),
                    days_until_expiry=int(row.get("days_until_expiry", 0)),
                    weight_grams=int(row.get("weight_grams", 0)),
                    price_mrp=float(row.get("price_mrp", 0)),
                    current_discount_percent=float(row.get("current_discount_percent", 0)),
                    inventory_quantity=int(row.get("inventory_quantity", 0)),
                    store_location_lat=float(row.get("store_location_lat", 0)),
                    store_location_lon=float(row.get("store_location_lon", 0)),
                    is_dead_stock_risk=int(row.get("is_dead_stock_risk", 0))
                )
                products.append(product)
            except Exception as row_error:
                logger.error(f"Error processing product row: {row_error}")
                continue
        
        logger.info(f"Successfully fetched {len(products)} products")
        
        # Sort by product_id for consistent ordering
        products_sorted = sorted(products, key=lambda x: x.product_id)
        
        return products_sorted
        
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching products: {str(e)}")
    
@app.get("/users")
def get_users():
    """Get all available users"""
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    
    try:
        users = []
        for _, row in system.users_df.iterrows():
            users.append({
                "id": str(row["user_id"]),
                "name": f"User {row['user_id']}",
                "diet_type": str(row["diet_type"]),
                "allergies": row.get("allergies", []),
                "prefers_discount": bool(row["prefers_discount"])
            })
        return {"users": users}
    except Exception as e:
        logger.error(f"Error fetching users: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching users: {str(e)}")

@app.post("/refresh_data")
def refresh_data():
    """Refresh data from Supabase"""
    global system
    
    try:
        # Fetch fresh data from Supabase
        users_response = supabase.table('users').select("*").execute()
        users_df = pd.DataFrame(users_response.data)
        
        products_response = supabase.table('products').select("*").execute()
        products_df = pd.DataFrame(products_response.data)
        products_df['packaging_date'] = pd.to_datetime(products_df['packaging_date'])
        products_df['expiry_date'] = pd.to_datetime(products_df['expiry_date'])
        
        transactions_response = supabase.table('transactions').select("*").execute()
        transactions_df = pd.DataFrame(transactions_response.data)
        transactions_df['purchase_date'] = pd.to_datetime(transactions_df['purchase_date'])
        
        # Reinitialize the system
        system = UnifiedRecommendationSystem(users_df, products_df, transactions_df)
        
        logger.info("Data refreshed successfully")
        return {"message": "Data refreshed successfully", "status": "success"}
        
    except Exception as e:
        logger.error(f"Error refreshing data: {e}")
        raise HTTPException(status_code=500, detail=f"Error refreshing data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True) 