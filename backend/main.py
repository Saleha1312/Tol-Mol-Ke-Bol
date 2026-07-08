import os
import re
import asyncio
from urllib.parse import quote, urlparse
from typing import List, Optional
from datetime import datetime, timezone

import httpx
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

from auth import router as auth_router, get_current_user
from database import search_cache, init_indexes

load_dotenv()

app = FastAPI(title="Tol Mol Ke Bol - Grocery Price Comparison API")


@app.on_event("startup")
async def startup():
    await init_indexes()

# ── CORS ────────────────────────────────────────────────
# In production, FRONTEND_URL should be set to the Vercel domain.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

if ENVIRONMENT == "production":
    origins = [FRONTEND_URL]
else:
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

# Noise words to strip from product titles for cleaner store search queries
NOISE_PATTERN = re.compile(
    r"\b("
    r"(?:Pack\s*of\s*\d+|Combo|Set\s*of\s*\d+|Assorted|Variant|Random)"
    r"|(?:Free\s*(?:Delivery|Shipping|Sample))"
    r"|(?:Best\s*Seller|Top\s*Rated|Trending|Popular|Recommended)"
    r"|(?:Limited\s*Edition|Exclusive|Special\s*Offer|Deal\s*of)"
    r"|(?:Inclusive\s*of\s*all\s*taxes|inc\.\s*tax|incl\.\s*tax)"
    r"|(?:MRP\s*:?\s*₹?[\d,.]+)"
    r")\s*",
    re.IGNORECASE,
)

# Store-specific search URL templates
STORE_URLS = {
    "amazon": "https://www.amazon.in/s?k={q}",
    "flipkart": "https://www.flipkart.com/search?q={q}",
    "bigbasket": "https://www.bigbasket.com/ps/?q={q}",
    "blinkit": "https://blinkit.com/s/?q={q}",
    "instamart": "https://www.swiggy.com/instamart/search?q={q}",
    "swiggy": "https://www.swiggy.com/instamart/search?q={q}",
}


def clean_product_title(title: str) -> str:
    """Strip noise from SerpAPI product titles to get a clean search query."""
    cleaned = NOISE_PATTERN.sub("", title)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    if len(cleaned) > 60:
        cleaned = cleaned[:60].rsplit(" ", 1)[0]
    return cleaned


def build_store_link(source: str, title: str, original_link: str) -> str:
    """Build a direct search URL for the store, using a cleaned product title."""
    source_lower = source.lower()
    for store_key, url_template in STORE_URLS.items():
        if store_key in source_lower:
            query = clean_product_title(title)
            return url_template.format(q=quote(query))
    return original_link or ""


def detect_store(title: str, source: str) -> Optional[str]:
    """Detect which target store a product belongs to."""
    combined = f"{title} {source}".lower()
    for store in TARGET_STORES:
        if store in combined:
            return store
    return None


class Product(BaseModel):
    title: str
    price: float
    price_display: str
    store: str
    image: str
    link: str


