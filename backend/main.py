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

TARGET_STORES = ["amazon", "flipkart", "jiomart"]

# ── Affiliate Links ─────────────────────────────────────
AFFILIATE_LINKS = {
    "amazon": "https://amzn.urlvia.com/sUmji8",
    "jiomart": "https://inr.deals/ydznav",
}


def get_affiliate_link(store: str, original_link: str) -> str:
    """Replace product link with affiliate link if available for the store."""
    store_lower = store.lower()
    for key, affiliate_url in AFFILIATE_LINKS.items():
        if key in store_lower:
            return affiliate_url
    return original_link


class Product(BaseModel):
    title: str
    price: float
    store: str
    image: str
    link: str


# ── Mock data fallback ──────────────────────────────────
def fetch_mock_data(query: str) -> List[dict]:
    return [
        {
            "title": f"{query} - 1kg Premium Pack",
            "price": 120.50,
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
            "link": AFFILIATE_LINKS["amazon"],
        },
        {
            "title": f"{query} Fresh Organic",
            "price": 115.00,
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=300&h=300&fit=crop",
            "link": "https://www.flipkart.com/search?q=" + query,
        },
        {
            "title": f"{query} Saver Pack",
            "price": 105.00,
            "store": "JioMart",
            "image": "https://images.unsplash.com/photo-1608686207856-001b95cf60ca?w=300&h=300&fit=crop",
            "link": AFFILIATE_LINKS["jiomart"],
        },
        {
            "title": f"{query} - Economy 500g",
            "price": 89.00,
            "store": "JioMart",
            "image": "https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=300&h=300&fit=crop",
            "link": AFFILIATE_LINKS["jiomart"],
        },
        {
            "title": f"{query} Gold Premium 2kg",
            "price": 245.00,
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1590779033100-9f60a05a013d?w=300&h=300&fit=crop",
            "link": AFFILIATE_LINKS["amazon"],
        },
        {
            "title": f"{query} Organic Special",
            "price": 175.00,
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=300&h=300&fit=crop",
            "link": "https://www.flipkart.com/search?q=" + query,
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

                store_name = item.get("source", "")
                original_link = item.get("link", "")
                results.append(
                    {
                        "title": item.get("title", ""),
                        "price": price_val,
                        "store": store_name,
                        "image": item.get("thumbnail", ""),
                        "link": get_affiliate_link(store_name, original_link),
                    }
                )

    results = sorted(results, key=lambda x: x["price"])
    return results
