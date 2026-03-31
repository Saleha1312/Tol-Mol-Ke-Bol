import os
import requests
import re
from typing import List
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Tol Mol Ke Bol - Grocery Price Comparison API")

# Allow requests from frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SERPAPI_KEY = os.getenv("SERPAPI_API_KEY", "")

class Product(BaseModel):
    title: str
    price: float
    store: str
    image: str
    link: str

TARGET_STORES = ["amazon", "flipkart", "jiomart"]

def fetch_mock_data(query: str) -> List[dict]:
    return [
        {
            "title": f"[Amazon] {query} - 1kg Premium Pack",
            "price": 120.50,
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
            "link": "https://www.amazon.in/s?k=" + query
        },
        {
            "title": f"[Flipkart] {query} Fresh Organic",
            "price": 115.00,
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=300&h=300&fit=crop",
            "link": "https://www.flipkart.com/search?q=" + query
        },
        {
            "title": f"[JioMart] {query} Saver Pack",
            "price": 105.00,
            "store": "JioMart",
            "image": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=300&h=300&fit=crop",
            "link": "https://www.jiomart.com/catalogsearch/result?q=" + query
        }
    ]

@app.get("/search", response_model=List[Product])
def search_groceries(q: str = Query(..., description="Query for groceries")):
    if not SERPAPI_KEY:
        # Fallback to mock data if no key provided
        results = fetch_mock_data(q)
    else:
        params = {
            "engine": "google_shopping",
            "q": q,
            "api_key": SERPAPI_KEY,
            "gl": "in",  # India
            "hl": "en"
        }
        res = requests.get("https://serpapi.com/search", params=params)
        
        if res.status_code != 200:
            return []
            
        data = res.json()
        shopping_results = data.get("shopping_results", [])
        
        results = []
        for item in shopping_results:
            source = item.get("source", "").lower()
            
            # Filter only target stores
            if any(store in source for store in TARGET_STORES):
                # Extract numeric price
                price_str = item.get("price", "0")
                price_clean = re.sub(r'[^\d.]', '', price_str)
                try:
                    price_val = float(price_clean) if price_clean else 0.0
                except ValueError:
                    price_val = 0.0
                
                results.append({
                    "title": item.get("title", ""),
                    "price": price_val,
                    "store": item.get("source", ""),
                    "image": item.get("thumbnail", ""),
                    "link": item.get("link", "")
                })
    
    # Sort by price ascending
    results = sorted(results, key=lambda x: x["price"])
    return results
