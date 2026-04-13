# 🛒 Tol Mol Ke Bol — Grocery Price Comparison

A full-stack grocery price comparison platform that lets users search and compare prices across **Amazon**, **Flipkart**, and others — and earn affiliate commissions while doing it.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React + Vite |
| Backend | FastAPI (Python) |
| Database | MongoDB Atlas |
| Auth | JWT (python-jose + bcrypt) |
| Deployment | Vercel (frontend) + Render (backend) |
| Monetization | Cuelinks affiliate script |

## Project Structure

```
├── backend/
│   ├── main.py              # FastAPI server + /search endpoint
│   ├── auth.py              # JWT signup/login/me routes
│   ├── database.py          # MongoDB Atlas connection (Motor)
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── api.js           # Axios instance with JWT injection
│   │   ├── context/AuthContext.jsx
│   │   ├── components/Navbar.jsx
│   │   ├── components/ProductCard.jsx
│   │   ├── pages/Home.jsx
│   │   ├── pages/Login.jsx
│   │   ├── pages/Signup.jsx
│   │   ├── App.jsx          # Router
│   │   ├── main.jsx         # Entry point
│   │   └── index.css        # Full design system
│   ├── index.html
│   ├── vercel.json          # SPA rewrite rules
│   └── package.json
├── .gitignore
└── README.md
```

## Features

-  **Price Comparison** — Search across Amazon, Flipkart, and more simultaneously
-  **Lowest Price Highlight** — Cheapest product is always visually marked
-  **JWT Authentication** — Secure signup, login, and protected routes
-  **Responsive Design** — Works beautifully on mobile, tablet, and desktop
-  **Affiliate Monetization** — Cuelinks auto-converts outbound links
-  **Production Ready** — Deployed on Vercel + Render

---

## Local Development

### Backend

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file inside `backend/`:

```env
MONGODB_URI=mongodb+srv://<user>:<pass>@<cluster>.mongodb.net/<db>?retryWrites=true&w=majority
JWT_SECRET=your-super-secret-key-here
SERPAPI_API_KEY=             # Optional — falls back to mock data
FRONTEND_URL=http://localhost:5173
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

Create a `.env.local` file inside `frontend/`:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Start the dev server:

```bash
npm run dev
```

Frontend runs at `http://localhost:5173`.

---

## Deployment

### Backend → Render

1. Go to [render.com](https://render.com) → **New Web Service**
2. Connect your GitHub repo
3. Settings:
   - **Root Directory:** `backend`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT`
4. Environment Variables:

| Key | Value |
|-----|-------|
| `MONGODB_URI` | Your MongoDB Atlas connection string |
| `JWT_SECRET` | A strong random secret |
| `SERPAPI_API_KEY` | Your SerpAPI key (optional) |
| `FRONTEND_URL` | Your Vercel URL (e.g. `https://tol-mol-ke-bol.vercel.app`) |

### Frontend → Vercel

1. Go to [vercel.com](https://vercel.com) → **New Project** → Import from GitHub
2. Settings:
   - **Root Directory:** `frontend`
   - **Framework Preset:** Vite
3. Environment Variables:

| Key | Value |
|-----|-------|
| `VITE_API_BASE_URL` | Your Render URL (e.g. `https://tol-mol-ke-bol.onrender.com`) |

### MongoDB Atlas

1. Create a free cluster at [cloud.mongodb.com](https://cloud.mongodb.com)
2. **Network Access** → Add IP `0.0.0.0/0` (allow from anywhere for Render)
3. **Database Access** → Create a user with read/write permissions
4. Copy the connection string into `MONGODB_URI`

---

## API Endpoints

| Method | Route | Auth | Description |
|--------|-------|------|-------------|
| GET | `/` | No | Health check |
| GET | `/search?q=rice` | No | Search & compare prices |
| POST | `/api/auth/signup` | No | Create account |
| POST | `/api/auth/login` | No | Log in, get JWT |
| GET | `/api/auth/me` | Yes | Get current user profile |
