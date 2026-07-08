# Tol Mol Ke Bol — Grocery Price Comparison

A full-stack grocery price comparison platform that searches and compares prices across **Amazon**, **Flipkart**, **BigBasket**, **Blinkit**, and **Instamart** — so users find the lowest price and you earn affiliate commissions.

## What This Project Does

1. User searches for a grocery item (e.g., "Basmati Rice 1kg")
2. Backend queries SerpAPI's Google Shopping engine for Indian grocery results
3. Results are filtered to only show your target stores
4. Products are sorted by price (cheapest first, highlighted with "Lowest Price")
5. User clicks "Buy Now" → redirected to the store's search page for that product
6. Cuelinks auto-converts the link to an affiliate link → you earn commission

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | React 19 + Vite 8 | SPA with client-side routing |
| HTTP Client | Axios | JWT-aware API calls with request cancellation |
| Backend | FastAPI (Python) | Async API server |
| Database | MongoDB Atlas | User auth + search result caching (1hr TTL) |
| External API | SerpAPI (Google Shopping) | Product data and prices |
| Auth | JWT (python-jose + bcrypt) | Secure signup/login |
| Monetization | Cuelinks | Auto-converts outbound links to affiliate links |
| Deployment | Vercel (frontend) + Render (backend) | Free tier hosting |

## Features

- **Price Comparison** — Search across 5 stores simultaneously
- **Lowest Price Highlight** — Cheapest product is always visually marked
- **Accurate Pricing** — Uses SerpAPI's `extracted_price` field for correct numeric prices
- **Store-Specific Links** — "Buy Now" redirects to the actual store's search page
- **Search Caching** — MongoDB caches results for 1 hour (instant repeat searches)
- **Async Backend** — Non-blocking httpx client (no thread starvation)
- **Request Cancellation** — Frontend AbortController cancels stale searches
- **JWT Authentication** — Secure signup, login, and protected routes
- **Responsive Design** — Works on mobile, tablet, and desktop
- **Affiliate Monetization** — Cuelinks auto-converts outbound links

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI app, /search endpoint, SerpAPI integration
│   ├── auth.py              # JWT signup/login/me routes
│   ├── database.py          # MongoDB connection, collections, index init
│   ├── requirements.txt     # Pinned Python dependencies
│   └── .env.example         # Template for environment variables
├── frontend/
│   ├── src/
│   │   ├── api.js           # Axios instance with JWT interceptor
│   │   ├── context/AuthContext.jsx  # Auth state management
│   │   ├── components/
│   │   │   ├── Navbar.jsx   # Navigation with auth-aware links
│   │   │   └── ProductCard.jsx  # Product card with price + Buy Now
│   │   ├── pages/
│   │   │   ├── Home.jsx     # Search UI + product grid
│   │   │   ├── Login.jsx    # Login form
│   │   │   └── Signup.jsx   # Signup form
│   │   ├── App.jsx          # Router + layout
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Full design system
│   ├── index.html           # Cuelinks affiliate script
│   ├── vercel.json          # SPA rewrite + security headers
│   └── package.json
├── .gitignore
└── README.md
```

## How Search Works

### Data Flow

```
User submits query
  → Frontend sends GET /search?q=basmati+rice
  → Backend checks MongoDB search_cache (1hr TTL)
  → If cache miss: calls SerpAPI Google Shopping (gl=in, hl=en)
  → Filters results to target stores only
  → Uses extracted_price (numeric) for accurate pricing
  → Builds clean store search URLs with trimmed product titles
  → Deduplicates results by title + store
  → Returns sorted list (cheapest first)
  → Caches results in MongoDB for future requests
```

### Price Extraction

SerpAPI returns two price fields:
- `price` — string like `"₹120"` or `"₹120 - ₹150"` (used for display)
- `extracted_price` — clean float like `120` (used for sorting and comparison)

The backend uses `extracted_price` as the source of truth. This avoids regex parsing errors on price ranges, unusual formatting, or missing currency symbols.

### Store Links

SerpAPI's `shopping_results` does not include direct store URLs. The backend:
1. Checks `inline_shopping_results` for direct store links (sponsored listings)
2. Falls back to constructing store search URLs with a cleaned product title
3. Strips noise from titles ("Pack of 2", "Best Seller", "Free Delivery", etc.)

### Caching

- First search for a query hits SerpAPI (~2s)
- Results cached in MongoDB `search_cache` collection with 1-hour TTL
- Repeat searches return instantly (~10ms)
- Drop cache: `db.search_cache.drop()`

## How Affiliate Monetization Works

### Cuelinks Integration

The `index.html` loads the Cuelinks JavaScript snippet:

```html
<script type="text/javascript">
    var cuelinks = { key: 'YOUR_PUBLISHER_KEY' };
    (function(d, t) {
        var s = d.createElement(t);
        s.type = 'text/javascript';
        s.async = true;
        s.src = '//cdn-widget.cuelinks.com/js/cuelinks.js';
        var r = d.getElementsByTagName(t)[0];
        r.parentNode.insertBefore(s, r);
    }(document, 'script'));
