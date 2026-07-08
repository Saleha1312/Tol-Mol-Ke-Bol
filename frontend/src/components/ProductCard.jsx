export default function ProductCard({ product, isLowest }) {
    return (
        <div className={`product-card ${isLowest ? 'product-card--lowest' : ''}`}>
            {isLowest && <div className="product-badge">🏷️ Lowest Price</div>}
            <img
                src={product.image}
                alt={product.title}
                className="product-image"
                onError={(e) => {
                    e.target.src =
                        'https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop';
                }}
            />
            <div className="product-info">
                <div className="product-store">{product.store}</div>
                <div className="product-title">{product.title}</div>
                <div className="product-price-row">
                    <div className={`product-price ${product.verified ? 'product-price--verified' : ''}`}>
                        {product.price_display || `₹${product.price.toFixed(2)}`}
                    </div>
                    {product.verified && <span className="verified-badge">✓ Exact</span>}
                </div>
                <a
                    href={product.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="product-btn"
                    aria-label={`Buy ${product.title} from ${product.store}`}
                >
                    Buy Now →
                </a>
            </div>
        </div>
    );
}
