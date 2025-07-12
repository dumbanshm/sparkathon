# API Documentation Overview

This directory contains comprehensive API documentation for the Waste Reduction System API.

## Available Documentation

### 1. **api_specification.md**
A human-readable markdown file containing:
- Complete endpoint documentation
- Request/response examples
- Status codes and error handling
- Usage examples in multiple languages

### 2. **openapi_spec.yaml**
An OpenAPI 3.0 specification file that can be:
- Imported into API design tools (Swagger UI, Postman, Insomnia)
- Used for API code generation
- Used for automated API testing
- Viewed at `http://localhost:8000/docs` when the server is running

### 3. **waste_reduction_api.postman_collection.json**
A Postman collection containing:
- Pre-configured requests for all endpoints
- Environment variables for easy base URL switching
- Example requests with different parameters

## Quick Start

### Using the Live Documentation
1. Start the backend server:
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. Access the interactive documentation:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Using Postman
1. Open Postman
2. Click "Import" → Select `waste_reduction_api.postman_collection.json`
3. Update the `base_url` variable in the collection settings if needed
4. Start making API requests!

### Testing the API
```bash
# Quick health check
curl http://localhost:8000/health

# Get recommendations for a user
curl http://localhost:8000/recommendations/U0001?n=5

# Get all categories
curl http://localhost:8000/categories
```

## API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Check API and model status |
| `/users` | GET | Get all users with dietary preferences |
| `/categories` | GET | Get all product categories |
| `/recommendations/{user_id}` | GET | Get personalized recommendations |
| `/dead_stock_risk` | GET | Get products at risk of expiry |

## Environment Variables

When using in different environments, update the base URL:
- Local: `http://localhost:8000`
- Gitpod: `https://8000-{workspace-id}.{region}.gitpod.io`
- Production: Your production API URL 