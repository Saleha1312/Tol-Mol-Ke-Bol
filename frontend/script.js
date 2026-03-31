document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');
    const productsGrid = document.getElementById('products-grid');
    const loadingEl = document.getElementById('loading');
    const resultsHeader = document.getElementById('results-header');
    const resultsTitleSpan = document.querySelector('#results-title span');

    // Use relative path if hosting frontend and backend together,
    // otherwise replace with actual backend URL.
    const API_BASE = 'http://127.0.0.1:8000';

    searchForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const query = searchInput.value.trim();
        if (!query) return;

        // Reset UI state
        productsGrid.innerHTML = '';
        resultsHeader.classList.add('hidden');
        loadingEl.classList.remove('hidden');
        
        try {
            const url = new URL(`${API_BASE}/search`);
            url.searchParams.append('q', query);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            const products = await response.json();
            renderProducts(products);
            
            resultsTitleSpan.textContent = query;
            resultsHeader.classList.remove('hidden');
            
        } catch (error) {
            console.error('Error fetching data:', error);
            productsGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                    <h3>Oops! Something went wrong.</h3>
                    <p>Make sure the backend server (${API_BASE}) is running.</p>
                </div>
            `;
        } finally {
            loadingEl.classList.add('hidden');
        }
    });

    function renderProducts(products) {
        if (!products || products.length === 0) {
            productsGrid.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
                    <h3>No products found.</h3>
                    <p>Try refining your search query.</p>
                </div>
            `;
            return;
        }

        // Backend assumes sorting by price ascending
        products.forEach((product, index) => {
            const isLowestPrice = (index === 0);
            
            const card = document.createElement('div');
            card.className = 'product-card';

            const badgeHtml = isLowestPrice ? `<div class="product-badge">Lowest Price</div>` : '';

            card.innerHTML = `
                ${badgeHtml}
                <img src="${product.image}" alt="${product.title}" class="product-image" onerror="this.src='https://images.unsplash.com/photo-1542838132-92c53300491e?w=300&h=300&fit=crop'">
                <div class="product-info">
                    <div class="product-store">${product.store}</div>
                    <div class="product-title">${product.title}</div>
                    <div class="product-price">₹${product.price.toFixed(2)}</div>
                    <a href="${product.link}" target="_blank" rel="noopener noreferrer" class="product-btn" aria-label="Buy ${product.title} from ${product.store}">Buy Now</a>
                </div>
            `;
            
            productsGrid.appendChild(card);
        });
    }
});
