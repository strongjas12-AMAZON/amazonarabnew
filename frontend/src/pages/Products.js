import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import api from '../lib/api';
import ProductCard from '../components/ProductCard';
import { toast } from 'sonner';
import { Search, Filter, X } from 'lucide-react';

const Products = () => {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const { user } = useAuth();
  const { addToCart } = useCart();

  useEffect(() => {
    fetchCategories();
  }, []);

  useEffect(() => {
    const handler = setTimeout(() => {
      fetchProducts(selectedCategory, searchQuery);
    }, 300);

    return () => clearTimeout(handler);
  }, [selectedCategory, searchQuery]);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to load categories');
    }
  };

  const fetchProducts = async (category = '', search = '') => {
    try {
      setLoading(true);
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (search) params.append('search', search);
      const url = params.toString() ? `/products?${params.toString()}` : '/products';
      const response = await api.get(url);
      setProducts(response.data.products || []);
    } catch (error) {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    if (!user) {
      toast.error('Please login to add items to cart');
      return;
    }
    if (user.role !== 'buyer') {
      toast.error('Only buyers can add items to cart');
      return;
    }
    addToCart(product);
    toast.success(`${product.title} added to cart`);
  };

  const filteredProducts = products;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-12">
        <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-4" data-testid="products-title">
          Luxury Products
        </h1>
        <p className="text-gray-400 text-lg">Discover premium products from verified sellers</p>
      </div>

      {/* Search and Filter Bar */}
      <div className="mb-8 space-y-4">
        {/* Search */}
        <div className="relative max-w-xl">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
          <input
            type="text"
            placeholder="Search products by name, description, or store name..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="luxury-input pl-12"
            data-testid="search-input"
          />
        </div>

        {/* Category Filter */}
        <div className="flex flex-wrap gap-2 items-center">
          <Filter className="w-5 h-5 text-gray-500" />
          <button
            onClick={() => setSelectedCategory('')}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              selectedCategory === ''
                ? 'bg-[#D4AF37] text-black'
                : 'bg-[rgba(30,30,30,0.8)] text-gray-300 hover:bg-[rgba(212,175,55,0.2)]'
            }`}
            data-testid="category-all"
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat.id}
              onClick={() => setSelectedCategory(cat.id)}
              className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
                selectedCategory === cat.id
                  ? 'bg-[#D4AF37] text-black'
                  : 'bg-[rgba(30,30,30,0.8)] text-gray-300 hover:bg-[rgba(212,175,55,0.2)]'
              }`}
              data-testid={`category-${cat.id}`}
            >
              {cat.icon} {cat.name}
            </button>
          ))}
        </div>

        {/* Active Filter Badge */}
        {selectedCategory && (
          <div className="flex items-center gap-2">
            <span className="text-gray-400 text-sm">Filtering by:</span>
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-[rgba(212,175,55,0.2)] text-[#D4AF37] rounded-full text-sm">
              {categories.find(c => c.id === selectedCategory)?.icon}{' '}
              {categories.find(c => c.id === selectedCategory)?.name}
              <button
                onClick={() => setSelectedCategory('')}
                className="ml-1 hover:text-white"
                data-testid="clear-filter"
              >
                <X className="w-4 h-4" />
              </button>
            </span>
          </div>
        )}
      </div>

      {/* Loading State */}
      {loading ? (
        <div className="flex items-center justify-center py-20">
          <div className="spinner"></div>
        </div>
      ) : (
        <>
          {/* Products Grid */}
          {filteredProducts.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-400 text-xl">No products found</p>
              {selectedCategory && (
                <button
                  onClick={() => setSelectedCategory('')}
                  className="mt-4 text-[#D4AF37] hover:underline"
                >
                  Clear filter and show all products
                </button>
              )}
            </div>
          ) : (
            <>
              <p className="text-gray-500 text-sm mb-4">
                Showing {filteredProducts.length} product{filteredProducts.length !== 1 ? 's' : ''}
                {selectedCategory && ` in ${categories.find(c => c.id === selectedCategory)?.name}`}
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6" data-testid="products-grid">
                {filteredProducts.map((product) => (
                  <ProductCard
                    key={product.id}
                    product={product}
                    onAddToCart={handleAddToCart}
                    canAddToCart={user?.role === 'buyer'}
                  />
                ))}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
};

export default Products;
