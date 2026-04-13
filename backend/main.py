import os
import re
import requests
from typing import List

from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from auth import router as auth_router, get_current_user

load_dotenv()

app = FastAPI(title="Tol Mol Ke Bol - Grocery Price Comparison API")

# ── CORS ────────────────────────────────────────────────
# In production, FRONTEND_URL should be set to the Vercel domain.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

origins = [
    FRONTEND_URL,
    "http://localhost:5173",
    "http://localhost:5500",
    "http://localhost:5501",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5500",
    "http://127.0.0.1:5501",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register auth routes ────────────────────────────────
app.include_router(auth_router)

# ── Config ──────────────────────────────────────────────
SERPAPI_KEY = os.getenv("SERPAPI_API_KEY", "")

TARGET_STORES = ["amazon", "flipkart", "bigbasket", "blinkit", "instamart", "swiggy"]

# ── Affiliate deep-link helpers ─────────────────────────
# These base URLs are used ONLY for mock data (when no SerpAPI key is set).
# For real SerpAPI results, the actual product URL from Google Shopping is used.
# The Cuelinks script in the frontend auto-converts all outbound store links
# to affiliate tracking links, so commissions are still earned.
AFFILIATE_SEARCH_URLS = {
    "amazon": "https://amzn.urlvia.com/sUmji8",
    "flipkart": "https://fktr.in/vrYP4jp",
    "bigbasket": "https://inr.deals/KQ7GIn",
    "blinkit": "https://inr.deals/LZkjaN",
    "instamart": "https://inr.deals/KMi0yI",
}


class Product(BaseModel):
    title: str
    price: float
    store: str
    image: str
    link: str


# ── Mock data fallback ──────────────────────────────────
def fetch_mock_data(query: str) -> List[dict]:
    """Return mock products with search URLs that go to query-specific results."""
    q = requests.utils.requote_uri(query)
    return [
        {
            "title": f"{query} - 1kg Premium Pack",
            "price": 120.50,
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
            "link": f"https://www.amazon.in/s?k={q}",
        },
        {
            "title": f"{query} Fresh Organic",
            "price": 115.00,
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=300&h=300&fit=crop",
            "link": f"https://www.flipkart.com/search?q={q}",
        },
        {
            "title": f"{query} - Economy 500g",
            "price": 89.00,
            "store": "BigBasket",
            "image": "https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=300&h=300&fit=crop",
            "link": f"https://www.bigbasket.com/ps/?q={q}",
        },
        {
            "title": f"{query} Gold Premium 2kg",
            "price": 245.00,
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1590779033100-9f60a05a013d?w=300&h=300&fit=crop",
            "link": f"https://www.amazon.in/s?k={q}",
        },
        {
            "title": f"{query} Organic Special",
            "price": 175.00,
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=300&h=300&fit=crop",
            "link": f"https://www.flipkart.com/search?q={q}",
        },
        {
            "title": f"{query} Quick Delivery",
            "price": 99.00,
            "store": "Blinkit",
            "image": "https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=300&h=300&fit=crop",
            "link": f"https://blinkit.com/s/?q={q}",
        },
        {
            "title": f"{query} Express Delivery",
            "price": 110.00,
            "store": "Swiggy Instamart",
            "image": "https://images.unsplash.com/photo-1579113800032-c38bd7635818?w=300&h=300&fit=crop",
            "link": f"https://www.swiggy.com/instamart/search?q={q}",
        },
    ]


# ── Routes ──────────────────────────────────────────────
@app.get("/")
def health_check():
    return {"status": "ok", "service": "Tol Mol Ke Bol API"}


@app.get("/search", response_model=List[Product])
def search_groceries(q: str = Query(..., description="Query for groceries")):
    if not SERPAPI_KEY:
        results = fetch_mock_data(q)
    else:
        params = {
            "engine": "google_shopping",
            "q": q,
            "api_key": SERPAPI_KEY,
            "gl": "in",
            "hl": "en",
        }
        res = requests.get("https://serpapi.com/search", params=params)

        if res.status_code != 200:
            return []

        data = res.json()
        shopping_results = data.get("shopping_results", [])

        results = []
        for item in shopping_results:
            source = item.get("source", "").lower()
            if any(store in source for store in TARGET_STORES):
                price_str = item.get("price", "0")
                price_clean = re.sub(r"[^\d.]", "", price_str)
                try:
                    price_val = float(price_clean) if price_clean else 0.0
                except ValueError:
                    price_val = 0.0

                # Always construct a direct store search URL using the product title
                # so "Buy Now" goes straight to the store with that specific product
                product_title = requests.utils.requote_uri(item.get("title", q))
                store_name = item.get("source", "").lower()
                if "amazon" in store_name:
                    product_link = f"https://www.amazon.in/s?k={product_title}"
                elif "flipkart" in store_name:
                    product_link = f"https://www.flipkart.com/search?q={product_title}"
                elif "bigbasket" in store_name:
                    product_link = f"https://www.bigbasket.com/ps/?q={product_title}"
                elif "blinkit" in store_name:
                    product_link = f"https://blinkit.com/s/?q={product_title}"
                elif "instamart" in store_name or "swiggy" in store_name:
                    product_link = f"https://www.swiggy.com/instamart/search?q={product_title}"
                else:
                    product_link = item.get("link", "")

                results.append(
                    {
                        "title": item.get("title", ""),
                        "price": price_val,
                        "store": item.get("source", ""),
                        "image": item.get("thumbnail", ""),
                        "link": product_link,
                    }
                )

    results = sorted(results, key=lambda x: x["price"])
    return results
