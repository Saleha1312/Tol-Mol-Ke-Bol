# Tol Mol Ke Bol - Grocery Price Comparison

Tol Mol Ke Bol is a grocery price comparison site that lets you search and compare grocery prices across Amazon, Flipkart, and JioMart to find the best deals. The project uses a FastAPI backend that scrapes search engine results (via SerpAPI or mock fallback) and a lightweight, responsive vanilla frontend.

## Features

- **Price Comparison:** Simultaneously fetches results from Amazon, Flipkart, and JioMart.
- **Smart Sorting:** Automatically sorts queries from lowest price to highest price.
- **Highlight Lowest Price:** The best-priced deal is highlighted at the top of the search results visually.
- **Affiliate Monetization:** Pre-integrated to use Cuelinks to convert ordinary outbound links into automatic affiliate commission links.
- **Premium Design:** Features a clean, fast-loading, dynamic interface built using modern CSS conventions (glassmorphism UI, gradient backgrounds, responsive flex grids).

## Project Structure

```bash
├── backend
│   ├── main.py              # FastAPI server handling /search endpoint
│   └── requirements.txt     # Python backend dependencies
├── frontend
│   ├── index.html           # Main HTML dashboard & UI
│   ├── script.js            # Vanilla JS fetching data and handling state
│   └── style.css            # Stylesheets with fluid grid and modern components
└── README.md                # This file!
```

## Getting Started

Follow the instructions below to get a local development copy up and running.

### 1. Prerequisites
- Python 3.8+
- Optional: A [SerpAPI](https://serpapi.com/) key installed for real-time web results. If missing, the app defaults to fallback mock data seamlessly.

### 2. Backend Setup
Navigate into the `backend/` directory and install the dependancies.

```bash
cd backend
pip install -r requirements.txt
```

Run the backend via Uvicorn:
```bash
uvicorn main:app --reload
```
*The backend server will run continuously on `http://127.0.0.1:8000`.*

### 3. Frontend Setup
Because the frontend is pure HTML/CSS/JS, you can simply open the `frontend/index.html` file in your favorite modern browser, or run a lightweight Live Server from Visual Studio Code.

### 4. Optional Configurations
- **SerpAPI:** Supply your valid `SERPAPI_API_KEY` environmental variable, and the app will cease to use mock data, replacing it with Google Shopping results filtered for actual stores.
- **Cuelinks:** Open `index.html` and replace `YOUR_CUELINKS_PUBLISHER_KEY` with your actual identifier to begin tracking clicks and earning commissions!
