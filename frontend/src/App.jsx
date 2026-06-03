import React, { useState, useEffect } from 'react';

function App() {
  const [products, setProducts] = useState([]);
  const [preference, setPreference] = useState('');
  const [loading, setLoading] = useState(false);
  const [isFiltered, setIsFiltered] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  const fetchProducts = async () => {
    try {
      const res = await fetch('http://127.0.0.1:8000/api/products');
      const data = await res.json();
      setProducts(data);
      setIsFiltered(false);
    } catch (err) {
      console.error("Error fetching products:", err);
    }
  };

  const handleRecommend = async (e) => {
    e.preventDefault();
    if (!preference.trim()) return;

    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/recommend', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ preference })
      });
      const data = await res.json();
      setProducts(data);
      setIsFiltered(true);
    } catch (err) {
      console.error("Error fetching recommendations:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen py-8 px-4 sm:px-6 lg:px-8 font-sans">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-3xl font-extrabold text-gray-900 tracking-tight">AI Product Advisor</h1>
          <p className="mt-2 text-sm text-gray-600">Powered by Groq Cloud API</p>
        </header>

        <div className="bg-white p-6 rounded-lg shadow-sm mb-8 border border-gray-200">
          <form onSubmit={handleRecommend} className="flex gap-3">
            <input
              type="text"
              value={preference}
              onChange={(e) => setPreference(e.target.value)}
              placeholder="e.g., 'I need a cheap phone under $500' or 'Premium laptop for work'"
              className="flex-1 min-w-0 block w-full px-4 py-2 text-base text-gray-900 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
            <button
              type="submit"
              disabled={loading}
              className="inline-flex items-center px-4 py-2 text-base font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50"
            >
              {loading ? 'Thinking...' : 'Recommend'}
            </button>
          </form>
          {isFiltered && (
            <button 
              onClick={fetchProducts} 
              className="mt-3 text-sm text-indigo-600 hover:text-indigo-500 font-medium"
            >
              Reset Filters & Show All Products
            </button>
          )}
        </div>

        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {products.length > 0 ? (
            products.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-5 flex flex-col justify-between">
                <div>
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800 mb-3">
                    {product.category}
                  </span>
                  <h3 className="text-lg font-bold text-gray-900">{product.name}</h3>
                  <p className="text-sm text-gray-500 mt-2">{product.description}</p>
                </div>
                <div className="mt-4 pt-4 border-t border-gray-100 flex items-center justify-between">
                  <span className="text-xl font-extrabold text-gray-900">${product.price}</span>
                </div>
              </div>
            ))
          ) : (
            <div className="col-span-full text-center py-12 text-gray-500">
              No matching products found. Try adjusting your preferences.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;