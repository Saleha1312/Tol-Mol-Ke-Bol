import { useState } from 'react';
import API from '../api';
import ProductCard from '../components/ProductCard';

export default function Home() {
    const [query, setQuery] = useState('');
    const [products, setProducts] = useState([]);
    const [loading, setLoading] = useState(false);
    const [searched, setSearched] = useState(false);

    const handleSearch = async (e) => {
        e.preventDefault();
        if (!query.trim()) return;

        setLoading(true);
        setSearched(true);
        setProducts([]);

        try {
            const res = await API.get('/search', { params: { q: query.trim() } });
            setProducts(res.data);
        } catch (err) {
            console.error('Search failed:', err);
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
                        Find the lowest grocery prices across Amazon, Flipkart & JioMart — instantly.
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
                        <span className="store-tag">JioMart</span>
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
                        <h2 className="results-title">
                            Results for "<span className="highlight">{query}</span>"
                        </h2>
                        <div className="products-grid">
                            {products.map((product, index) => (
                                <ProductCard
                                    key={index}
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
