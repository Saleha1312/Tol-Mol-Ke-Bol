import { useState, useRef } from 'react';
import API from '../api';
import ProductCard from '../components/ProductCard';

export default function Home() {
    const [query, setQuery] = useState('');
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [verifying, setVerifying] = useState(false);
    const [searched, setSearched] = useState(false);
    const abortRef = useRef(null);

    const verifyPrices = async (items) => {
        if (!items.length) return;
        setVerifying(true);
        try {
            const res = await API.post('/verify-prices', { products: items });
            if (res.data.length > 0) {
                setProducts((prev) => {
                    const updated = [...prev];
                    for (const v of res.data) {
                        if (updated[v.index]) {
                            updated[v.index] = {
                                ...updated[v.index],
                                price: v.price,
                                price_display: v.price_display,
                                verified: true,
                            };
                        }
                    }
                    return updated.sort((a, b) => a.price - b.price);
                });
            }
        } catch {
            // Verification failed — keep SerpAPI prices
        } finally {
            setVerifying(false);
        }
    };

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        if (abortRef.current) abortRef.current.abort();
        const controller = new AbortController();
        abortRef.current = controller;

        setLoading(true);
        setSearched(true);
        setProducts([]);

        try {
            const res = await API.get('/search', {
                params: { q: query.trim() },
                signal: controller.signal,
            });
            setProducts(res.data);
            verifyPrices(res.data);
        } catch (err) {
            if (err.name !== 'CanceledError') {
                console.error('Search failed:', err);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <>
            <header className="hero">
                <div className="hero-content">
                    <h1 className="hero-title">
                        Compare. Save. <span className="hero-highlight">Shop Smart.</span>
                    </h1>
                    <p className="hero-subtitle">
                        Find the lowest grocery prices across Amazon, Flipkart, BigBasket, Blinkit & Instamart — instantly.
                    </p>
                    <form onSubmit={handleSearch} className="search-box" id="search-form">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Search for groceries (e.g. 'Basmati Rice 1kg')"
                            className="search-input"
                            id="search-input"
                            required
                        />
                        <button type="submit" className="search-btn" id="search-btn" disabled={loading}>
                            {loading ? 'Searching...' : 'Search'}
                        </button>
                    </form>
                    <div className="hero-stores">
                        <span className="store-tag">Amazon</span>
                        <span className="store-tag">Flipkart</span>
                        <span className="store-tag">BigBasket</span>
                        <span className="store-tag">Blinkit</span>
                        <span className="store-tag">Instamart</span>
                    </div>
                </div>
            </header>

            <main className="container">
                {loading && (
                    <div className="loading-state">
                        <div className="spinner"></div>
                        <p>Scanning stores for the best prices...</p>
                    </div>
                )}

                {!loading && searched && products.length === 0 && (
                    <div className="empty-state">
                        <span className="empty-icon">🔍</span>
                        <h3>No products found</h3>
                        <p>Try a different search term like "Atta", "Sugar", or "Oil"</p>
                    </div>
                )}

                {!loading && products.length > 0 && (
                    <>
                        <div className="results-header">
                            <h2 className="results-title">
                                Results for "<span className="highlight">{query}</span>"
                            </h2>
                            {verifying && (
                                <div className="verifying-badge">
                                    <div className="spinner spinner--small"></div>
                                    Fetching exact prices from stores...
                                </div>
                            )}
                        </div>
                        <div className="products-grid">
                            {products.map((product, index) => (
                                <ProductCard
                                    key={`${product.store}-${product.title}-${index}`}
                                    product={product}
                                    isLowest={index === 0}
                                />
                            ))}
                        </div>
                    </>
                )}
            </main>
        </>
    );
}
