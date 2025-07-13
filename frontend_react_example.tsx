// React Example - Using Waste Reduction API

import React, { useState, useEffect } from 'react';
import { WasteReductionAPI, Product, TransactionRequest, DynamicPricingResponse } from './frontend_types';

// Initialize API client
const api = new WasteReductionAPI('http://localhost:8000');

// Example 1: Product Listing Component
export const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: '',
    min_discount: 0,
    max_days_until_expiry: undefined as number | undefined
  });

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const data = await api.getProducts(filters);
      setProducts(data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Products</h2>
      
      {/* Filters */}
      <div>
        <select onChange={(e) => setFilters({...filters, category: e.target.value})}>
          <option value="">All Categories</option>
          <option value="Dairy">Dairy</option>
          <option value="Meat">Meat</option>
          <option value="Snacks">Snacks</option>
        </select>
        
        <input
          type="checkbox"
          onChange={(e) => setFilters({
            ...filters, 
            max_days_until_expiry: e.target.checked ? 7 : undefined
          })}
        /> Show Expiring Soon
      </div>

      {/* Product Grid */}
      {loading ? (
        <p>Loading...</p>
      ) : (
        <div className="product-grid">
          {products.map(product => (
            <ProductCard key={product.product_id} product={product} />
          ))}
        </div>
      )}
    </div>
  );
};

// Example 2: Product Card with Dynamic Pricing
export const ProductCard: React.FC<{ product: Product }> = ({ product }) => {
  const [dynamicPricing, setDynamicPricing] = useState<DynamicPricingResponse | null>(null);
  const [showPricing, setShowPricing] = useState(false);

  const checkDynamicPricing = async () => {
    try {
      const pricing = await api.getDynamicPricing(product.product_id);
      setDynamicPricing(pricing);
      setShowPricing(true);
    } catch (error) {
      console.error('Failed to get dynamic pricing:', error);
    }
  };

  const getUrgencyColor = (days: number) => {
    if (days <= 2) return '#ff0000'; // Red
    if (days <= 5) return '#ff8800'; // Orange
    if (days <= 10) return '#ffcc00'; // Yellow
    return '#00cc00'; // Green
  };

  return (
    <div className="product-card">
      <h3>{product.name}</h3>
      <p>{product.brand} • {product.category}</p>
      
      {/* Expiry Badge */}
      <div style={{ color: getUrgencyColor(product.days_until_expiry) }}>
        {product.days_until_expiry <= 0 
          ? 'EXPIRED' 
          : `${product.days_until_expiry} days until expiry`}
      </div>

      {/* Pricing */}
      <div>
        <span style={{ textDecoration: product.current_discount_percent > 0 ? 'line-through' : 'none' }}>
          ₹{product.price_mrp}
        </span>
        {product.current_discount_percent > 0 && (
          <span> ₹{(product.price_mrp * (1 - product.current_discount_percent / 100)).toFixed(2)}</span>
        )}
        {product.current_discount_percent > 0 && (
          <span className="discount-badge">{product.current_discount_percent}% OFF</span>
        )}
      </div>

      {/* Dead Stock Risk Badge */}
      {product.is_dead_stock_risk === 1 && (
        <div className="risk-badge">⚠️ At Risk</div>
      )}

      {/* Dynamic Pricing Check */}
      <button onClick={checkDynamicPricing}>Check Better Price</button>
      
      {showPricing && dynamicPricing && dynamicPricing.discount_increase > 0 && (
        <div className="dynamic-pricing-alert">
          <p>🎉 Better price available!</p>
          <p>New discount: {dynamicPricing.recommended_discount}%</p>
          <p>You save: ₹{dynamicPricing.savings.toFixed(2)}</p>
          <p style={{ fontSize: '0.8em', color: '#666' }}>{dynamicPricing.reasoning}</p>
        </div>
      )}

      <AddToCartButton product={product} />
    </div>
  );
};

// Example 3: Add to Cart with Transaction
export const AddToCartButton: React.FC<{ product: Product }> = ({ product }) => {
  const [quantity, setQuantity] = useState(1);
  const [loading, setLoading] = useState(false);

  const handlePurchase = async () => {
    try {
      setLoading(true);
      
      const transaction: TransactionRequest = {
        user_id: 'U0001', // Get from user context/auth
        product_id: product.product_id,
        quantity: quantity
      };

      // Create transaction with dynamic pricing (default)
      const result = await api.createTransaction(transaction);
      
      alert(`Purchase successful! 
        Total: ₹${result.total_price_paid}
        Discount: ${result.discount_percent}%
        ${result.message}`);
        
    } catch (error: any) {
      alert(`Purchase failed: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input
        type="number"
        min="1"
        max={product.inventory_quantity}
        value={quantity}
        onChange={(e) => setQuantity(parseInt(e.target.value))}
      />
      <button 
        onClick={handlePurchase} 
        disabled={loading || product.inventory_quantity === 0}
      >
        {loading ? 'Processing...' : 'Buy Now'}
      </button>
      <p style={{ fontSize: '0.8em' }}>Stock: {product.inventory_quantity}</p>
    </div>
  );
};

// Example 4: Personalized Recommendations
export const UserRecommendations: React.FC<{ userId: string }> = ({ userId }) => {
  const [recommendations, setRecommendations] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecommendations();
  }, [userId]);

  const fetchRecommendations = async () => {
    try {
      const data = await api.getRecommendations(userId, { n: 10 });
      setRecommendations(data.recommendations);
    } catch (error) {
      console.error('Failed to fetch recommendations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h2>Recommended for You</h2>
      {loading ? (
        <p>Loading recommendations...</p>
      ) : (
        <div className="recommendations-list">
          {recommendations.map(rec => (
            <div key={rec.product_id} className="recommendation-card">
              <h4>{rec.product_name}</h4>
              <p>{rec.category} • {rec.days_until_expiry} days left</p>
              <p>
                <span style={{ textDecoration: 'line-through' }}>₹{rec.price_mrp}</span>
                <span> ₹{rec.price.toFixed(2)}</span>
                <span className="discount">{rec.discount}% OFF</span>
              </p>
              <p>Match Score: {(rec.score * 100).toFixed(0)}%</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Example 5: Dead Stock Alert Dashboard
export const DeadStockDashboard: React.FC = () => {
  const [deadStockItems, setDeadStockItems] = useState<any[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('');

  useEffect(() => {
    fetchDeadStock();
  }, [selectedCategory]);

  const fetchDeadStock = async () => {
    try {
      const items = await api.getDeadStockRisk(selectedCategory || undefined);
      setDeadStockItems(items);
    } catch (error) {
      console.error('Failed to fetch dead stock:', error);
    }
  };

  return (
    <div>
      <h2>🚨 Dead Stock Risk Alert</h2>
      <p>{deadStockItems.length} items at risk</p>
      
      {deadStockItems.map(item => (
        <div key={item.product_id} className="dead-stock-item">
          <h4>{item.name}</h4>
          <div className="risk-metrics">
            <span>Expires in: {item.days_until_expiry} days</span>
            <span>Risk Score: {(item.risk_score * 100).toFixed(0)}%</span>
            <span>Stock: {item.inventory_quantity} units</span>
            <span>Current Discount: {item.current_discount_percent}%</span>
          </div>
        </div>
      ))}
    </div>
  );
}; 