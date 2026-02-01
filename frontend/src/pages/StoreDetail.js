import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Store, Package, ShoppingCart, DollarSign } from 'lucide-react';
import { toast } from 'sonner';
import { useCart } from '../context/CartContext';
import api from '../lib/api';

export default function StoreDetail() {
  const { storeId } = useParams();
  const navigate = useNavigate();
  const { addToCart } = useCart();
  
  const [store, setStore] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [productsLoading, setProductsLoading] = useState(true);

  useEffect(() => {
    if (storeId) {
      fetchStoreDetails();
      fetchStoreProducts();
    }
  }, [storeId]);

  const fetchStoreDetails = async () => {
    try {
      const response = await api.get(`/stores/${storeId}`);
      const data = response.data;

      if (data.success) {
        setStore(data.store);
      } else {
        toast.error('Store not found');
        navigate('/stores/search');
      }
    } catch (error) {
      console.error('Fetch store error:', error);
      toast.error('Failed to load store details');
    } finally {
      setLoading(false);
    }
  };

  const fetchStoreProducts = async () => {
    try {
      const response = await api.get(`/stores/${storeId}/products?limit=100`);
      const data = response.data;

      if (data.success) {
        setProducts(data.products || []);
      } else {
        toast.error('Failed to load products');
      }
    } catch (error) {
      console.error('Fetch products error:', error);
      toast.error('Failed to load products');
    } finally {
      setProductsLoading(false);
    }
  };

  const handleAddToCart = (product) => {
    if (product.stock <= 0) {
      toast.error('Product out of stock');
      return;
    }

    // Create a product object compatible with cart
    const cartProduct = {
      id: product.id, // FIXED: Use store_product ID (not catalogProductId)
      title: product.name,
      price: product.price,
      images: product.images,
      sellerId: product.sellerId,
      storeName: store?.storeName,
      stock: product.stock,
      catalogProductId: product.catalogProductId // Keep for reference
    };

    addToCart(cartProduct);
    toast.success('Added to cart!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black py-12 px-4">
        <div className="max-w-7xl mx-auto text-center py-20">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-yellow-400"></div>
          <p className="text-gray-400 mt-4">Loading store...</p>
        </div>
      </div>
    );
  }

  if (!store) {
    return null;
  }

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/stores/search')}
          className="flex items-center space-x-2 text-gray-400 hover:text-[#D4AF37] transition-colors mb-8"
        >
          <ArrowLeft size={20} />
          <span>Back to Stores</span>
        </button>

        {/* Store Header */}
        <div className="luxury-card mb-10">
          <div className="flex items-start space-x-6">
            <div className="p-4 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-2xl">
              <Store className="text-[#0a0a0a]" size={48} />
            </div>
            <div className="flex-1">
              <h1 className="font-['Playfair_Display'] text-4xl font-bold text-gold-gradient mb-2">
                {store.storeName}
              </h1>
              {store.seller && (
                <div className="flex items-center space-x-4 text-gray-400 mb-4">
                  <span>By {store.seller.name}</span>
                  <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-sm font-semibold">
                    {store.seller.verificationStatus === 'verified' ? 'Verified' : store.seller.verificationStatus}
                  </span>
                </div>
              )}
              <div className="flex items-center space-x-6 text-sm text-gray-500">
                <div className="flex items-center space-x-2">
                  <Package size={16} />
                  <span>{products.length} Products</span>
                </div>
                <div className="flex items-center space-x-2">
                  <span>Store ID: {store.id.substring(0, 12)}...</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Products Section */}
        <div>
          <h2 className="font-['Playfair_Display'] text-3xl font-bold text-white mb-6">Store Products</h2>

          {productsLoading ? (
            <div className="text-center py-20">
              <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#D4AF37]"></div>
              <p className="text-gray-400 mt-4">Loading products...</p>
            </div>
          ) : products.length === 0 ? (
            <div className="luxury-card text-center py-20">
              <Package size={64} className="mx-auto text-gray-600 mb-4" />
              <h3 className="font-['Playfair_Display'] text-2xl font-semibold text-gray-300 mb-2">No products yet</h3>
              <p className="text-gray-500">This store hasn't added any products yet. Check back later!</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {products.map((product) => (
                <div
                  key={product.id}
                  className="luxury-card group hover:border-[#D4AF37] transition-all hover:shadow-xl hover:shadow-[rgba(212,175,55,0.1)] transform hover:-translate-y-1 overflow-hidden"
                >
                  {/* Product Image */}
                  <div className="relative h-48 bg-[rgba(20,20,20,0.5)] overflow-hidden">
                    {product.images && product.images.length > 0 ? (
                      <img
                        src={product.images[0]}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package size={48} className="text-gray-700" />
                      </div>
                    )}
                    {product.stock <= 0 && (
                      <div className="absolute inset-0 bg-black/70 flex items-center justify-center">
                        <span className="px-4 py-2 bg-red-500 text-white font-semibold rounded-lg">
                          Out of Stock
                        </span>
                      </div>
                    )}
                  </div>

                  {/* Product Info */}
                  <div className="p-5">
                    <h3 className="text-lg font-['Playfair_Display'] font-semibold text-white mb-2 line-clamp-2 group-hover:text-[#D4AF37] transition-colors">
                      {product.name}
                    </h3>
                    
                    <p className="text-sm text-gray-400 mb-3 line-clamp-2">
                      {product.description}
                    </p>

                    <div className="flex items-center justify-between mb-4">
                      <div>
                        <div className="flex items-center space-x-2">
                          <DollarSign size={18} className="text-[#D4AF37]" />
                          <span className="text-2xl font-bold text-[#D4AF37]">
                            {product.price.toFixed(2)}
                          </span>
                        </div>
                        {product.basePrice && product.basePrice !== product.price && (
                          <span className="text-sm text-gray-500 line-through">
                            ${product.basePrice.toFixed(2)}
                          </span>
                        )}
                      </div>
                      <div className="text-right">
                        <p className="text-xs text-gray-500">Stock</p>
                        <p className="text-sm font-semibold text-gray-300">{product.stock}</p>
                      </div>
                    </div>

                    <button
                      onClick={() => handleAddToCart(product)}
                      disabled={product.stock <= 0}
                      className="btn-gold w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
                    >
                      <ShoppingCart size={18} />
                      <span>{product.stock <= 0 ? 'Out of Stock' : 'Add to Cart'}</span>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
