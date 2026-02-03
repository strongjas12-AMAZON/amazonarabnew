import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { useDropzone } from 'react-dropzone';
import { 
  Package, Plus, Edit, Trash2, Upload, AlertCircle, CheckCircle, Tag, 
  ShoppingCart, Clock, DollarSign, Wallet, Search, Store, Check, ClipboardList
} from 'lucide-react';
import OrderCenter from './OrderCenter';

const SellerDashboard = () => {
  const { user } = useAuth();
  const [myProducts, setMyProducts] = useState([]);
  const [catalogProducts, setCatalogProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [earnings, setEarnings] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('myProducts');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [showVerificationForm, setShowVerificationForm] = useState(false);
  const [verificationForm, setVerificationForm] = useState({
    merchantInviteCode: '',
    documentType: 'business_document'
  });

  console.log("orders",orders);
  const [storeRequest, setStoreRequest] = useState(null);
  const [showStoreNameModal, setShowStoreNameModal] = useState(false);
  const [newStoreName, setNewStoreName] = useState('');
  const [payoutAmount, setPayoutAmount] = useState('');
  const [payoutWallet, setPayoutWallet] = useState('');
  const [payoutSubmitting, setPayoutSubmitting] = useState(false);
  
  // Wallet recharge states
  const [showRechargeModal, setShowRechargeModal] = useState(false);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [transactionHash, setTransactionHash] = useState('');
  const [rechargeSubmitting, setRechargeSubmitting] = useState(false);
  const [rechargeHistory, setRechargeHistory] = useState([]);
  const [walletBalance, setWalletBalance] = useState(null);
  
  // NEW: Escrow + Deposit system states
  const [pendingDepositOrders, setPendingDepositOrders] = useState([]);
  const [depositingOrderId, setDepositingOrderId] = useState(null);
  const [loadingDeposits, setLoadingDeposits] = useState(false);

  useEffect(() => {
    if (user) {
      fetchData();
      fetchCategories();
      fetchStoreNameRequest();
      fetchEarnings();
      fetchRechargeHistory();
      fetchWalletBalance();
      fetchPendingDepositOrders(); // NEW: Fetch orders needing deposits
    }
  }, [user]);

  const fetchWalletBalance = async () => {
    try {
      const res = await api.get('/seller/wallet/balance');
      setWalletBalance(res.data.wallet || null);
    } catch (error) {
      console.error('Failed to load wallet balance', error);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to load categories');
    }
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [myProductsRes, ordersRes] = await Promise.all([
        api.get('/seller/store/products'),  // Use new store system endpoint
        api.get('/orders/my')
      ]);
      setMyProducts(myProductsRes.data.products || []);
      setOrders(ordersRes.data.orders || []);
      
      // Fetch catalog if seller is verified
      if (user?.verificationStatus === 'verified') {
        try {
          const catalogRes = await api.get('/seller/catalog/products');
          setCatalogProducts(catalogRes.data.products || []);
        } catch (err) {
          console.log('Catalog not available');
          setCatalogProducts([]);
        }
      }
    } catch (error) {
      toast.error('Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const fetchEarnings = async () => {
    try {
      const res = await api.get('/seller/earnings');
      setEarnings(res.data.earnings || null);
    } catch (error) {
      // silently ignore for now; stats section will just not show payouts
      console.error('Failed to load earnings', error);
    }
  };

  const fetchRechargeHistory = async () => {
    try {
      const res = await api.get('/seller/wallet/recharge-requests');
      setRechargeHistory(res.data.rechargeRequests || []);
    } catch (error) {
      console.error('Failed to load recharge history', error);
    }
  };

  const handleRechargeSubmit = async (e) => {
    e.preventDefault();
    const amount = parseFloat(rechargeAmount || '0');
    
    if (!amount || amount <= 0) {
      toast.error('Please enter a valid amount');
      return;
    }
    
    if (!transactionHash || transactionHash.trim() === '') {
      toast.error('Please enter your transaction hash');
      return;
    }
    
    try {
      setRechargeSubmitting(true);
      await api.post('/seller/wallet/recharge', {
        amount: amount,
        paymentMethod: 'USDT_TRON',
        paymentWallet: transactionHash.trim() // Using this field for transaction hash
      });
      toast.success('Recharge request submitted successfully! Awaiting admin approval.');
      setRechargeAmount('');
      setTransactionHash('');
      setShowRechargeModal(false);
      await fetchRechargeHistory();
      await fetchWalletBalance(); // Refresh wallet balance
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit recharge request');
    } finally {
      setRechargeSubmitting(false);
    }
  };

  const fetchStoreNameRequest = async () => {
    try {
      const res = await api.get('/seller/store-name-change');
      setStoreRequest(res.data.request || null);
    } catch (error) {
      // silently ignore
    }
  };

  const handleAddToStore = async (product) => {
    try {
      // Backend expects form data with catalog_product_id, price, and stock
      const formData = new FormData();
      formData.append('catalog_product_id', product.id);
      formData.append('price', product.basePrice || product.price || 0);
      formData.append('stock', 10); // Default stock of 10
      
      await api.post('/seller/store/products', formData);
      toast.success('Product added to your store!');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to add product');
    }
  };

  const handleRemoveFromStore = async (productId) => {
    if (!window.confirm('Remove this product from your store?')) return;
    try {
      await api.delete(`/seller/store/products/${productId}`);
      toast.success('Product removed from your store');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to remove product');
    }
  };

  const handleVerificationUpload = async (file) => {
    if (!verificationForm.merchantInviteCode) {
      toast.error('Please enter merchant invite code');
      return;
    }
    try {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('documentType', verificationForm.documentType);
      formData.append('merchantInviteCode', verificationForm.merchantInviteCode);
      // Don't set Content-Type explicitly - axios will set it automatically for FormData with the correct boundary
      await api.post('/verification/upload', formData);
      toast.success('Verification document uploaded! Awaiting admin review.');
      setShowVerificationForm(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    }
  };

  // Filter catalog products - use 'name' field from new store system
  const filteredCatalog = catalogProducts.filter(p => {
    const matchesSearch = (p.name || p.title || '')?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          (p.description || '')?.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesCategory = !selectedCategory || p.category === selectedCategory;
    return matchesSearch && matchesCategory;
  });

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-4" data-testid="seller-dashboard-title">
          Seller Dashboard
        </h1>
        {user.storeName ? (
          <>
            {/* Store Name Card - Prominently Displayed */}
            <div className="luxury-card mb-4 p-4 border-[#D4AF37]/30 flex flex-col gap-2">
              <div className="flex items-center justify-between gap-3 flex-wrap">
                <div className="flex items-center gap-3">
                  <p className="text-gray-300 text-lg font-medium">Store Name:</p>
                  <p className="text-[#D4AF37] text-2xl font-bold flex items-center gap-2">
                    {user.storeName}
                    {storeRequest?.status === 'pending' && (
                      <span className="inline-flex px-2 py-0.5 rounded-full text-[10px] font-semibold bg-yellow-500/20 text-yellow-400 border border-yellow-500/40">
                        Pending change
                      </span>
                    )}
                  </p>
                </div>
                <button
                  onClick={() => {
                    setNewStoreName('');
                    setShowStoreNameModal(true);
                  }}
                  className="px-3 py-1 rounded-md text-xs bg-[rgba(212,175,55,0.1)] text-[#D4AF37] hover:bg-[rgba(212,175,55,0.2)] transition-colors"
                >
                  Edit Store Name
                </button>
              </div>
              <p className="text-xs text-gray-500">
                Store name changes require admin approval
              </p>
              {storeRequest && (
                <div className="text-xs mt-1">
                  {storeRequest.status === 'pending' && (
                    <p className="text-yellow-400">
                      Change requested to "<span className="font-semibold">{storeRequest.newStoreName}</span>" (Pending admin approval)
                    </p>
                  )}
                  {storeRequest.status === 'rejected' && (
                    <p className="text-red-400">
                      Last change request to "<span className="font-semibold">{storeRequest.newStoreName}</span>" was rejected
                      {storeRequest.adminNote && `: ${storeRequest.adminNote}`}
                    </p>
                  )}
                </div>
              )}
            </div>
            <p className="text-gray-400 text-sm">
              Welcome back, {user.name}
            </p>
          </>
        ) : (
          <p className="text-gray-400">Welcome back, {user.name}</p>
        )}
      </div>

      {/* Store Name Change Modal */}
      {showStoreNameModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-md w-full">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">Request Store Name Change</h2>
            <p className="text-sm text-gray-400 mb-4">
              Current store name: <span className="text-[#D4AF37] font-semibold">{user.storeName}</span>
            </p>
            <form
              onSubmit={async (e) => {
                e.preventDefault();
                try {
                  const trimmed = newStoreName.trim();
                  if (!trimmed) {
                    toast.error('New store name is required');
                    return;
                  }
                  const res = await api.post('/seller/store-name-change', {
                    newStoreName: trimmed,
                  });
                  toast.success('Store name change request submitted');
                  setStoreRequest(res.data.request);
                  setShowStoreNameModal(false);
                } catch (error) {
                  toast.error(error.response?.data?.detail || 'Failed to request store name change');
                }
              }}
              className="space-y-4"
            >
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  New Store Name
                </label>
                <input
                  type="text"
                  value={newStoreName}
                  onChange={(e) => setNewStoreName(e.target.value)}
                  className="luxury-input"
                  placeholder="Enter new store name"
                  minLength={2}
                  maxLength={100}
                  required
                />
              </div>
              <div className="flex gap-2 justify-end">
                <button
                  type="button"
                  onClick={() => setShowStoreNameModal(false)}
                  className="btn-gold-outline"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="btn-gold"
                >
                  Submit Request
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Verification Status */}
      {user.verificationStatus !== 'verified' && (
        <div className={`luxury-card mb-8 ${
          user.verificationStatus === 'pending' ? 'border-yellow-500/50' :
          user.verificationStatus === 'rejected' ? 'border-red-500/50' :
          'border-[#D4AF37]'
        }`}>
          <div className="flex items-start gap-4">
            {user.verificationStatus === 'pending' ? (
              <AlertCircle className="w-6 h-6 text-yellow-500 flex-shrink-0" />
            ) : user.verificationStatus === 'rejected' ? (
              <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-6 h-6 text-[#D4AF37] flex-shrink-0" />
            )}
            <div className="flex-1">
              <h3 className="font-semibold text-white mb-2">
                {user.verificationStatus === 'unverified' && 'Verification Required'}
                {user.verificationStatus === 'pending' && 'Verification Pending'}
                {user.verificationStatus === 'rejected' && 'Verification Rejected'}
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                {user.verificationStatus === 'unverified' && 'You need to verify your account with a merchant invite code and business documents to start selling.'}
                {user.verificationStatus === 'pending' && 'Your verification documents are being reviewed by our admin team.'}
                {user.verificationStatus === 'rejected' && 'Your verification was rejected. Please submit new documents.'}
              </p>
              {(user.verificationStatus === 'unverified' || user.verificationStatus === 'rejected') && (
                <button
                  onClick={() => setShowVerificationForm(true)}
                  className="btn-gold"
                  data-testid="start-verification-btn"
                >
                  Start Verification
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Verification Form Modal */}
      {showVerificationForm && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-md w-full">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">Upload Verification Documents</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Merchant Invite Code</label>
                <input
                  type="text"
                  value={verificationForm.merchantInviteCode}
                  onChange={(e) => setVerificationForm({ ...verificationForm, merchantInviteCode: e.target.value })}
                  className="luxury-input"
                  placeholder="Enter invite code"
                  data-testid="invite-code-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Document Type</label>
                <select
                  value={verificationForm.documentType}
                  onChange={(e) => setVerificationForm({ ...verificationForm, documentType: e.target.value })}
                  className="luxury-input"
                >
                  <option value="business_document">Business Document</option>
                  <option value="government_id">Government ID</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Upload Document</label>
                <input
                  type="file"
                  accept="image/*,application/pdf"
                  onChange={(e) => {
                    if (e.target.files[0]) handleVerificationUpload(e.target.files[0]);
                  }}
                  className="luxury-input"
                  data-testid="document-upload-input"
                />
              </div>
              <div className="flex gap-2">
                <button onClick={() => setShowVerificationForm(false)} className="btn-gold-outline flex-1">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">My Products</p>
          <p className="text-3xl font-bold text-[#D4AF37]">{myProducts.length}</p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Total Orders</p>
          <p className="text-3xl font-bold text-[#D4AF37]">{orders.length}</p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Total Earnings</p>
          <p className="text-3xl font-bold text-green-400">
            {earnings ? `$${earnings.totalEarnings.toFixed(2)}` : '—'}
          </p>
          <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
            <DollarSign className="w-3 h-3 text-green-400" />
            Available: <span className="text-green-400 font-semibold ml-1">{earnings ? `$${earnings.availableBalance.toFixed(2)}` : '—'}</span>
          </p>
        </div>
        <div className="luxury-card cursor-pointer hover:border-[#D4AF37] transition-colors" onClick={() => setActiveTab('wallet')}>
          <p className="text-gray-400 text-sm mb-1">Wallet Balance</p>
          <p className="text-3xl font-bold text-[#D4AF37]">
            ${walletBalance ? walletBalance.balance.toFixed(2) : '0.00'}
          </p>
          <p className="text-xs text-gray-500 mt-2 flex items-center gap-1">
            <Clock className="w-3 h-3 text-yellow-400" />
            Pending: <span className="text-yellow-400 font-semibold ml-1">${walletBalance ? walletBalance.pendingRecharges.toFixed(2) : '0.00'}</span>
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 flex-wrap">
        <button
          onClick={() => setActiveTab('myProducts')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'myProducts'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-my-products"
        >
          <Store className="w-4 h-4" />
          My Store ({myProducts.length})
        </button>
        <button
          onClick={() => setActiveTab('catalog')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'catalog'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-catalog"
        >
          <Package className="w-4 h-4" />
          Browse Catalog
        </button>
        <button
          onClick={() => setActiveTab('orders')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'orders'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-orders"
        >
          <ShoppingCart className="w-4 h-4" />
          Orders ({orders.length})
        </button>
        <button
          onClick={() => setActiveTab('orderCenter')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'orderCenter'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-order-center"
        >
          <ClipboardList className="w-4 h-4" />
          Order Center
        </button>
        <button
          onClick={() => setActiveTab('wallet')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'wallet'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-wallet"
        >
          <Wallet className="w-4 h-4" />
          Wallet
        </button>
        <button
          onClick={() => setActiveTab('payouts')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'payouts'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-payouts"
        >
          <DollarSign className="w-4 h-4" />
          Payouts
        </button>
      </div>

      {/* My Products Section */}
      {activeTab === 'myProducts' && (
        <div className="luxury-card">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">My Store Products</h2>
            {user.verificationStatus === 'verified' && (
              <button
                onClick={() => setActiveTab('catalog')}
                className="btn-gold"
                data-testid="browse-catalog-btn"
              >
                <Plus className="w-4 h-4 inline mr-2" />
                Add from Catalog
              </button>
            )}
          </div>

          {user.verificationStatus !== 'verified' ? (
            <div className="text-center py-12">
              <AlertCircle className="w-16 h-16 mx-auto text-yellow-500 mb-4" />
              <p className="text-gray-400">You need to be verified to add products</p>
              <p className="text-gray-500 text-sm mt-2">Complete verification to browse the product catalog</p>
            </div>
          ) : myProducts.length === 0 ? (
            <div className="text-center py-12">
              <Store className="w-16 h-16 mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">Your store is empty</p>
              <p className="text-gray-500 text-sm mt-2">Browse the catalog and add products to your store</p>
              <button
                onClick={() => setActiveTab('catalog')}
                className="btn-gold mt-4"
              >
                <Plus className="w-4 h-4 inline mr-2" />
                Browse Catalog
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {myProducts.map((product) => (
                <div 
                  key={product.id} 
                  className="bg-[rgba(30,30,30,0.6)] rounded-lg overflow-hidden border border-green-500/30"
                  data-testid="my-store-product"
                >
                  <div className="h-40 bg-[rgba(50,50,50,0.6)] relative">
                    {product.images && product.images.length > 0 ? (
                      <img
                        src={product.images[0]}
                        alt={product.name || product.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package className="w-10 h-10 text-gray-500" />
                      </div>
                    )}
                    <span className="absolute top-2 right-2 px-2 py-1 bg-green-500/80 text-white rounded text-xs flex items-center gap-1">
                      <Check className="w-3 h-3" />
                      In Store
                    </span>
                    {product.category && (
                      <span className="absolute top-2 left-2 px-2 py-1 bg-black/70 text-[#D4AF37] rounded text-xs">
                        {product.category}
                      </span>
                    )}
                  </div>
                  
                  <div className="p-4">
                    <h3 className="font-semibold text-white mb-1 truncate">{product.name || product.title}</h3>
                    <p className="text-[#D4AF37] font-bold">${(product.price || 0).toFixed(2)}</p>
                    <p className="text-gray-400 text-sm">Stock: {product.stock || 0}</p>
                    
                    <button
                      onClick={() => handleRemoveFromStore(product.id)}
                      className="w-full mt-3 p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors flex items-center justify-center gap-2"
                      data-testid="remove-from-store-btn"
                    >
                      <Trash2 className="w-4 h-4" />
                      Remove from Store
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Catalog Section */}
      {activeTab === 'catalog' && (
        <div className="luxury-card">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Product Catalog</h2>
          
          {user.verificationStatus !== 'verified' ? (
            <div className="text-center py-12">
              <AlertCircle className="w-16 h-16 mx-auto text-yellow-500 mb-4" />
              <p className="text-gray-400">You need to be verified to browse the catalog</p>
            </div>
          ) : (
            <>
              {/* Search and Filter */}
              <div className="flex flex-col sm:flex-row gap-4 mb-6">
                <div className="relative flex-1">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search products..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="luxury-input pl-10 w-full"
                    data-testid="search-catalog"
                  />
                </div>
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="luxury-input"
                  data-testid="filter-category"
                >
                  <option value="">All Categories</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon} {cat.name}
                    </option>
                  ))}
                </select>
              </div>

              <p className="text-gray-400 mb-4">
                Found {filteredCatalog.length} products • 
                <span className="text-green-400"> {filteredCatalog.filter(p => p.isSelected).length} in your store</span>
              </p>

              {/* Catalog Grid */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                {filteredCatalog.map((product) => (
                  <div 
                    key={product.id} 
                    className={`bg-[rgba(30,30,30,0.6)] rounded-lg overflow-hidden border ${
                      product.isSelected 
                        ? 'border-green-500/50' 
                        : 'border-[rgba(212,175,55,0.1)] hover:border-[rgba(212,175,55,0.3)]'
                    } transition-all`}
                    data-testid="catalog-product"
                  >
                    <div className="h-36 bg-[rgba(50,50,50,0.6)] relative">
                      {product.images && product.images.length > 0 ? (
                        <img
                          src={product.images[0]}
                          alt={product.name || product.title}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full flex items-center justify-center">
                          <Package className="w-8 h-8 text-gray-500" />
                        </div>
                      )}
                      {product.isSelected && (
                        <span className="absolute top-2 right-2 px-2 py-1 bg-green-500/80 text-white rounded text-xs flex items-center gap-1">
                          <Check className="w-3 h-3" />
                          Added
                        </span>
                      )}
                      {product.categoryName && (
                        <span className="absolute top-2 left-2 px-2 py-1 bg-black/70 text-[#D4AF37] rounded text-xs">
                          {product.categoryIcon}
                        </span>
                      )}
                    </div>
                    
                    <div className="p-3">
                      <h3 className="font-semibold text-white text-sm mb-1 truncate">{product.name || product.title}</h3>
                      <p className="text-xs text-gray-400 mb-2 line-clamp-2">{product.description}</p>
                      <p className="text-[#D4AF37] font-bold">${(product.basePrice || product.price || 0).toFixed(2)}</p>
                      
                      {product.isSelected ? (
                        <button
                          onClick={() => handleRemoveFromStore(product.id)}
                          className="w-full mt-2 p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors text-sm flex items-center justify-center gap-1"
                          data-testid="remove-catalog-btn"
                        >
                          <Trash2 className="w-3 h-3" />
                          Remove
                        </button>
                      ) : (
                        <button
                          onClick={() => handleAddToStore(product)}
                          className="w-full mt-2 p-2 bg-[rgba(212,175,55,0.1)] hover:bg-[rgba(212,175,55,0.2)] text-[#D4AF37] rounded-lg transition-colors text-sm flex items-center justify-center gap-1"
                          data-testid="add-to-store-btn"
                        >
                          <Plus className="w-3 h-3" />
                          Add to Store
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      )}

      {/* Orders Section */}
      {activeTab === 'orders' && (
        <div className="luxury-card">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">My Orders</h2>
          
          {orders.length === 0 ? (
            <div className="text-center py-12">
              <ShoppingCart className="w-16 h-16 mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">No orders yet</p>
              <p className="text-gray-500 text-sm mt-2">Orders containing your products will appear here</p>
            </div>
          ) : (
            <div className="space-y-4">
              {/* Order Status Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
                <div className="p-4 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <Clock className="w-4 h-4 text-yellow-400" />
                    <span className="text-yellow-400 font-medium">Pending Payment</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {orders.filter(o => o.paymentStatus === 'pending_payment').length}
                  </p>
                </div>
                <div className="p-4 bg-green-500/10 border border-green-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <DollarSign className="w-4 h-4 text-green-400" />
                    <span className="text-green-400 font-medium">Paid</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {orders.filter(o => o.paymentStatus === 'paid').length}
                  </p>
                </div>
                <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <div className="flex items-center gap-2 mb-1">
                    <CheckCircle className="w-4 h-4 text-blue-400" />
                    <span className="text-blue-400 font-medium">Completed</span>
                  </div>
                  <p className="text-2xl font-bold text-white">
                    {orders.filter(o => o.paymentStatus === 'completed').length}
                  </p>
                </div>
              </div>

              {/* Orders List */}
              {orders.map((order) => (
                <div 
                  key={order.id} 
                  className={`p-5 rounded-lg border ${
                    order.paymentStatus === 'pending_payment' ? 'bg-yellow-500/5 border-yellow-500/30' :
                    order.paymentStatus === 'paid' ? 'bg-green-500/5 border-green-500/30' :
                    order.paymentStatus === 'completed' ? 'bg-blue-500/5 border-blue-500/30' :
                    'bg-[rgba(30,30,30,0.6)] border-[rgba(212,175,55,0.1)]'
                  }`}
                  data-testid="seller-order"
                >
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <p className="text-white font-semibold text-lg">
                        Order #{order.id?.slice(0, 8).toUpperCase()}
                      </p>
                      <p className="text-sm text-gray-400">
                        {new Date(order.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                          hour: '2-digit',
                          minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <span className={`status-badge ${
                        order.paymentStatus === 'paid' || order.paymentStatus === 'completed' ? 'status-verified' :
                        order.paymentStatus === 'pending_payment' ? 'status-pending' :
                        'status-rejected'
                      }`}>
                        {order.paymentStatus?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>

                  {/* Order Items */}
                  <div className="space-y-3 border-t border-[rgba(212,175,55,0.1)] pt-4">
                    <p className="text-sm text-gray-400 mb-2">Products in this order:</p>
                    {order.orderItems?.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-4 p-3 bg-[rgba(20,20,20,0.6)] rounded-lg">
                        {item.product?.images?.[0] ? (
                          <img
                            src={item.product.images[0]}
                            alt={item.product.title}
                            className="w-16 h-16 object-cover rounded-lg"
                          />
                        ) : (
                          <div className="w-16 h-16 bg-[rgba(50,50,50,0.6)] rounded-lg flex items-center justify-center">
                            <Package className="w-6 h-6 text-gray-500" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="text-white font-medium">{item.product?.title || 'Product'}</p>
                          <p className="text-sm text-gray-400">Quantity: {item.quantity}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-[#D4AF37] font-bold">${(item.price * item.quantity).toFixed(2)}</p>
                          <p className="text-xs text-gray-500">${item.price?.toFixed(2)} each</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Order Total */}
                  <div className="flex justify-between items-center mt-4 pt-4 border-t border-[rgba(212,175,55,0.1)]">
                    <span className="text-gray-400">Your earnings from this order:</span>
                    <span className="text-[#D4AF37] font-bold text-xl">
                      ${order.orderItems?.reduce((sum, item) => sum + (item.price * item.quantity), 0).toFixed(2)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Wallet Section */}
      {activeTab === 'wallet' && (
        <div className="luxury-card mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">My Wallet</h2>
            <button
              onClick={() => setShowRechargeModal(true)}
              className="luxury-button flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Recharge Wallet
            </button>
          </div>

          {/* Wallet Balance Card */}
          <div className="mb-8">
            <div className="bg-gradient-to-br from-[#1a1a1a] to-[#0a0a0a] rounded-xl border-2 border-[#D4AF37] p-6 shadow-lg">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-12 h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center">
                    <Wallet className="w-6 h-6 text-[#D4AF37]" />
                  </div>
                  <div>
                    <p className="text-gray-400 text-sm">Current Balance</p>
                    <p className="text-4xl font-bold text-[#D4AF37]">
                      ${walletBalance ? walletBalance.balance.toFixed(2) : '0.00'}
                    </p>
                  </div>
                </div>
                <button
                  onClick={fetchWalletBalance}
                  className="text-gray-400 hover:text-[#D4AF37] transition-colors p-2"
                  title="Refresh Balance"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 11-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
                    <path d="M21 3v5h-5" />
                  </svg>
                </button>
              </div>
              {walletBalance?.updatedAt && (
                <p className="text-xs text-gray-500">
                  Last updated: {new Date(walletBalance.updatedAt).toLocaleString()}
                </p>
              )}
            </div>
          </div>

          {/* Wallet Summary Stats */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
            <div className="p-4 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.2)]">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-green-400" />
                <p className="text-gray-400 text-sm">Total Approved Recharges</p>
              </div>
              <p className="text-2xl font-bold text-green-400">
                ${walletBalance ? walletBalance.approvedRecharges.toFixed(2) : '0.00'}
              </p>
            </div>
            <div className="p-4 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.2)]">
              <div className="flex items-center gap-2 mb-2">
                <Clock className="w-4 h-4 text-yellow-400" />
                <p className="text-gray-400 text-sm">Pending Recharges</p>
              </div>
              <p className="text-2xl font-bold text-yellow-400">
                ${walletBalance ? walletBalance.pendingRecharges.toFixed(2) : '0.00'}
              </p>
            </div>
            <div className="p-4 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.2)]">
              <div className="flex items-center gap-2 mb-2">
                <DollarSign className="w-4 h-4 text-[#D4AF37]" />
                <p className="text-gray-400 text-sm">Available Balance</p>
              </div>
              <p className="text-2xl font-bold text-[#D4AF37]">
                ${walletBalance ? walletBalance.balance.toFixed(2) : '0.00'}
              </p>
            </div>
          </div>

          {/* How to Recharge Info */}
          <div className="mb-8 p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
            <h3 className="text-lg font-semibold text-white mb-2 flex items-center gap-2">
              <AlertCircle className="w-5 h-5 text-blue-400" />
              How to Recharge Your Wallet
            </h3>
            <ol className="list-decimal list-inside text-sm text-gray-300 space-y-2">
              <li>Click the "Recharge Wallet" button above</li>
              <li>Send USDT (TRC20) to the provided wallet address</li>
              <li>Enter the transaction hash from your wallet app</li>
              <li>Submit your recharge request for admin approval</li>
              <li>Once approved, your balance will be updated automatically</li>
            </ol>
          </div>

          {/* Recharge History */}
          <div className="border-t border-[rgba(212,175,55,0.1)] pt-6">
            <h3 className="text-lg font-semibold text-white mb-4">Recharge History</h3>
            {rechargeHistory.length === 0 ? (
              <p className="text-gray-400 text-center py-8">No recharge requests yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[rgba(212,175,55,0.2)]">
                      <th className="text-left p-3 text-gray-400 font-medium">Date</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Amount</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Transaction Hash</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rechargeHistory.map((req) => (
                      <tr key={req.id} className="border-b border-[rgba(212,175,55,0.1)]">
                        <td className="p-3 text-gray-300 text-sm">
                          {req.createdAt ? new Date(req.createdAt).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric'
                          }) : '—'}
                        </td>
                        <td className="p-3 text-[#D4AF37] font-semibold">
                          ${parseFloat(req.amount || 0).toFixed(2)}
                        </td>
                        <td className="p-3 text-gray-400 hidden md:table-cell">
                          <span className="text-xs font-mono truncate max-w-[200px] inline-block" title={req.transactionHash}>
                            {req.transactionHash || 'N/A'}
                          </span>
                        </td>
                        <td className="p-3">
                          <span className={`status-badge ${
                            req.status === 'approved' ? 'status-verified' :
                            req.status === 'rejected' ? 'status-rejected' :
                            'status-pending'
                          }`}>
                            {req.status}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Payouts Section */}
      {activeTab === 'payouts' && (
        <div className="luxury-card mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Payouts & Earnings</h2>
            <button
              onClick={() => setShowRechargeModal(true)}
              className="luxury-button flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Recharge Wallet
            </button>
          </div>

          {!earnings ? (
            <p className="text-gray-400 text-center py-8">Earnings data is not available yet.</p>
          ) : (
            <div className="space-y-8">
              {/* Summary */}
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div className="p-4 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.2)]">
                  <p className="text-gray-400 text-sm mb-1">Total Earnings</p>
                  <p className="text-2xl font-bold text-green-400">${earnings.totalEarnings.toFixed(2)}</p>
                </div>
                <div className="p-4 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.2)]">
                  <p className="text-gray-400 text-sm mb-1">Available Balance</p>
                  <p className="text-2xl font-bold text-[#D4AF37]">${earnings.availableBalance.toFixed(2)}</p>
                </div>
                <div className="p-4 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.2)]">
                  <p className="text-gray-400 text-sm mb-1">Pending Withdrawals</p>
                  <p className="text-2xl font-bold text-yellow-400">${earnings.pendingWithdrawals.toFixed(2)}</p>
                </div>
              </div>

              {/* Payout Request Form */}
              <div className="border-t border-[rgba(212,175,55,0.1)] pt-6">
                <h3 className="text-lg font-semibold text-white mb-2">Request Payout</h3>
                <div className="mb-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                  <p className="text-sm text-blue-300 flex items-start gap-2">
                    <Wallet className="w-4 h-4 mt-0.5 flex-shrink-0" />
                    <span>
                      <strong>Important:</strong> You must provide a valid USDT TRC20 wallet address to receive your payout. 
                      TRC20 addresses start with 'T' and are exactly 34 characters long.
                    </span>
                  </p>
                </div>
                <p className="text-xs text-gray-500 mb-4">
                  Payouts are processed manually by admin. You can request a payout up to your available balance.
                </p>
                <form
                  className="space-y-4"
                  onSubmit={async (e) => {
                    e.preventDefault();
                    if (!earnings) return;
                    const amount = parseFloat(payoutAmount || '0');
                    if (!amount || amount <= 0) {
                      toast.error('Enter a valid amount');
                      return;
                    }
                    if (amount > earnings.availableBalance) {
                      toast.error('Amount exceeds available balance');
                      return;
                    }
                    if (!payoutWallet || payoutWallet.trim() === '') {
                      toast.error('Please enter your wallet address');
                      return;
                    }
                    try {
                      setPayoutSubmitting(true);
                      await api.post('/seller/payout-requests', {
                        requestedAmount: amount,
                        payoutWallet: payoutWallet.trim(),
                      });
                      toast.success('Payout request submitted');
                      setPayoutAmount('');
                      setPayoutWallet('');
                      await fetchEarnings();
                    } catch (error) {
                      toast.error(error.response?.data?.detail || 'Failed to submit payout request');
                    } finally {
                      setPayoutSubmitting(false);
                    }
                  }}
                >
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Amount to withdraw (USD)
                      </label>
                      <input
                        type="number"
                        min="0"
                        step="0.01"
                        value={payoutAmount}
                        onChange={(e) => setPayoutAmount(e.target.value)}
                        className="luxury-input w-full"
                        placeholder="Enter amount"
                        required
                      />
                    </div>
                    <div className="flex-1">
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        USDT TRC20 Wallet Address <span className="text-red-400">*</span>
                      </label>
                      <input
                        type="text"
                        value={payoutWallet}
                        onChange={(e) => setPayoutWallet(e.target.value)}
                        className="luxury-input w-full font-mono text-sm"
                        placeholder="Enter your TRC20 wallet address (starts with T)"
                        minLength={34}
                        maxLength={34}
                        pattern="T[A-Za-z0-9]{33}"
                        title="Must be a valid TRC20 wallet address (34 characters, starts with T)"
                        required
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        ⓘ Must be a valid USDT TRC20 wallet address (34 characters, starts with 'T')
                      </p>
                    </div>
                  </div>
                  <button
                    type="submit"
                    disabled={payoutSubmitting || !earnings || earnings.availableBalance <= 0}
                    className="btn-gold whitespace-nowrap disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {payoutSubmitting ? 'Submitting...' : 'Request Payout'}
                  </button>
                </form>
              </div>

              {/* Payout History */}
              <div className="border-t border-[rgba(212,175,55,0.1)] pt-6">
                <h3 className="text-lg font-semibold text-white mb-4">Payout Requests History</h3>
                {(!earnings.payoutRequests || earnings.payoutRequests.length === 0) ? (
                  <p className="text-gray-400 text-sm">No payout requests yet.</p>
                ) : (
                  <div className="overflow-x-auto">
                    <table className="min-w-full text-sm">
                      <thead>
                        <tr className="text-left text-gray-400 border-b border-[rgba(212,175,55,0.1)]">
                          <th className="py-2 pr-4">Date</th>
                          <th className="py-2 pr-4">Amount</th>
                          <th className="py-2 pr-4">Wallet Address</th>
                          <th className="py-2 pr-4">Status</th>
                          <th className="py-2 pr-4">Admin Note</th>
                        </tr>
                      </thead>
                      <tbody>
                        {earnings.payoutRequests.map((p) => (
                          <tr key={p.id} className="border-b border-[rgba(212,175,55,0.05)]">
                            <td className="py-2 pr-4 text-gray-300">
                              {p.requestDate
                                ? new Date(p.requestDate).toLocaleDateString('en-US', {
                                    year: 'numeric',
                                    month: 'short',
                                    day: 'numeric',
                                  })
                                : '—'}
                            </td>
                            <td className="py-2 pr-4 text-[#D4AF37] font-semibold">
                              ${p.requestedAmount?.toFixed(2)}
                            </td>
                            <td className="py-2 pr-4 font-mono text-xs text-gray-400">
                              {p.payoutWallet ? (
                                <span className="truncate max-w-[150px] inline-block" title={p.payoutWallet}>
                                  {p.payoutWallet}
                                </span>
                              ) : (
                                '—'
                              )}
                            </td>
                            <td className="py-2 pr-4">
                              <span
                                className={`status-badge ${
                                  p.status === 'pending'
                                    ? 'status-pending'
                                    : p.status === 'approved'
                                    ? 'status-verified'
                                    : p.status === 'paid'
                                    ? 'status-verified'
                                    : 'status-rejected'
                                }`}
                              >
                                {p.status}
                              </span>
                            </td>
                            <td className="py-2 pr-4 text-xs text-gray-400 max-w-xs truncate">
                              {p.adminNote || '—'}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Order Center Section */}
      {activeTab === 'orderCenter' && (
        <OrderCenter />
      )}

      {/* Wallet Recharge Modal */}
      {showRechargeModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Recharge Wallet</h2>
              <button
                onClick={() => setShowRechargeModal(false)}
                className="text-gray-400 hover:text-white"
              >
                ✕
              </button>
            </div>

            <div className="space-y-6">
              {/* Payment Instructions */}
              <div className="p-4 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                <p className="text-sm text-blue-300 mb-3">
                  <strong>Payment Instructions:</strong>
                </p>
                <ol className="text-sm text-blue-200 space-y-2 list-decimal list-inside">
                  <li>Send USDT (TRC20) to the wallet address below</li>
                  <li>Scan the QR code or copy the wallet address</li>
                  <li>After completing payment, enter the transaction hash</li>
                  <li>Submit the recharge request for admin approval</li>
                </ol>
              </div>

              {/* Wallet Address & QR Code */}
              <div className="p-6 bg-[rgba(30,30,30,0.8)] rounded-lg border border-[rgba(212,175,55,0.3)]">
                <div className="text-center space-y-4">
                  <p className="text-gray-400 text-sm">USDT TRC20 Wallet Address</p>
                  <div className="flex items-center justify-center gap-2 p-3 bg-[rgba(20,20,20,0.8)] rounded-lg">
                    <code className="text-[#D4AF37] font-mono text-sm break-all">
                      TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
                    </code>
                    <button
                      onClick={() => {
                        navigator.clipboard.writeText('TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU');
                        toast.success('Wallet address copied!');
                      }}
                      className="text-[#D4AF37] hover:text-[#f4c542] flex-shrink-0"
                      title="Copy address"
                    >
                      📋
                    </button>
                  </div>

                  {/* QR Code */}
                  <div className="flex justify-center my-6">
                    <img 
                      src="https://customer-assets.emergentagent.com/job_clone-master-88/artifacts/avpblbp4_Screenshot%202025-12-12%20at%201.41.52%E2%80%AFPM.png"
                      alt="USDT TRC20 QR Code"
                      className="w-64 h-64 rounded-lg border-2 border-[rgba(212,175,55,0.3)]"
                    />
                  </div>

                  <p className="text-xs text-gray-500">
                    Scan this QR code with your USDT TRC20 wallet app
                  </p>
                </div>
              </div>

              {/* Recharge Form */}
              <form onSubmit={handleRechargeSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Recharge Amount (USD) <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="number"
                    min="1"
                    step="0.01"
                    value={rechargeAmount}
                    onChange={(e) => setRechargeAmount(e.target.value)}
                    className="luxury-input w-full"
                    placeholder="Enter amount in USD"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Enter the amount you sent in USD
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Transaction Hash <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    value={transactionHash}
                    onChange={(e) => setTransactionHash(e.target.value)}
                    className="luxury-input w-full font-mono text-sm"
                    placeholder="Enter your transaction hash (TxID)"
                    required
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    You can find this in your wallet app after sending USDT
                  </p>
                </div>

                <div className="flex gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowRechargeModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-600 text-gray-300 rounded-lg hover:bg-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={rechargeSubmitting}
                    className="flex-1 luxury-button"
                  >
                    {rechargeSubmitting ? 'Submitting...' : 'Submit Request'}
                  </button>
                </div>
              </form>

              {/* Recharge History */}
              {rechargeHistory.length > 0 && (
                <div className="border-t border-[rgba(212,175,55,0.1)] pt-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Recent Recharge Requests</h3>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {rechargeHistory.slice(0, 5).map((req) => (
                      <div 
                        key={req.id} 
                        className="p-3 bg-[rgba(20,20,20,0.6)] rounded-lg flex justify-between items-center"
                      >
                        <div>
                          <p className="text-white font-medium">${req.amount.toFixed(2)}</p>
                          <p className="text-xs text-gray-500">
                            {new Date(req.createdAt).toLocaleDateString()}
                          </p>
                        </div>
                        <span
                          className={`status-badge ${
                            req.status === 'pending'
                              ? 'status-pending'
                              : req.status === 'approved'
                              ? 'status-verified'
                              : 'status-rejected'
                          }`}
                        >
                          {req.status}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SellerDashboard;