# ── Mock data fallback ──────────────────────────────────
def fetch_mock_data(query: str) -> List[dict]:
    """Return mock products with search URLs that go to query-specific results."""
    q = quote(query)
    return [
        {
            "title": f"{query} - 1kg Premium Pack",
            "price": 120.50,
            "price_display": "₹120.50",
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop",
            "link": f"https://www.amazon.in/s?k={q}",
        },
        {
            "title": f"{query} Fresh Organic",
            "price": 115.00,
            "price_display": "₹115.00",
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1596040033229-a9821ebd058d?w=300&h=300&fit=crop",
            "link": f"https://www.flipkart.com/search?q={q}",
        },
        {
            "title": f"{query} - Economy 500g",
            "price": 89.00,
            "price_display": "₹89.00",
            "store": "BigBasket",
            "image": "https://images.unsplash.com/photo-1559181567-c3190ca9959b?w=300&h=300&fit=crop",
            "link": f"https://www.bigbasket.com/ps/?q={q}",
        },
        {
            "title": f"{query} Gold Premium 2kg",
            "price": 245.00,
            "price_display": "₹245.00",
            "store": "Amazon.in",
            "image": "https://images.unsplash.com/photo-1590779033100-9f60a05a013d?w=300&h=300&fit=crop",
            "link": f"https://www.amazon.in/s?k={q}",
        },
        {
            "title": f"{query} Organic Special",
            "price": 175.00,
            "price_display": "₹175.00",
            "store": "Flipkart",
            "image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?w=300&h=300&fit=crop",
            "link": f"https://www.flipkart.com/search?q={q}",
        },
        {
            "title": f"{query} Quick Delivery",
            "price": 99.00,
            "price_display": "₹99.00",
            "store": "Blinkit",
            "image": "https://images.unsplash.com/photo-1604719312566-8912e9227c6a?w=300&h=300&fit=crop",
            "link": f"https://blinkit.com/s/?q={q}",
        },
        {
            "title": f"{query} Express Delivery",
            "price": 110.00,
            "price_display": "₹110.00",
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
async def search_groceries(q: str = Query(..., min_length=1, max_length=200, description="Query for groceries")):
    q = q.strip()
    if not SERPAPI_KEY:
        results = fetch_mock_data(q)
    else:
        cached = await search_cache.find_one({"query": q})
        if cached:
            results = cached["results"]
        else:
            params = {
                "engine": "google_shopping",
                "q": q,
                "api_key": SERPAPI_KEY,
                "gl": "in",
                "hl": "en",
            }
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    res = await client.get("https://serpapi.com/search", params=params)
            except (httpx.ConnectError, httpx.TimeoutException):
                return []

            if res.status_code != 200:
                return []

            data = res.json()
            shopping_results = data.get("shopping_results", [])
            inline_results = data.get("inline_shopping_results", [])

            # Build a map of direct links from inline results (these have actual store URLs)
            direct_links = {}
            for item in inline_results:
                link = item.get("link", "")
                if not link:
                    continue
                parsed = urlparse(link)
                hostname = parsed.hostname or ""
                for store in TARGET_STORES:
                    if store in hostname:
                        direct_links[store] = link
                        break

            seen = set()
            results = []

            for item in shopping_results:
                title = item.get("title", "")
                source = item.get("source", "")

                store = detect_store(title, source)
                if not store:
                    continue

                price_val = item.get("extracted_price")
                if price_val is None:
                    price_str = item.get("price", "")
                    price_clean = re.sub(r"[^\d.]", "", price_str)
                    try:
                        price_val = float(price_clean) if price_clean else 0.0
                    except ValueError:
                        price_val = 0.0

                if price_val <= 0:
                    continue

                # Deduplicate by title + store
                dedup_key = f"{title.lower()}_{store}"
                if dedup_key in seen:
                    continue
                seen.add(dedup_key)

                # Use direct link if available, otherwise build store search URL
                product_link = direct_links.get(store, "")
                if not product_link:
                    product_link = build_store_link(source, title, item.get("product_link", ""))

                price_display = item.get("price", f"₹{price_val:.2f}")

                results.append(
                    {
                        "title": title,
                        "price": float(price_val),
                        "price_display": price_display,
                        "store": source,
                        "image": item.get("thumbnail", ""),
                        "link": product_link,
                    }
                )

            await search_cache.update_one(
                {"query": q},
                {"$set": {"results": results, "cached_at": datetime.now(timezone.utc)}},
                upsert=True,
            )

    results = sorted(results, key=lambda x: x["price"])
    return results


# ── Price verification (scrape actual store pages) ──────

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
    "Accept-Encoding": "gzip, deflate",
}

# Regex patterns to extract prices from store HTML pages
PRICE_PATTERNS = {
    "amazon": [
        re.compile(r'"price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'class="a-price-whole"[^>]*>([\d,]+)'),
        re.compile(r'id="priceblock_ourprice"[^>]*>.*?(\d[\d,]*\.?\d*)', re.DOTALL),
        re.compile(r'"priceAmount"\s*:\s*([\d,.]+)'),
    ],
    "flipkart": [
        re.compile(r'"price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'class="_30jeq3"[^>]*>.*?(\d[\d,]*\.?\d*)', re.DOTALL),
        re.compile(r'class="_16FRkO"[^>]*>.*?(\d[\d,]*\.?\d*)', re.DOTALL),
    ],
    "bigbasket": [
        re.compile(r'"price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'"selling_price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'class="[^"]*price[^"]*"[^>]*>.*?(\d[\d,]*\.?\d*)', re.DOTALL | re.IGNORECASE),
    ],
    "blinkit": [
        re.compile(r'"price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'"finalPrice"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'"mrp"\s*:\s*"?([\d,]+\.?\d*)"?'),
    ],
    "instamart": [
        re.compile(r'"price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'"mrp"\s*:\s*"?([\d,]+\.?\d*)"?'),
    ],
    "swiggy": [
        re.compile(r'"price"\s*:\s*"?([\d,]+\.?\d*)"?'),
        re.compile(r'"mrp"\s*:\s*"?([\d,]+\.?\d*)"?'),
    ],
}


def extract_store_from_url(url: str) -> Optional[str]:
    """Detect which store a URL belongs to."""
    hostname = urlparse(url).hostname or ""
    hostname = hostname.lower()
    for store in TARGET_STORES:
        if store in hostname:
            return store
    return None


def extract_price_from_html(html: str, store: str) -> Optional[float]:
    """Extract price from store HTML using store-specific regex patterns."""
    patterns = PRICE_PATTERNS.get(store, [])
    for pattern in patterns:
        match = pattern.search(html)
        if match:
            price_str = match.group(1).replace(",", "")
            try:
                price = float(price_str)
                if 1 < price < 100000:
                    return price
            except ValueError:
                continue
    return None


async def fetch_store_price(client: httpx.AsyncClient, url: str) -> Optional[float]:
    """Fetch a store page and extract the price."""
    store = extract_store_from_url(url)
    if not store:
        return None
    try:
        res = await client.get(url, headers=HEADERS, follow_redirects=True, timeout=10.0)
        if res.status_code == 200:
            return extract_price_from_html(res.text, store)
    except (httpx.ConnectError, httpx.TimeoutException, Exception):
        pass
    return None


class VerifyRequest(BaseModel):
    products: List[dict]


class VerifiedProduct(BaseModel):
    index: int
    price: float
    price_display: str
    verified: bool


@app.post("/verify-prices", response_model=List[VerifiedProduct])
async def verify_prices(req: VerifyRequest):
    """Fetch actual store pages in parallel and extract real prices."""
    async with httpx.AsyncClient(timeout=12.0) as client:
        tasks = []
        indices = []
        for i, product in enumerate(req.products):
            link = product.get("link", "")
            if link:
                tasks.append(fetch_store_price(client, link))
                indices.append(i)

        results = await asyncio.gather(*tasks, return_exceptions=True)

    verified = []
    for i, price in zip(indices, results):
        if isinstance(price, Exception) or price is None:
            continue
        verified.append(
            VerifiedProduct(
                index=i,
                price=price,
                price_display=f"₹{price:.2f}",
                verified=True,
            )
        )
    return verified
