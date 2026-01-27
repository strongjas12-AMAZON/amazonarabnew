import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Store, ChevronRight, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

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
        ? `${BACKEND_URL}/api/stores/search?query=${encodeURIComponent(query)}&limit=50`
        : `${BACKEND_URL}/api/stores/search?limit=50`;
      
      const response = await fetch(url);
      const data = await response.json();

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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-black py-12 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-yellow-200 mb-4">
            Browse Stores
          </h1>
          <p className="text-gray-400 text-lg">
            Discover products from verified sellers in our marketplace
          </p>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="mb-10">
          <div className="relative max-w-2xl mx-auto">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search stores by name..."
              className="w-full px-6 py-4 pl-14 bg-gray-800/50 border border-gray-700 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-yellow-500 focus:ring-2 focus:ring-yellow-500/20 transition-all"
            />
            <Search className="absolute left-5 top-1/2 transform -translate-y-1/2 text-gray-500" size={20} />
            <button
              type="submit"
              disabled={searching}
              className="absolute right-2 top-1/2 transform -translate-y-1/2 px-6 py-2 bg-gradient-to-r from-yellow-500 to-yellow-400 text-black font-semibold rounded-lg hover:from-yellow-400 hover:to-yellow-300 transition-all disabled:opacity-50"
            >
              {searching ? 'Searching...' : 'Search'}
            </button>
          </div>
        </form>

        {/* Loading State */}
        {loading && (
          <div className="text-center py-20">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-yellow-400"></div>
            <p className="text-gray-400 mt-4">Loading stores...</p>
          </div>
        )}

        {/* Empty State */}
        {!loading && stores.length === 0 && (
          <div className="text-center py-20">
            <ShoppingBag size={64} className="mx-auto text-gray-600 mb-4" />
            <h3 className="text-2xl font-semibold text-gray-300 mb-2">No stores found</h3>
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
                className="group bg-gradient-to-br from-gray-800 to-gray-900 border border-gray-700 rounded-2xl p-6 hover:border-yellow-500 transition-all cursor-pointer hover:shadow-xl hover:shadow-yellow-500/10 transform hover:-translate-y-1"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="p-3 bg-gradient-to-br from-yellow-500 to-yellow-400 rounded-xl group-hover:scale-110 transition-transform">
                      <Store className="text-black" size={24} />
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white group-hover:text-yellow-400 transition-colors">
                        {store.storeName}
                      </h3>
                      <p className="text-sm text-gray-500">Verified Seller</p>
                    </div>
                  </div>
                  <ChevronRight className="text-gray-600 group-hover:text-yellow-400 transition-colors" size={20} />
                </div>

                <div className="pt-4 border-t border-gray-700">
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