</script>
```

When a user clicks "Buy Now", Cuelinks:
1. Intercepts the outbound link click
2. Converts the regular store URL into an affiliate tracking URL
3. Redirects the user through the tracking link to the store
4. Sets a cookie (typically 24 hours) for that store

### Earning Commission

- User clicks "Buy Now" → Cuelinks sets a store cookie
- User buys **anything** from that store within 24 hours → you earn commission
- Commission rates vary by category (typically 5-12% for Amazon, 2-12% for Flipkart)

### Getting Your Publisher Key

1. Sign up at [Cuelinks](https://www.cuelinks.com)
2. Go to **Account > My Profile** in the dashboard
3. Copy your Publisher Key
4. Replace `'YOUR_PUBLISHER_KEY'` in `frontend/index.html`

> **Note:** The publisher key is different from the API key. The API key requires earning 10,000+/month and is only for programmatic access.

## Local Development

### Prerequisites

- Python 3.10+
- Node.js 18+
- MongoDB Atlas account (free tier works)
- SerpAPI account (optional — mock data fallback available)

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create `backend/.env`:

```env
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/<db>?retryWrites=true&w=majority
JWT_SECRET=<generate-a-random-64-char-hex-string>
SERPAPI_API_KEY=              # Optional — falls back to mock data if empty
FRONTEND_URL=http://localhost:5173
ENVIRONMENT=development
```

Start the server:

```bash
uvicorn main:app --reload
```

Backend runs at `http://127.0.0.1:8000`. Swagger UI at `/docs`.

### Frontend

```bash
cd frontend
npm install
```

Create `frontend/.env.local`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the dev server:

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`.

## Deployment

### Backend → Render

1. Go to [render.com](https://render.com) → **New Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app -w 2 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. Set environment variables:

| Key | Value |
|-----|-------|
| `MONGODB_URI` | Your MongoDB Atlas connection string |
| `JWT_SECRET` | A strong random secret (64+ chars) |
| `SERPAPI_API_KEY` | Your SerpAPI key |
| `FRONTEND_URL` | Your Vercel URL (e.g., `https://tol-mol-ke-bol.vercel.app`) |
| `ENVIRONMENT` | `production` |

> **Note:** Use `-w 2` workers for Render free tier (512MB RAM). More workers will cause OOM kills.

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → Import from GitHub
2. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
3. Set environment variables:

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | Your Render URL (e.g., `https://tol-mol-ke-bol.onrender.com`) |

### MongoDB Atlas

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. **Network Access** → Add IP `0.0.0.0/0` (allow from anywhere for Render)
3. **Database Access** → Create a user with read/write permissions
4. Copy the connection string into `MONGODB_URI`
5. The backend auto-creates indexes on startup (unique email, search cache TTL)

## Environment Variables

### Backend

| Variable | Required | Description |
|----------|----------|-------------|
| `MONGODB_URI` | Yes | MongoDB Atlas connection string |
| `JWT_SECRET` | Yes | Secret key for signing JWT tokens (64+ char hex string) |
| `SERPAPI_API_KEY` | No | SerpAPI key (falls back to mock data if empty) |
| `FRONTEND_URL` | Yes | Frontend URL for CORS (e.g., `https://tol-mol-ke-bol.vercel.app`) |
| `ENVIRONMENT` | No | `production` or `development` (default: `development`) |
| `DB_NAME` | No | MongoDB database name (default: `tol_mol_ke_bol`) |

### Frontend

| Variable | Required | Description |
|----------|----------|-------------|
| `VITE_API_BASE_URL` | Yes | Backend API URL (e.g., `https://tol-mol-ke-bol.onrender.com`) |

## API Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | No | Health check |
| GET | `/search?q=rice` | No | Search & compare prices (max 200 chars) |
| POST | `/api/auth/signup` | No | Create account (name, email, password) |
| POST | `/api/auth/login` | No | Log in, returns JWT + user info |
| GET | `/api/auth/me` | Yes | Get current user profile |

## Security Measures

- **JWT Secret Validation** — Backend crashes on startup if `JWT_SECRET` is missing or is the default value
- **Email Uniqueness** — MongoDB unique index on `users.email` prevents duplicate accounts
- **Query Length Limit** — Search queries capped at 200 characters
- **CORS Restrictions** — Only allows the configured `FRONTEND_URL` in production
- **Security Headers** — Vercel config sets `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`
- **Request Cancellation** — Frontend cancels stale requests to prevent race conditions
- **Error Handling** — SerpAPI network errors return empty results instead of crashing

## Performance Optimizations

| Optimization | Before | After |
|-------------|--------|-------|
| SerpAPI call | Blocking `requests.get()` | Async `httpx.AsyncClient` |
| Repeat searches | ~2s (fresh API call) | ~10ms (MongoDB cache) |
| Stale requests | Both resolve, last wins | AbortController cancels old |
| Price parsing | Regex on string `price` | Direct `extracted_price` float |
| Product titles | Full SEO spam in URLs | Clean noise-stripped queries |
| React keys | Array index (unstable) | `store-title-index` (stable) |
| datetime | Deprecated `utcnow()` | `datetime.now(timezone.utc)` |

## Known Limitations

- **SerpAPI Coverage** — Quick commerce platforms (Blinkit, Zepto, Instamart) have limited Google Shopping catalog in India. Some searches may not return results for all stores.
- **Search URLs, Not Product URLs** — "Buy Now" redirects to the store's search page with a cleaned query, not the exact product page. This is because SerpAPI does not provide direct store product URLs.
- **Cuelinks Cookie Duration** — Affiliate cookies last ~24 hours. If a user returns after that, no commission is earned.
- **Rate Limits** — SerpAPI has usage limits. No rate limiting is implemented on the backend yet.
- **No Email Validation** — Signup accepts any string as email (no server-side format validation).

## License

This project is for personal use.
