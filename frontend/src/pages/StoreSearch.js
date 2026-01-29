import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Store, ChevronRight, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';
import api from '../lib/api';

export default function StoreSearch() {
  const navigate = useNavigate();
  const [stores, setStores] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [searching, setSearching] = useState(false);

  // Fetch stores on mount
  useEffect(() => {
    fetchStores();
  }, []);

  const fetchStores = async (query = '') => {
    try {
      setSearching(true);
      const url = query 
        ? `/stores/search?query=${encodeURIComponent(query)}&limit=50`
        : `/stores/search?limit=50`;
      
      const response = await api.get(url);
      const data = response.data;

      if (data.success) {
        setStores(data.stores || []);
      } else {
        toast.error('Failed to load stores');
      }
    } catch (error) {
      console.error('Fetch stores error:', error);
      toast.error('Failed to load stores');
    } finally {
      setLoading(false);
      setSearching(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchStores(searchQuery);
  };

  const handleStoreClick = (storeId) => {
    navigate(`/stores/${storeId}`);
  };

  return (
    <div className="min-h-screen py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-4">
            Browse Stores
          </h1>
          <p className="text-gray-400 text-lg">
            Discover products from verified sellers in our marketplace
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-10">
          <div className="relative max-w-2xl mx-auto">
            <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-500 z-10" size={20} />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search stores by name..."
              className="luxury-input w-full pl-14 pr-32"
            />
            <button
              type="submit"
              disabled={searching}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-[#D4AF37] to-[#F4E4B0] text-[#0a0a0a] font-semibold rounded-lg hover:from-[#F4E4B0] hover:to-[#D4AF37] transition-all disabled:opacity-50 text-sm"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-[#D4AF37]"></div>
            <p className="text-gray-400 mt-4">Loading stores...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && stores.length === 0 && (
          <div className="text-center py-20">
            <ShoppingBag size={64} className="mx-auto text-gray-600 mb-4" />
            <h3 className="font-['Playfair_Display'] text-2xl font-semibold text-gray-300 mb-2">No stores found</h3>
            <p className="text-gray-500">
              {searchQuery ? 'Try a different search term' : 'No active stores available yet'}
            </p>
          </div>
        )}

        {/* Stores Grid */}
        {!loading && stores.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stores.map((store) => (
              <div
                key={store.id}
                onClick={() => handleStoreClick(store.id)}
                className="luxury-card group cursor-pointer hover:border-[#D4AF37] transition-all hover:shadow-xl hover:shadow-[rgba(212,175,55,0.1)] transform hover:-translate-y-1"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-xl group-hover:scale-110 transition-transform">
                      <Store className="text-[#0a0a0a]" size={24} />
                    </div>
                    <div>
                      <h3 className="text-xl font-['Playfair_Display'] font-bold text-white group-hover:text-[#D4AF37] transition-colors">
                        {store.storeName}
                      </h3>
                      <p className="text-sm text-gray-500">Verified Seller</p>
                    </div>
                  </div>
                  <ChevronRight className="text-gray-600 group-hover:text-[#D4AF37] transition-colors" size={20} />
                </div>

                <div className="pt-4 border-t border-[rgba(212,175,55,0.2)]">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Store ID</span>
                    <span className="text-gray-500 font-mono text-xs">
                      {store.id.substring(0, 8)}...
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm mt-2">
                    <span className="text-gray-400">Status</span>
                    <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                      {store.status}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Results Count */}
        {!loading && stores.length > 0 && (
          <div className="text-center mt-10 text-gray-500">
            Showing {stores.length} store{stores.length !== 1 ? 's' : ''}
          </div>
        )}
      </div>
    </div>
  );
}
