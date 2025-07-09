import pickle
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import pandas as pd
import os

# Load the pickled model at startup
MODEL_PATH = os.path.join(os.path.dirname(__file__), 'model.pkl')
try:
    with open(MODEL_PATH, 'rb') as f:
        system = pickle.load(f)
except Exception as e:
    print(f"Failed to load model: {e}")
    system = None

app = FastAPI(title="Unified Waste Reduction API")

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for responses
class Recommendation(BaseModel):
    product_id: str
    product_name: str
    category: str
    days_until_expiry: int
    price: float
    discount: float
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
    risk_score: Optional[float] = None
    threshold: Optional[int] = None

@app.get("/recommendations/{user_id}", response_model=RecommendationsResponse)
def get_recommendations(user_id: str, n: int = Query(10, ge=1, le=50)):
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    try:
        recs = system.get_hybrid_recommendations(user_id, n_recommendations=n)
        if recs.empty:
            return {"user_id": user_id, "recommendations": []}
        # Convert DataFrame to list of Recommendation
        recommendations = [
            Recommendation(
                product_id=row.get("product_id", ""),
                product_name=row.get("product_name", row.get("name", "")),
                category=row.get("category", ""),
                days_until_expiry=int(row.get("days_until_expiry", 0)),
                price=float(row.get("price", row.get("price_mrp", 0))),
                discount=float(row.get("discount", row.get("current_discount_percent", 0))),
                score=float(row.get("hybrid_score", row.get("recommendation_score", 0))),
                is_dead_stock_risk=int(row.get("is_dead_stock_risk", 0)),
            )
            for _, row in recs.iterrows()
        ]
        return {"user_id": user_id, "recommendations": recommendations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendations: {e}")

@app.get("/dead_stock_risk", response_model=List[DeadStockRiskItem])
def get_dead_stock_risk(category: Optional[str] = None):
    if system is None:
        raise HTTPException(status_code=500, detail="Model not loaded.")
    try:
        df = system.products_df
        if category:
            df = df[df["category"] == category]
        at_risk = df[df["is_dead_stock_risk"] == 1]
        # Merge with product_risk_df to get threshold and risk_score
        merged = at_risk.merge(system.product_risk_df, on='product_id', how='left')
        items = [
            DeadStockRiskItem(
                product_id=row.get("product_id", ""),
                name=row.get("name", ""),
                category=row.get("category", ""),
                days_until_expiry=int(row.get("days_until_expiry", 0)),
                current_discount_percent=float(row.get("current_discount_percent", 0)),
                risk_score=row.get("risk_score", None),
                threshold=row.get("threshold", None),
            )
            for _, row in merged.iterrows()
        ]
        return items
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dead stock risk: {e}")

@app.get("/")
def root():
    return {"message": "Unified Waste Reduction System API is running."}