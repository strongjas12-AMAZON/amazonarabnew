import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { supabase } from '../../lib/supabase';
import { toast } from 'sonner';
import { 
  Users, Package, ShoppingCart, Code, CheckCircle, XCircle, Eye, 
  Clock, DollarSign, Trash2, Plus, Edit, Search, Database, 
  ToggleLeft, ToggleRight, X, Save, AlertTriangle
} from 'lucide-react';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [allUsers, setAllUsers] = useState([]);
  const [usersPage, setUsersPage] = useState(1);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [verificationDocs, setVerificationDocs] = useState([]);
  const [inviteCodes, setInviteCodes] = useState([]);
  const [storeNameRequests, setStoreNameRequests] = useState([]);
  const [payoutRequests, setPayoutRequests] = useState([]);
  const [rechargeRequests, setRechargeRequests] = useState([]);
  const [sellerRechargeRequests, setSellerRechargeRequests] = useState([]);
  const [depositConfirmations, setDepositConfirmations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);
  
  // NEW: Escrow system states
  const [platformBalance, setPlatformBalance] = useState(null);
  const [shippingOrderId, setShippingOrderId] = useState(null);
  
  // Product form state
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [productForm, setProductForm] = useState({
    title: '',
    description: '',
    price: '',
    category: '',
    images: []
  });
  const [seedingCatalog, setSeedingCatalog] = useState(false);

  // Password reset modal state (admin-triggered)
  const [passwordResetModal, setPasswordResetModal] = useState(null); // { userId, email, name } while awaiting response
  const [passwordResetResult, setPasswordResetResult] = useState(null); // { email, reset_link, email_sent } after response
  const [passwordResetLoading, setPasswordResetLoading] = useState(false);
  const [resetLinkCopied, setResetLinkCopied] = useState(false);

  const USERS_PER_PAGE = 10;

  // Calculate pagination for users (client-side)
  const usersTotalPages = Math.max(1, Math.ceil(allUsers.length / USERS_PER_PAGE));
  const startIndex = (usersPage - 1) * USERS_PER_PAGE;
  const endIndex = startIndex + USERS_PER_PAGE;
  const users = allUsers.slice(startIndex, endIndex);

  useEffect(() => {
    fetchData();
    fetchCategories();
    fetchPlatformBalance(); // NEW: Fetch platform balance
  }, []);

  // Throttled version of fetchData for real-time subscription triggers.
  // Real-time events can fire rapidly in bursts (e.g. when an order is paid,
  // multiple rows change across orders/platform_balance/wallet_transactions
  // within milliseconds). Without throttling, each event would spawn 10
  // parallel API requests, increasing the chance that one fails transiently.
  const lastRefreshRef = useRef(0);
  const pendingRefreshRef = useRef(null);
  const throttledRefresh = useCallback(() => {
    const MIN_INTERVAL = 1500; // at most one full refresh every 1.5s
    const now = Date.now();
    const elapsed = now - lastRefreshRef.current;

    if (elapsed >= MIN_INTERVAL) {
      lastRefreshRef.current = now;
      fetchData();
      fetchPlatformBalance();
      return;
    }

    // Coalesce burst of events into a single trailing refresh
    if (pendingRefreshRef.current) return;
    pendingRefreshRef.current = setTimeout(() => {
      pendingRefreshRef.current = null;
      lastRefreshRef.current = Date.now();
      fetchData();
      fetchPlatformBalance();
    }, MIN_INTERVAL - elapsed);
  }, []);

  // Real-time subscription for platform balance updates
  useEffect(() => {
    if (!user) return;

    console.log('Setting up admin real-time subscriptions...');

    // Subscribe to platform_balance table updates
    const platformBalanceChannel = supabase
      .channel('admin-platform-balance-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'platform_balance'
      }, (payload) => {
        console.log('Platform balance update received:', payload.eventType);
        fetchPlatformBalance();
      })
      .subscribe((status) => {
        console.log('Platform balance channel subscription status:', status);
      });

    // Subscribe to platform_transactions (affects platform balance)
    const platformTransactionsChannel = supabase
      .channel('admin-platform-transactions-changes')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'platform_transactions'
      }, (payload) => {
        console.log('Platform transaction update received:', payload.eventType);
        fetchPlatformBalance();
      })
      .subscribe((status) => {
        console.log('Platform transactions channel subscription status:', status);
      });

    // Subscribe to orders table (order payments affect balance)
    const ordersChannel = supabase
      .channel('admin-orders-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'orders'
      }, (payload) => {
        console.log('Order update received:', payload.eventType);
        throttledRefresh();
      })
      .subscribe((status) => {
        console.log('Orders channel subscription status:', status);
      });

    // Subscribe to order_deposits table (seller deposits affect balance)
    const depositsChannel = supabase
      .channel('admin-deposits-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'order_deposits'
      }, (payload) => {
        console.log('Deposit update received:', payload.eventType);
        throttledRefresh();
      })
      .subscribe((status) => {
        console.log('Deposits channel subscription status:', status);
      });

    // Subscribe to wallet_transactions (buyer/seller wallet changes)
    const walletTransactionsChannel = supabase
      .channel('admin-wallet-transactions-changes')
      .on('postgres_changes', {
        event: 'INSERT',
        schema: 'public',
        table: 'wallet_transactions'
      }, (payload) => {
        console.log('Wallet transaction update received:', payload.eventType);
        fetchPlatformBalance();
      })
      .subscribe((status) => {
        console.log('Wallet transactions channel subscription status:', status);
      });

    // Cleanup function
    return () => {
      console.log('Cleaning up admin real-time subscriptions...');
      supabase.removeChannel(platformBalanceChannel);
      supabase.removeChannel(platformTransactionsChannel);
      supabase.removeChannel(ordersChannel);
      supabase.removeChannel(depositsChannel);
      supabase.removeChannel(walletTransactionsChannel);
    };
  }, [user, throttledRefresh]);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to load categories');
    }
  };
  
  // NEW: Fetch platform balance
  const fetchPlatformBalance = async () => {
    try {
      const res = await api.get('/admin/platform-wallet');
      setPlatformBalance(res.data || null);
    } catch (error) {
      console.error('Failed to load platform balance', error);
    }
  };

  // Send a secure password reset link to a user (admin-triggered)
  const handleSendPasswordReset = async (user) => {
    // Support both {id} (direct user row) and {userId} (modal state shape)
    const targetUserId = user?.id || user?.userId;
    const targetEmail = user?.email;
    if (!targetUserId) {
      toast.error('Missing user id. Please try again.');
      return;
    }
    setPasswordResetLoading(true);
    setResetLinkCopied(false);
    try {
      const res = await api.post(`/admin/users/${targetUserId}/send-password-reset`);
      setPasswordResetResult({
        email: res.data?.email || targetEmail,
        reset_link: res.data?.reset_link || '',
        email_sent: !!res.data?.email_sent,
        message: res.data?.message || '',
      });
      if (res.data?.email_sent) {
        toast.success('Password reset email sent');
      } else {
        toast.info('Reset link generated. Share it manually with the user.');
      }
    } catch (error) {
      const detail = error?.response?.data?.detail || 'Failed to generate reset link';
      toast.error(detail);
      setPasswordResetModal(null);
    } finally {
      setPasswordResetLoading(false);
    }
  };

  const closePasswordResetModal = () => {
    setPasswordResetModal(null);
    setPasswordResetResult(null);
    setResetLinkCopied(false);
  };

  const copyResetLink = async () => {
    if (!passwordResetResult?.reset_link) return;
    try {
      await navigator.clipboard.writeText(passwordResetResult.reset_link);
      setResetLinkCopied(true);
      toast.success('Reset link copied to clipboard');
      setTimeout(() => setResetLinkCopied(false), 2500);
    } catch (e) {
      toast.error('Could not copy. Select and copy manually.');
    }
  };


  
  // NEW: Ship order by platform
  const handleShipByPlatform = async (orderId) => {
    const trackingNumber = prompt('Enter tracking number (optional):');
    const courierName = prompt('Enter courier name (optional):');
    
    try {
      setShippingOrderId(orderId);
      await api.post(`/orders/${orderId}/ship-by-platform`, {
        trackingNumber: trackingNumber || undefined,
        courierName: courierName || undefined
      });
      toast.success('Order marked as shipped by platform!');
      await fetchData();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to ship order';
      toast.error(errorMsg);
    } finally {
      setShippingOrderId(null);
    }
  };

  const fetchData = async () => {
    setLoading(true);

    // Use Promise.allSettled so each request is handled independently
    // This way if one fails, others can still succeed
    const results = await Promise.allSettled([
      api.get('/admin/users').catch(err => ({ error: err })),
      api.get('/orders/my').catch(err => ({ error: err })),
      api.get('/admin/products').catch(err => ({ error: err })),
      api.get('/verification/documents').catch(err => ({ error: err })),
      api.get('/admin/invite-codes').catch(err => ({ error: err })),
      api.get('/admin/store-name-requests').catch(err => ({ error: err })),
      api.get('/admin/payout-requests').catch(err => ({ error: err })),
      api.get('/admin/wallet-recharge-requests').catch(err => ({ error: err })),
      api.get('/admin/seller-wallet-recharge-requests').catch(err => ({ error: err })),
      api.get('/admin/deposit-confirmations').catch(err => ({ error: err }))
    ]);

    // Helper: update state ONLY on successful fetch.
    // On transient failure (network hiccup, token refresh, etc.) we preserve
    // the last known good data instead of wiping the UI to empty arrays.
    const applyResult = (index, label, dataKey, setter) => {
      const r = results[index];
      if (r.status === 'fulfilled' && !r.value?.error) {
        const data = r.value?.data?.[dataKey];
        setter(Array.isArray(data) ? data : []);
      } else {
        // Log details for developers but don't show a scary toast or wipe state.
        const err = r.status === 'fulfilled' ? r.value?.error : r.reason;
        const status = err?.response?.status;
        const detail = err?.response?.data?.detail || err?.message || 'unknown error';
        // eslint-disable-next-line no-console
        console.warn(`[AdminDashboard] Failed to load ${label}: status=${status || 'n/a'} - ${detail}`);
      }
    };

    try {
      applyResult(0, 'users', 'users', setAllUsers);
      applyResult(1, 'orders', 'orders', setOrders);
      applyResult(2, 'products', 'products', setProducts);
      applyResult(3, 'verification documents', 'documents', setVerificationDocs);
      applyResult(4, 'invite codes', 'codes', setInviteCodes);
      applyResult(5, 'store name requests', 'requests', setStoreNameRequests);
      applyResult(6, 'payout requests', 'requests', setPayoutRequests);
      applyResult(7, 'recharge requests', 'requests', setRechargeRequests);
      applyResult(8, 'seller recharge requests', 'requests', setSellerRechargeRequests);
      applyResult(9, 'deposit confirmations', 'deposits', setDepositConfirmations);
    } catch (error) {
      // Silently handle errors - individual requests already handled above
      // eslint-disable-next-line no-console
      console.error('[AdminDashboard] Unexpected error processing results:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateInviteCode = async () => {
    try {
      const response = await api.post('/admin/invite-codes');
      toast.success(`Invite code created: ${response.data.inviteCode.code}`);
      fetchData();
    } catch (error) {
      toast.error('Failed to create invite code');
    }
  };

  const handleDeleteProduct = async (productId, productTitle) => {
    if (!window.confirm(`Are you sure you want to delete "${productTitle}"?`)) return;
    try {
      await api.delete(`/admin/products/${productId}`);
      toast.success('Product deleted');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete product');
    }
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      await api.post('/admin/products', {
        ...productForm,
        price: parseFloat(productForm.price),
        category: productForm.category || null
      });
      toast.success('Product created successfully');
      setShowProductForm(false);
      resetProductForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create product');
    }
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/admin/products/${editingProduct}`, {
        title: productForm.title,
        description: productForm.description,
        price: parseFloat(productForm.price),
        category: productForm.category || null
      });
      toast.success('Product updated');
      setEditingProduct(null);
      resetProductForm();
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update product');
    }
  };

  const resetProductForm = () => {
    setProductForm({ title: '', description: '', price: '', category: '', images: [] });
  };

  const handleSeedCatalog = async () => {
    if (!window.confirm('This will seed the catalog with 100 sample products. Continue?')) return;
    setSeedingCatalog(true);
    try {
      const response = await api.post('/admin/seed-catalog');
      if (response.data.success) {
        toast.success(response.data.message);
        fetchData();
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to seed catalog');
    } finally {
      setSeedingCatalog(false);
    }
  };

  const handleClearCatalog = async () => {
    if (!window.confirm('⚠️ This will DELETE all products. Are you absolutely sure?')) return;
    if (!window.confirm('This action cannot be undone. Final confirmation?')) return;
    try {
      const response = await api.delete('/admin/clear-catalog');
      toast.success(response.data.message);
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to clear catalog');
    }
  };

  const handleReviewVerification = async (docId, status, rejectionReason = '') => {
    try {
      await api.put(`/verification/documents/${docId}/review`, {
        status,
        rejectionReason
      });
      toast.success(`Verification ${status}`);
      fetchData();
    } catch (error) {
      toast.error('Failed to review verification');
    }
  };

  const handleConfirmPayment = async (orderId) => {
    try {
      await api.put(`/orders/${orderId}/status`, { status: 'paid' });
      toast.success('✅ Payment confirmed! Order marked as paid.');
      fetchData();
    } catch (error) {
      toast.error('Failed to confirm payment');
    }
  };

  const handleMarkCompleted = async (orderId) => {
    try {
      await api.put(`/orders/${orderId}/status`, { status: 'completed' });
      toast.success('✅ Order marked as completed!');
      fetchData();
    } catch (error) {
      toast.error('Failed to update order');
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    try {
      await api.put(`/orders/${orderId}/status`, { status: 'cancelled' });
      toast.success('Order cancelled successfully');
      fetchData();
    } catch (error) {
      toast.error('Failed to cancel order');
    }
  };

  const handleCompleteOrder = async (orderId) => {
    try {
      await api.put(`/orders/${orderId}/status`, { status: 'completed' });
      toast.success('✅ Order marked as completed!');
      fetchData();
    } catch (error) {
      toast.error('Failed to complete order');
    }
  };

  // Filter products
  const filteredProducts = products.filter(p => {
    const matchesSearch = p.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                          p.description?.toLowerCase().includes(searchTerm.toLowerCase());
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

  const pendingPaymentOrders = orders.filter(o => o.paymentStatus === 'pending_payment');
  const paidOrders = orders.filter(o => o.paymentStatus === 'paid');
  const completedOrders = orders.filter(o => o.paymentStatus === 'completed');
  const pendingPayoutRequests = payoutRequests.filter(p => p.status === 'pending');

  const bannedUsers = allUsers.filter(
    (u) => u.banStatus && u.banStatus !== 'active'
  );

  const stats = {
    totalUsers: allUsers.length,
    buyers: allUsers.filter(u => u.role === 'buyer').length,
    sellers: allUsers.filter(u => u.role === 'seller').length,
    verifiedSellers: allUsers.filter(u => u.role === 'seller' && u.verificationStatus === 'verified').length,
    pendingVerifications: verificationDocs.filter(d => d.status === 'pending').length,
    totalProducts: products.length,
    totalOrders: orders.length,
    pendingPayments: pendingPaymentOrders.length,
    paidOrders: paidOrders.length,
    completedOrders: completedOrders.length,
    pendingPayouts: pendingPayoutRequests.length,
    totalRevenue: orders.filter(o => ['paid', 'completed'].includes(o.paymentStatus))
      .reduce((sum, o) => sum + parseFloat(o.totalAmount || 0), 0)
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-2" data-testid="admin-dashboard-title">
          Admin Dashboard
        </h1>
        <p className="text-gray-400">Manage your marketplace catalog and operations</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 flex-wrap">
        {['overview', 'products', 'orders', 'users', 'verifications', 'inviteCodes', 'bannedUsers', 'storeRequests', 'payoutRequests', 'depositConfirmations', 'wallets'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-4 py-2 rounded-lg font-medium transition-all ${
              activeTab === tab
                ? 'bg-[#D4AF37] text-[#0a0a0a]'
                : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
            }`}
            data-testid={`tab-${tab}`}
          >
            {tab === 'overview' && <Users className="w-4 h-4 inline mr-2" />}
            {tab === 'products' && <Package className="w-4 h-4 inline mr-2" />}
            {tab === 'orders' && <ShoppingCart className="w-4 h-4 inline mr-2" />}
            {tab === 'users' && <Users className="w-4 h-4 inline mr-2" />}
            {tab === 'verifications' && <CheckCircle className="w-4 h-4 inline mr-2" />}
            {tab === 'inviteCodes' && <Code className="w-4 h-4 inline mr-2" />}
            {tab === 'depositConfirmations' && <DollarSign className="w-4 h-4 inline mr-2" />}
            {tab.charAt(0).toUpperCase() + tab.slice(1).replace(/([A-Z])/g, ' $1')}
            {tab === 'depositConfirmations' && depositConfirmations.length > 0 && (
              <span className="ml-2 bg-orange-500 text-white text-xs px-2 py-0.5 rounded-full">
                {depositConfirmations.length}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Product Form Modal */}
      {(showProductForm || editingProduct) && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="bg-[#1a1a1a] rounded-lg border border-[rgba(212,175,55,0.3)] max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">
                  {editingProduct ? 'Edit Product' : 'Add New Product'}
                </h2>
                <button
                  onClick={() => {
                    setShowProductForm(false);
                    setEditingProduct(null);
                    resetProductForm();
                  }}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              <form onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct} className="space-y-4">
                {/* Product Title */}
                <div>
                  <label className="block text-gray-300 mb-2 font-medium">
                    Product Title <span className="text-red-400">*</span>
                  </label>
                  <input
                    type="text"
                    required
                    value={productForm.title}
                    onChange={(e) => setProductForm({ ...productForm, title: e.target.value })}
                    placeholder="Enter product title"
                    className="luxury-input w-full"
                    data-testid="product-title-input"
                  />
                </div>

                {/* Product Description */}
                <div>
                  <label className="block text-gray-300 mb-2 font-medium">
                    Description <span className="text-red-400">*</span>
                  </label>
                  <textarea
                    required
                    value={productForm.description}
                    onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
                    placeholder="Enter product description"
                    rows={4}
                    className="luxury-input w-full resize-none"
                    data-testid="product-description-input"
                  />
                </div>

                {/* Price and Category Row */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  {/* Price */}
                  <div>
                    <label className="block text-gray-300 mb-2 font-medium">
                      Price (USD) <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="number"
                      required
                      min="0"
                      step="0.01"
                      value={productForm.price}
                      onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                      placeholder="0.00"
                      className="luxury-input w-full"
                      data-testid="product-price-input"
                    />
                  </div>

                  {/* Category */}
                  <div>
                    <label className="block text-gray-300 mb-2 font-medium">
                      Category <span className="text-red-400">*</span>
                    </label>
                    <select
                      required
                      value={productForm.category}
                      onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                      className="luxury-input w-full"
                      data-testid="product-category-select"
                    >
                      <option value="">Select Category</option>
                      {categories.map((cat) => (
                        <option key={cat.id} value={cat.id}>
                          {cat.icon} {cat.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Image URL Input */}
                <div>
                  <label className="block text-gray-300 mb-2 font-medium">
                    Product Images
                  </label>
                  <div className="space-y-2">
                    {productForm.images.map((img, index) => (
                      <div key={index} className="flex gap-2">
                        <input
                          type="url"
                          value={img}
                          onChange={(e) => {
                            const newImages = [...productForm.images];
                            newImages[index] = e.target.value;
                            setProductForm({ ...productForm, images: newImages });
                          }}
                          placeholder="https://example.com/image.jpg"
                          className="luxury-input flex-1"
                        />
                        <button
                          type="button"
                          onClick={() => {
                            const newImages = productForm.images.filter((_, i) => i !== index);
                            setProductForm({ ...productForm, images: newImages });
                          }}
                          className="px-3 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                    <button
                      type="button"
                      onClick={() => {
                        setProductForm({ ...productForm, images: [...productForm.images, ''] });
                      }}
                      className="w-full px-4 py-2 bg-[rgba(212,175,55,0.1)] text-[#D4AF37] rounded-lg hover:bg-[rgba(212,175,55,0.2)] transition-colors flex items-center justify-center gap-2"
                    >
                      <Plus className="w-4 h-4" />
                      Add Image URL
                    </button>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">
                    Add URLs to product images. You can add multiple images.
                  </p>
                </div>

                {/* Action Buttons */}
                <div className="flex gap-3 pt-4">
                  <button
                    type="submit"
                    className="flex-1 btn-gold flex items-center justify-center gap-2"
                    data-testid="submit-product-btn"
                  >
                    <Save className="w-4 h-4" />
                    {editingProduct ? 'Update Product' : 'Create Product'}
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      setShowProductForm(false);
                      setEditingProduct(null);
                      resetProductForm();
                    }}
                    className="flex-1 px-4 py-2 bg-[rgba(30,30,30,0.6)] text-gray-300 rounded-lg hover:bg-[rgba(30,30,30,0.8)] transition-colors"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}


      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <div>
          {/* NEW: Platform Balance Card */}
          {platformBalance && (
            <div className="luxury-card mb-6 bg-gradient-to-br from-[#D4AF37]/10 to-[#1a1a1a] border-2 border-[#D4AF37]">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-['Playfair_Display'] text-xl font-bold text-white">Platform Balance (Escrow)</h3>
                <button
                  onClick={fetchPlatformBalance}
                  className="text-gray-400 hover:text-[#D4AF37] transition-colors p-2"
                  title="Refresh Balance"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M21 12a9 9 0 11-9-9c2.52 0 4.93 1 6.74 2.74L21 8" />
                    <path d="M21 3v5h-5" />
                  </svg>
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-gray-400 text-sm mb-1">Current Balance</p>
                  <p className="text-4xl font-bold text-[#D4AF37]">${platformBalance.balance.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Total Received</p>
                  <p className="text-2xl font-bold text-green-400">${platformBalance.totalReceived.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm mb-1">Total Paid Out</p>
                  <p className="text-2xl font-bold text-blue-400">${platformBalance.totalPaidOut.toFixed(2)}</p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">
                Platform balance includes buyer payments in escrow and collected seller deposits
              </p>
            </div>
          )}
          
          {/* Stats Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Total Products</p>
            <p className="text-3xl font-bold text-[#D4AF37]">{stats.totalProducts}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Total Orders</p>
            <p className="text-3xl font-bold text-blue-400">{stats.totalOrders}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Total Revenue</p>
            <p className="text-3xl font-bold text-green-400">${stats.totalRevenue.toFixed(2)}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Pending Payments</p>
            <p className="text-3xl font-bold text-yellow-400">{stats.pendingPayments}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Total Users</p>
            <p className="text-3xl font-bold text-white">{stats.totalUsers}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Verified Sellers</p>
            <p className="text-3xl font-bold text-green-400">{stats.verifiedSellers}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Pending Verifications</p>
            <p className="text-3xl font-bold text-orange-400">{stats.pendingVerifications}</p>
          </div>
          <div className="luxury-card">
            <p className="text-gray-400 text-sm mb-1">Pending Payouts</p>
            <p className="text-3xl font-bold text-yellow-400">{stats.pendingPayouts}</p>
          </div>
        </div>
        </div>
      )}

      {activeTab === 'payoutRequests' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">
              Payout Requests
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[rgba(212,175,55,0.2)]">
                    <th className="text-left p-3 text-gray-400 font-medium">Seller</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Email</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Store</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Amount</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden lg:table-cell">Wallet Address</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Request Date</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                    <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {payoutRequests.map((p) => (
                    <tr key={p.id} className="border-b border-[rgba(212,175,55,0.1)]">
                      <td className="p-3 text-white">{p.sellerName || 'Unknown'}</td>
                      <td className="p-3 text-gray-400 hidden sm:table-cell">{p.sellerEmail || 'N/A'}</td>
                      <td className="p-3 text-gray-300">{p.sellerStoreName || '—'}</td>
                      <td className="p-3 text-[#D4AF37] font-semibold">${p.requestedAmount?.toFixed(2)}</td>
                      <td className="p-3 hidden lg:table-cell">
                        {p.payoutWallet ? (
                          <div className="flex items-center gap-2">
                            <span className="text-gray-300 font-mono text-xs truncate max-w-[150px]" title={p.payoutWallet}>
                              {p.payoutWallet}
                            </span>
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(p.payoutWallet);
                                toast.success('Wallet address copied!');
                              }}
                              className="text-[#D4AF37] hover:text-[#f0c860] transition-colors"
                              title="Copy wallet address"
                            >
                              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                              </svg>
                            </button>
                          </div>
                        ) : (
                          <span className="text-gray-500 text-xs">Not provided</span>
                        )}
                      </td>
                      <td className="p-3 text-gray-400 hidden md:table-cell text-sm">
                        {p.requestDate
                          ? new Date(p.requestDate).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric',
                            })
                          : '—'}
                      </td>
                      <td className="p-3">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${
                            p.status === 'approved' || p.status === 'paid'
                              ? 'bg-green-500/20 text-green-400'
                              : p.status === 'rejected'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-yellow-500/20 text-yellow-400'
                          }`}
                        >
                          {p.status}
                        </span>
                        {p.adminNote && p.status !== 'pending' && (
                          <p className="text-xs text-gray-500 mt-1 max-w-xs truncate">{p.adminNote}</p>
                        )}
                      </td>
                      <td className="p-3">
                        {p.status === 'pending' ? (
                          <div className="flex flex-col sm:flex-row flex-wrap gap-2 sm:justify-end items-stretch">
                            <button
                              onClick={async () => {
                                const note = window.prompt('Enter admin note (optional):') || undefined;
                                try {
                                  await api.post(`/admin/payout-requests/${p.id}/status`, {
                                    status: 'approved',
                                    adminNote: note,
                                  });
                                  toast.success('Payout request approved');
                                  fetchData();
                                } catch (error) {
                                  toast.error(error.response?.data?.detail || 'Failed to approve request');
                                }
                              }}
                              className="px-3 py-1 rounded-md text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors whitespace-nowrap w-full sm:w-auto text-center"
                            >
                              Approve
                            </button>
                            <button
                              onClick={async () => {
                                const note = window.prompt('Enter rejection reason (required):');
                                if (!note) {
                                  toast.error('Rejection reason is required');
                                  return;
                                }
                                try {
                                  await api.post(`/admin/payout-requests/${p.id}/status`, {
                                    status: 'rejected',
                                    adminNote: note,
                                  });
                                  toast.success('Payout request rejected');
                                  fetchData();
                                } catch (error) {
                                  toast.error(error.response?.data?.detail || 'Failed to reject request');
                                }
                              }}
                              className="px-3 py-1 rounded-md text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors whitespace-nowrap w-full sm:w-auto text-center"
                            >
                              Reject
                            </button>
                          </div>
                        ) : p.status === 'approved' ? (
                          <div className="flex justify-end">
                            <button
                              onClick={async () => {
                                if (!window.confirm('Mark this payout as paid? This confirms you have manually paid the seller.')) return;
                                try {
                                  await api.post(`/admin/payout-requests/${p.id}/status`, {
                                    status: 'paid',
                                  });
                                  toast.success('Payout marked as paid');
                                  fetchData();
                                } catch (error) {
                                  toast.error(error.response?.data?.detail || 'Failed to mark as paid');
                                }
                              }}
                              className="px-3 py-1 rounded-md text-xs bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors whitespace-nowrap w-full sm:w-auto text-center"
                            >
                              Mark Paid
                            </button>
                          </div>
                        ) : (
                          <div className="text-right text-xs text-gray-500">
                            {p.adminActionTimestamp && `Processed: ${new Date(p.adminActionTimestamp).toLocaleDateString()}`}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                  {payoutRequests.length === 0 && (
                    <tr>
                      <td colSpan={7} className="p-4 text-center text-gray-500 text-sm">
                        No payout requests yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {activeTab === 'storeRequests' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">
              Store Name Change Requests
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[rgba(212,175,55,0.2)]">
                    <th className="text-left p-3 text-gray-400 font-medium">Seller</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Email</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Old Store</th>
                    <th className="text-left p-3 text-gray-400 font-medium">New Store</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                    <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {storeNameRequests.map((r) => (
                    <tr key={r.id} className="border-b border-[rgba(212,175,55,0.1)]">
                      <td className="p-3 text-white">{r.sellerName || 'Unknown'}</td>
                      <td className="p-3 text-gray-400 hidden sm:table-cell">{r.sellerEmail || 'N/A'}</td>
                      <td className="p-3 text-gray-300">{r.oldStoreName || '—'}</td>
                      <td className="p-3 text-[#D4AF37] font-semibold">{r.newStoreName}</td>
                      <td className="p-3">
                        <span
                          className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${
                            r.status === 'approved'
                              ? 'bg-green-500/20 text-green-400'
                              : r.status === 'rejected'
                              ? 'bg-red-500/20 text-red-400'
                              : 'bg-yellow-500/20 text-yellow-400'
                          }`}
                        >
                          {r.status}
                        </span>
                        {r.adminNote && r.status !== 'pending' && (
                          <p className="text-xs text-gray-500 mt-1">{r.adminNote}</p>
                        )}
                      </td>
                      <td className="p-3">
                        {r.status === 'pending' ? (
                          <div className="flex flex-wrap gap-2 justify-end">
                            <button
                              onClick={async () => {
                                try {
                                  await api.post(`/admin/store-name-requests/${r.id}/approve`, {});
                                  toast.success('Store name change approved');
                                  fetchData();
                                } catch (error) {
                                  toast.error(error.response?.data?.detail || 'Failed to approve request');
                                }
                              }}
                              className="px-3 py-1 rounded-md text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors whitespace-nowrap"
                            >
                              Approve
                            </button>
                            <button
                              onClick={async () => {
                                const note = window.prompt('Enter rejection reason (optional):') || undefined;
                                try {
                                  await api.post(`/admin/store-name-requests/${r.id}/reject`, {
                                    adminNote: note,
                                  });
                                  toast.success('Store name change rejected');
                                  fetchData();
                                } catch (error) {
                                  toast.error(error.response?.data?.detail || 'Failed to reject request');
                                }
                              }}
                              className="px-3 py-1 rounded-md text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors whitespace-nowrap"
                            >
                              Reject
                            </button>
                          </div>
                        ) : (
                          <div className="text-right text-xs text-gray-500">
                            {r.updatedAt && `Updated at ${new Date(r.updatedAt).toLocaleString()}`}
                          </div>
                        )}
                      </td>
                    </tr>
                  ))}
                  {storeNameRequests.length === 0 && (
                    <tr>
                      <td colSpan={6} className="p-4 text-center text-gray-500 text-sm">
                        No store name change requests yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        )}
        {activeTab === 'orders' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Order Management</h2>
            
            {/* Filter Buttons */}
            <div className="flex gap-2 mb-6">
              <button
                className="px-4 py-2 bg-yellow-500/20 text-yellow-400 border border-yellow-500/30 rounded-lg text-sm font-medium"
                onClick={() => document.getElementById('pending-orders')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Pending ({pendingPaymentOrders.length})
              </button>
              <button
                className="px-4 py-2 bg-green-500/20 text-green-400 border border-green-500/30 rounded-lg text-sm font-medium"
                onClick={() => document.getElementById('paid-orders')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Paid ({paidOrders.length})
              </button>
              <button
                className="px-4 py-2 bg-blue-500/20 text-blue-400 border border-blue-500/30 rounded-lg text-sm font-medium"
                onClick={() => document.getElementById('completed-orders')?.scrollIntoView({ behavior: 'smooth' })}
              >
                Completed ({completedOrders.length})
              </button>
            </div>

            <div className="space-y-8">
              {/* Pending Payment Orders */}
              {pendingPaymentOrders.length > 0 && (
                <div id="pending-orders">
                  <h3 className="font-semibold text-yellow-400 text-lg mb-4 flex items-center gap-2">
                    <Clock className="w-5 h-5" />
                    Pending Payment Confirmation ({pendingPaymentOrders.length})
                  </h3>
                  <div className="space-y-4">
                    {pendingPaymentOrders.map((order) => (
                      <div key={order.id} className="p-5 bg-yellow-500/10 border border-yellow-500/30 rounded-lg" data-testid="pending-order">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <p className="text-white font-semibold text-lg">Order #{order.id.slice(0, 8).toUpperCase()}</p>
                            <p className="text-sm text-gray-400">Buyer: {order.users?.name || 'N/A'}</p>
                            <p className="text-sm text-gray-400">Email: {order.users?.email || 'N/A'}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              Created: {new Date(order.createdAt).toLocaleString()}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-[#D4AF37] font-bold text-2xl">${order.totalAmount.toFixed(2)}</p>
                            <div className="mt-2 px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-semibold">
                              PENDING PAYMENT
                            </div>
                          </div>
                        </div>

                        <div className="bg-[rgba(20,20,20,0.6)] rounded-lg p-4 mb-4">
                          <p className="text-sm text-gray-400 mb-1">Payment Method:</p>
                          <p className="text-white font-medium">{order.paymentMethod}</p>
                          <p className="text-sm text-gray-400 mt-2 mb-1">Payment Wallet:</p>
                          <p className="text-[#D4AF37] font-mono text-xs break-all">{order.paymentWallet}</p>
                        </div>

                        {/* Order Items */}
                        {order.orderItems && order.orderItems.length > 0 && (
                          <div className="mb-4 p-3 bg-[rgba(20,20,20,0.4)] rounded-lg">
                            <p className="text-sm text-gray-400 mb-2">Order Items:</p>
                            {order.orderItems.map((item, idx) => (
                              <div key={idx} className="text-sm text-gray-300">
                                • {item.product?.title || 'Product'} x {item.quantity} - ${(item.price * item.quantity).toFixed(2)}
                              </div>
                            ))}
                          </div>
                        )}

                        <div className="flex gap-3">
                          <button
                            onClick={() => handleConfirmPayment(order.id)}
                            className="flex-1 btn-gold text-sm px-4 py-2.5 flex items-center justify-center gap-2"
                            data-testid="confirm-payment-btn"
                          >
                            <CheckCircle className="w-4 h-4" />
                            Confirm Payment Received
                          </button>
                          <button
                            onClick={() => handleCancelOrder(order.id)}
                            className="px-4 py-2.5 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm"
                          >
                            Cancel Order
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Paid Orders */}
              {paidOrders.length > 0 && (
                <div id="paid-orders">
                  <h3 className="font-semibold text-green-400 text-lg mb-4 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5" />
                    Paid Orders - Ready to Process ({paidOrders.length})
                  </h3>
                  <div className="space-y-4">
                    {paidOrders.map((order) => (
                      <div key={order.id} className="p-5 bg-green-500/10 border border-green-500/30 rounded-lg">
                        <div className="flex justify-between items-start mb-4">
                          <div>
                            <p className="text-white font-semibold text-lg">Order #{order.id.slice(0, 8).toUpperCase()}</p>
                            <p className="text-sm text-gray-400">Buyer: {order.users?.name || 'N/A'}</p>
                            <p className="text-xs text-gray-500 mt-1">
                              Confirmed: {order.confirmedAt ? new Date(order.confirmedAt).toLocaleString() : 'N/A'}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-[#D4AF37] font-bold text-2xl">${order.totalAmount.toFixed(2)}</p>
                            <div className="mt-2 px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-semibold">
                              PAYMENT CONFIRMED
                            </div>
                          </div>
                        </div>

                        <button
                          onClick={() => handleCompleteOrder(order.id)}
                          className="w-full btn-gold text-sm px-4 py-2.5 flex items-center justify-center gap-2"
                        >
                          <Package className="w-4 h-4" />
                          Mark as Completed
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Completed Orders */}
              {completedOrders.length > 0 && (
                <div id="completed-orders">
                  <h3 className="font-semibold text-blue-400 text-lg mb-4">Completed Orders ({completedOrders.length})</h3>
                  <div className="space-y-3">
                    {completedOrders.map((order) => (
                      <div key={order.id} className="p-4 bg-blue-500/5 border border-blue-500/20 rounded-lg">
                        <div className="flex justify-between items-center">
                          <div>
                            <p className="text-white font-medium">Order #{order.id.slice(0, 8).toUpperCase()}</p>
                            <p className="text-xs text-gray-500">
                              Completed: {order.confirmedAt ? new Date(order.confirmedAt).toLocaleString() : 'N/A'}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-[#D4AF37] font-semibold">${order.totalAmount.toFixed(2)}</p>
                            <div className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded text-xs">
                              COMPLETED
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {orders.length === 0 && (
                <div className="text-center py-12">
                  <ShoppingCart className="w-16 h-16 mx-auto text-gray-600 mb-4" />
                  <p className="text-gray-400">No orders yet</p>
                </div>
              )}
            </div>
          </div>
        )}

      {/* Products Tab - Admin Catalog Management */}
      {activeTab === 'products' && (
        <div className="luxury-card">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">
              Product Catalog ({products.length} items)
            </h2>
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => {
                  setShowProductForm(true);
                  setEditingProduct(null);
                  resetProductForm();
                }}
                className="btn-gold"
                data-testid="add-product-btn"
              >
                <Plus className="w-4 h-4 inline mr-2" />
                Add Product
              </button>
              <button
                onClick={handleSeedCatalog}
                disabled={seedingCatalog}
                className="bg-blue-500/20 text-blue-400 px-4 py-2 rounded-lg hover:bg-blue-500/30 transition-colors disabled:opacity-50"
                data-testid="seed-catalog-btn"
              >
                <Database className="w-4 h-4 inline mr-2" />
                {seedingCatalog ? 'Seeding...' : 'Seed 100 Products'}
              </button>
              <button
                onClick={handleClearCatalog}
                className="bg-red-500/20 text-red-400 px-4 py-2 rounded-lg hover:bg-red-500/30 transition-colors"
                data-testid="clear-catalog-btn"
              >
                <Trash2 className="w-4 h-4 inline mr-2" />
                Clear All
              </button>
            </div>
          </div>

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
                data-testid="search-products"
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

          {/* Products Grid */}
          {filteredProducts.length === 0 ? (
            <div className="text-center py-12">
              <Package className="w-16 h-16 mx-auto text-gray-600 mb-4" />
              <p className="text-gray-400">No products found</p>
              <p className="text-gray-500 text-sm mt-2">Add products or seed the catalog to get started</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredProducts.map((product) => (
                <div
                  key={product.id}
                  className="bg-[rgba(30,30,30,0.6)] rounded-lg overflow-hidden border border-[rgba(212,175,55,0.1)] hover:border-[rgba(212,175,55,0.3)] transition-all"
                  data-testid="admin-product-card"
                >
                  {/* Product Image */}
                  <div className="h-48 bg-[rgba(50,50,50,0.6)] relative">
                    {product.images && product.images.length > 0 ? (
                      <img
                        src={product.images[0]}
                        alt={product.title}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Package className="w-12 h-12 text-gray-500" />
                      </div>
                    )}
                    {product.categoryName && (
                      <span className="absolute top-2 left-2 px-2 py-1 bg-black/70 text-[#D4AF37] rounded text-xs">
                        {product.categoryIcon} {product.categoryName}
                      </span>
                    )}
                  </div>
                  
                  {/* Product Info */}
                  <div className="p-4">
                    <h3 className="font-semibold text-white mb-1 truncate">{product.title}</h3>
                    <p className="text-sm text-gray-400 mb-2 line-clamp-2">{product.description}</p>
                    <p className="text-[#D4AF37] font-bold text-lg">${product.price?.toFixed(2)}</p>
                    
                    {/* Actions */}
                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => {
                          setEditingProduct(product.id);
                          setProductForm({
                            title: product.title,
                            description: product.description,
                            price: product.price?.toString() || '',
                            category: product.category || '',
                            images: product.images || []
                          });
                        }}
                        className="flex-1 p-2 bg-[rgba(212,175,55,0.1)] hover:bg-[rgba(212,175,55,0.2)] text-[#D4AF37] rounded-lg transition-colors flex items-center justify-center gap-2"
                        data-testid="edit-product-btn"
                      >
                        <Edit className="w-4 h-4" />
                        Edit
                      </button>
                      <button
                        onClick={() => handleDeleteProduct(product.id, product.title)}
                        className="flex-1 p-2 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors flex items-center justify-center gap-2"
                        data-testid="delete-product-btn"
                      >
                        <Trash2 className="w-4 h-4" />
                        Delete
                      </button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Orders Tab */}
      {activeTab === 'orders' && (
        <div className="luxury-card">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">All Orders</h2>
          {orders.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No orders yet</p>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => (
                <div key={order.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg" data-testid="admin-order">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="text-white font-semibold">Order #{order.id?.slice(0, 8).toUpperCase()}</p>
                      <p className="text-sm text-gray-400">Buyer: {order.users?.name || 'Unknown'} ({order.users?.email || 'N/A'})</p>
                      <p className="text-sm text-gray-400">
                        {new Date(order.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[#D4AF37] font-bold text-xl">${order.totalAmount?.toFixed(2)}</p>
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
                  <div className="space-y-2 mb-4">
                    {order.order_items?.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-2 bg-[rgba(20,20,20,0.6)] rounded">
                        {item.products?.images?.[0] ? (
                          <img src={item.products.images[0]} alt="" className="w-12 h-12 object-cover rounded" />
                        ) : (
                          <div className="w-12 h-12 bg-gray-700 rounded flex items-center justify-center">
                            <Package className="w-6 h-6 text-gray-500" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="text-white text-sm">{item.products?.title || 'Product'}</p>
                          <p className="text-gray-400 text-xs">Qty: {item.quantity} × ${item.price?.toFixed(2)}</p>
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Actions */}
                  <div className="flex gap-2 flex-wrap">
                    {order.paymentStatus === 'pending_payment' && (
                      <button
                        onClick={() => handleConfirmPayment(order.id)}
                        className="btn-gold text-sm"
                        data-testid="confirm-payment-btn"
                      >
                        <DollarSign className="w-4 h-4 inline mr-1" />
                        Confirm Payment
                      </button>
                    )}
                    {/* NEW: Ship by Platform button for orders with deposit received */}
                    {order.escrowStatus === 'deposit_received' && (
                      <button
                        onClick={() => handleShipByPlatform(order.id)}
                        disabled={shippingOrderId === order.id}
                        className="bg-purple-500/20 text-purple-400 text-sm px-4 py-2 rounded-lg hover:bg-purple-500/30 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {shippingOrderId === order.id ? 'Shipping...' : (
                          <>
                            <ShoppingCart className="w-4 h-4 inline mr-1" />
                            Ship by Platform
                          </>
                        )}
                      </button>
                    )}
                    {order.paymentStatus === 'paid' && (
                      <button
                        onClick={() => handleMarkCompleted(order.id)}
                        className="bg-green-500/20 text-green-400 text-sm px-4 py-2 rounded-lg hover:bg-green-500/30 transition-colors"
                        data-testid="mark-completed-btn"
                      >
                        <CheckCircle className="w-4 h-4 inline mr-1" />
                        Mark Completed
                      </button>
                    )}
                    {order.paymentStatus === 'completed' && (
                      <span className="text-green-400 text-sm flex items-center">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Order Fulfilled
                      </span>
                    )}
                    {/* NEW: Display escrow status */}
                    {order.escrowStatus && (
                      <span className="text-xs text-gray-400 border border-gray-600 px-2 py-1 rounded">
                        Escrow: {order.escrowStatus.replace(/_/g, ' ')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <div className="luxury-card">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">All Users</h2>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[rgba(212,175,55,0.2)]">
                  <th className="text-left p-3 text-gray-400 font-medium">Name</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Email</th>
                  <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Role</th>
                  <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Verification</th>
                  <th className="text-left p-3 text-gray-400 font-medium hidden lg:table-cell">Store</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                  <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-[rgba(212,175,55,0.1)]">
                    <td className="p-3 text-white">{u.name}</td>
                    <td className="p-3 text-gray-400">{u.email}</td>
                    <td className="p-3 hidden sm:table-cell">
                      <span className={`status-badge ${
                        u.role === 'admin' ? 'bg-purple-500/20 text-purple-400' :
                        u.role === 'seller' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="p-3 hidden md:table-cell">
                      {u.role === 'buyer' ? (
                        <span className="status-badge bg-gray-500/20 text-gray-300">
                          Not required
                        </span>
                      ) : (
                        <span className={`status-badge ${
                          u.verificationStatus === 'verified' ? 'status-verified' :
                          u.verificationStatus === 'pending' ? 'status-pending' :
                          u.verificationStatus === 'rejected' ? 'status-rejected' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {u.verificationStatus}
                        </span>
                      )}
                    </td>
                    <td className="p-3 hidden lg:table-cell">
                      {u.role === 'seller' ? (
                        <span
                          className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${
                            u.storeName
                              ? 'bg-[rgba(212,175,55,0.15)] text-[#D4AF37]'
                              : 'bg-gray-500/20 text-gray-300'
                          }`}
                        >
                          {u.storeName || 'No store set'}
                        </span>
                      ) : (
                        <span className="inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium bg-gray-500/20 text-gray-400">
                          —
                        </span>
                      )}
                    </td>
                    <td className="p-3">
                      <span
                        className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium ${
                          u.banStatus === 'banned'
                            ? 'bg-red-500/20 text-red-400'
                            : u.banStatus === 'suspended'
                            ? 'bg-orange-500/20 text-orange-400'
                            : 'bg-green-500/20 text-green-400'
                        }`}
                        title={u.banReason || ''}
                      >
                        {u.banStatus || 'active'}
                      </span>
                    </td>
                    <td className="p-3">
                      {u.banStatus && u.banStatus !== 'active' ? (
                        <div className="flex flex-wrap gap-2 justify-end">
                          <button
                            onClick={() =>
                              setPasswordResetModal({ userId: u.id, email: u.email, name: u.name })
                            }
                            className="px-3 py-1 rounded-md text-xs bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors whitespace-nowrap"
                            data-testid={`reset-password-btn-${u.id}`}
                          >
                            Reset Password
                          </button>
                          <button
                            onClick={async () => {
                              try {
                                await api.post(`/admin/users/${u.id}/unban`);
                                toast.success('User unbanned successfully');
                                fetchData();
                              } catch (error) {
                                toast.error(error.response?.data?.detail || 'Failed to unban user');
                              }
                            }}
                            className="px-3 py-1 rounded-md text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors whitespace-nowrap"
                          >
                            Unban
                          </button>
                        </div>
                      ) : (
                        <div className="flex flex-wrap gap-2 justify-end">
                          <button
                            onClick={() =>
                              setPasswordResetModal({ userId: u.id, email: u.email, name: u.name })
                            }
                            className="px-3 py-1 rounded-md text-xs bg-blue-500/20 text-blue-400 hover:bg-blue-500/30 transition-colors whitespace-nowrap"
                            data-testid={`reset-password-btn-${u.id}`}
                          >
                            Reset Password
                          </button>
                          <button
                            onClick={async () => {
                              const reason = window.prompt('Enter reason for ban:');
                              if (!reason) return;
                              try {
                                await api.post(`/admin/users/${u.id}/ban`, {
                                  status: 'banned',
                                  reason,
                                });
                                toast.success('User banned successfully');
                                fetchData();
                              } catch (error) {
                                toast.error(error.response?.data?.detail || 'Failed to ban user');
                              }
                            }}
                            className="px-3 py-1 rounded-md text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors whitespace-nowrap"
                          >
                            Ban
                          </button>
                          <button
                            onClick={async () => {
                              const reason = window.prompt('Enter reason for suspension:');
                              if (!reason) return;
                              try {
                                await api.post(`/admin/users/${u.id}/ban`, {
                                  status: 'suspended',
                                  reason,
                                });
                                toast.success('User suspended successfully');
                                fetchData();
                              } catch (error) {
                                toast.error(error.response?.data?.detail || 'Failed to suspend user');
                              }
                            }}
                            className="px-3 py-1 rounded-md text-xs bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30 transition-colors whitespace-nowrap"
                          >
                            Suspend
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {/* Pagination controls */}
            {allUsers.length > USERS_PER_PAGE && (
              <div className="flex items-center justify-center mt-4 px-3">
                <div className="flex gap-2">
                  {Array.from({ length: usersTotalPages }, (_, index) => {
                    const pageNumber = index + 1;
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => setUsersPage(pageNumber)}
                        className={`px-3 py-1 rounded-md text-xs transition-colors ${
                          usersPage === pageNumber
                            ? 'bg-[#D4AF37] text-black'
                            : 'bg-[rgba(30,30,30,0.8)] text-gray-300 hover:bg-[rgba(50,50,50,0.9)]'
                        }`}
                      >
                        {pageNumber}
                      </button>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {activeTab === 'bannedUsers' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">
              Banned Users
            </h2>

            {bannedUsers.length === 0 ? (
              <p className="text-gray-400 text-sm">No banned or suspended users.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[rgba(212,175,55,0.2)]">
                      <th className="text-left p-3 text-gray-400 font-medium">Name</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Email</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Role</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Ban Reason</th>
                      <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {bannedUsers.map((u) => (
                      <tr key={u.id} className="border-b border-[rgba(212,175,55,0.1)]">
                        <td className="p-3 text-white">{u.name}</td>
                        <td className="p-3 text-gray-400">{u.email}</td>
                        <td className="p-3 hidden sm:table-cell">
                          <span className={`status-badge ${
                            u.role === 'admin' ? 'bg-purple-500/20 text-purple-400' :
                            u.role === 'seller' ? 'bg-blue-500/20 text-blue-400' :
                            'bg-green-500/20 text-green-400'
                          }`}>
                            {u.role}
                          </span>
                        </td>
                        <td className="p-3 text-gray-400 text-sm">
                          {u.banReason || 'No reason provided'}
                        </td>
                        <td className="p-3">
                          <div className="flex flex-wrap gap-2 justify-end">
                            <button
                              onClick={async () => {
                                try {
                                  await api.post(`/admin/users/${u.id}/unban`);
                                  toast.success('User unbanned successfully');
                                  fetchData();
                                } catch (error) {
                                  toast.error(error.response?.data?.detail || 'Failed to unban user');
                                }
                              }}
                              className="px-3 py-1 rounded-md text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors whitespace-nowrap"
                            >
                              Unban
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

      {/* Verifications Tab */}
      {activeTab === 'verifications' && (
        <div className="luxury-card">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Verification Documents</h2>
          <div className="space-y-4">
            {verificationDocs.map((doc) => (
              <div key={doc.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg" data-testid="verification-doc">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <p className="text-white font-semibold">{doc.users?.name || 'Unknown'}</p>
                    <p className="text-sm text-gray-400">Email: {doc.users?.email || 'N/A'}</p>
                    <p className="text-sm text-gray-400">Role: {doc.users?.role || 'N/A'}</p>
                    <p className="text-sm text-gray-400">Document: {doc.documentType}</p>
                    {doc.merchantInviteCode && (
                      <p className="text-sm text-[#D4AF37]">Invite Code: {doc.merchantInviteCode}</p>
                    )}
                  </div>
                  <span className={`status-badge ${
                    doc.status === 'verified' ? 'status-verified' :
                    doc.status === 'pending' ? 'status-pending' :
                    'status-rejected'
                  }`}>
                    {doc.status}
                  </span>
                </div>
                
                {doc.documentUrl && (
                  <div className="mb-3">
                    <a 
                      href={doc.documentUrl} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[#D4AF37] hover:text-[#f0c850] text-sm flex items-center gap-2"
                    >
                      <Eye className="w-4 h-4" />
                      View Document
                    </a>
                  </div>
                )}
                
                {doc.status === 'pending' && (
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleReviewVerification(doc.id, 'verified')}
                      className="flex-1 p-2 bg-green-500/20 hover:bg-green-500/30 text-green-400 rounded-lg transition-colors flex items-center justify-center gap-2"
                      data-testid="approve-verification-btn"
                    >
                      <CheckCircle className="w-4 h-4" />
                      Approve
                    </button>
                    <button
                      onClick={() => {
                        const reason = window.prompt('Enter rejection reason:');
                        if (reason) handleReviewVerification(doc.id, 'rejected', reason);
                      }}
                      className="flex-1 p-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors flex items-center justify-center gap-2"
                      data-testid="reject-verification-btn"
                    >
                      <XCircle className="w-4 h-4" />
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        
      </div>
    )}

    {/* Invite Codes Tab */}
    {activeTab === 'inviteCodes' && (
      <div className="luxury-card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Merchant Invite Codes</h2>
          <button
            onClick={async () => {
              try {
                await api.post('/admin/invite-codes');
                toast.success('New invite code generated!');
                fetchData();
              } catch (error) {
                toast.error(error.response?.data?.detail || 'Failed to generate code');
              }
            }}
            className="btn-gold"
            data-testid="generate-invite-btn"
          >
            <Plus className="w-4 h-4 inline mr-2" />
            Generate New Code
          </button>
        </div>

        {inviteCodes.length === 0 ? (
          <div className="text-center py-12">
            <Code className="w-16 h-16 mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400">No invite codes yet</p>
            <p className="text-gray-500 text-sm mt-2">Generate invite codes for new sellers</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[rgba(212,175,55,0.2)]">
                  <th className="text-left p-3 text-gray-400 font-medium">Code</th>
                  <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Created</th>
                  <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Used By</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                  <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {inviteCodes.map((code) => (
                  <tr key={code.id} className="border-b border-[rgba(212,175,55,0.1)]">
                    <td className="p-3">
                      <span className="font-mono text-[#D4AF37] font-semibold">{code.code}</span>
                    </td>
                    <td className="p-3 text-gray-400 text-sm hidden sm:table-cell">
                      {code.createdAt ? new Date(code.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'short',
                        day: 'numeric'
                      }) : '—'}
                    </td>
                    <td className="p-3 text-gray-400 text-sm hidden md:table-cell">
                      {code.isUsed && code.usedByUserId ? (
                        <div>
                          <span className="text-white">{code.usedByName || 'User'}</span>
                          {code.usedAt && (
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(code.usedAt).toLocaleDateString('en-US', {
                                year: 'numeric',
                                month: 'short',
                                day: 'numeric'
                              })}
                            </p>
                          )}
                        </div>
                      ) : (
                        <span className="text-gray-500">Not used</span>
                      )}
                    </td>
                    <td className="p-3">
                      <span className={`status-badge ${
                        !code.isUsed ? 'status-verified' :
                        code.isUsed ? 'bg-blue-500/20 text-blue-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {code.isUsed ? 'Used' : 'Active'}
                      </span>
                    </td>
                    <td className="p-3">
                      <div className="flex gap-2 justify-end">
                        {!code.isUsed && (
                          <button
                            onClick={async () => {
                              if (!window.confirm('Deactivate this invite code?')) return;
                              try {
                                await api.delete(`/admin/invite-codes/${code.id}`);
                                toast.success('Invite code deactivated');
                                fetchData();
                              } catch (error) {
                                toast.error(error.response?.data?.detail || 'Failed to deactivate');
                              }
                            }}
                            className="px-3 py-1 rounded-md text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors"
                            data-testid="deactivate-code-btn"
                          >
                            Deactivate
                          </button>
                        )}
                        {code.isUsed && (
                          <span className="text-xs text-gray-500">Already used</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    )}

    {/* Orders Tab */}
      {/* {activeTab === 'orders' && (
        <div className="luxury-card">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">All Orders</h2>
          {orders.length === 0 ? (
            <p className="text-gray-400 text-center py-8">No orders yet</p>
          ) : (
            <div className="space-y-4">
              {orders.map((order) => (
                <div key={order.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg" data-testid="admin-order">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="text-white font-semibold">Order #{order.id?.slice(0, 8).toUpperCase()}</p>
                      <p className="text-sm text-gray-400">Buyer: {order.users?.name || 'Unknown'} ({order.users?.email || 'N/A'})</p>
                      <p className="text-sm text-gray-400">
                        {new Date(order.createdAt).toLocaleDateString('en-US', {
                          year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
                        })}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-[#D4AF37] font-bold text-xl">${order.totalAmount?.toFixed(2)}</p>
                      <span className={`status-badge ${
                        order.paymentStatus === 'paid' || order.paymentStatus === 'completed' ? 'status-verified' :
                        order.paymentStatus === 'pending_payment' ? 'status-pending' :
                        'status-rejected'
                      }`}>
                        {order.paymentStatus?.replace('_', ' ')}
                      </span>
                    </div>
                  </div>
                  
               
                  <div className="space-y-2 mb-4">
                    {order.order_items?.map((item, idx) => (
                      <div key={idx} className="flex items-center gap-3 p-2 bg-[rgba(20,20,20,0.6)] rounded">
                        {item.products?.images?.[0] ? (
                          <img src={item.products.images[0]} alt="" className="w-12 h-12 object-cover rounded" />
                        ) : (
                          <div className="w-12 h-12 bg-gray-700 rounded flex items-center justify-center">
                            <Package className="w-6 h-6 text-gray-500" />
                          </div>
                        )}
                        <div className="flex-1">
                          <p className="text-white text-sm">{item.products?.title || 'Product'}</p>
                          <p className="text-gray-400 text-xs">Qty: {item.quantity} × ${item.price?.toFixed(2)}</p>
                        </div>
                      </div>
                    ))}
                  </div>

               
                  <div className="flex gap-2">
                    {order.paymentStatus === 'pending_payment' && (
                      <button
                        onClick={() => handleConfirmPayment(order.id)}
                        className="btn-gold text-sm"
                        data-testid="confirm-payment-btn"
                      >
                        <DollarSign className="w-4 h-4 inline mr-1" />
                        Confirm Payment
                      </button>
                    )}
                    {order.paymentStatus === 'paid' && (
                      <button
                        onClick={() => handleMarkCompleted(order.id)}
                        className="bg-green-500/20 text-green-400 text-sm px-4 py-2 rounded-lg hover:bg-green-500/30 transition-colors"
                        data-testid="mark-completed-btn"
                      >
                        <CheckCircle className="w-4 h-4 inline mr-1" />
                        Mark Completed
                      </button>
                    )}
                    {order.paymentStatus === 'completed' && (
                      <span className="text-green-400 text-sm flex items-center">
                        <CheckCircle className="w-4 h-4 mr-1" />
                        Order Fulfilled
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )} */}


      {/* Deposit Confirmations Tab */}
      {activeTab === 'depositConfirmations' && (
        <div>
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">
            Seller Deposit Confirmations
          </h2>
          <p className="text-gray-400 mb-6">
            Review and confirm seller deposit payments for orders (USDT TRC20 and Wallet Balance)
          </p>

          {depositConfirmations.length === 0 ? (
            <div className="luxury-card text-center py-12">
              <CheckCircle className="w-16 h-16 text-green-500/50 mx-auto mb-4" />
              <p className="text-gray-400 text-lg">No pending deposit confirmations</p>
              <p className="text-gray-500 text-sm mt-2">All deposits have been processed</p>
            </div>
          ) : (
            <div className="luxury-card overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[rgba(212,175,55,0.2)]">
                    <th className="text-left p-3 text-gray-400 font-medium">Order ID</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Seller</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Email</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Order Amount</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Deposit (80%)</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Payment Method</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Submitted</th>
                    <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {depositConfirmations.map((deposit) => (
                    <tr key={deposit.id} className="border-b border-[rgba(212,175,55,0.1)] hover:bg-[rgba(212,175,55,0.05)] transition-colors">
                      <td className="p-3">
                        <span className="text-white font-mono text-sm">
                          {deposit.orderId?.slice(0, 8)}...
                        </span>
                      </td>
                      <td className="p-3 text-white font-medium">{deposit.sellerName || 'Unknown'}</td>
                      <td className="p-3 text-gray-400 hidden sm:table-cell text-sm">{deposit.sellerEmail || 'N/A'}</td>
                      <td className="p-3 text-[#D4AF37] font-semibold">${deposit.orderAmount?.toFixed(2)}</td>
                      <td className="p-3 text-orange-400 font-bold">${deposit.depositRequired?.toFixed(2)}</td>
                      <td className="p-3">
                        {deposit.depositMethod === 'internal_wallet' ? (
                          <div className="flex flex-col gap-1">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-500/20 text-green-400">
                              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
                              </svg>
                              Wallet Balance
                            </span>
                            <span className="text-xs text-gray-400">Pre-verified funds</span>
                          </div>
                        ) : (
                          <div className="flex flex-col gap-1">
                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-500/20 text-blue-400">
                              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                              </svg>
                              USDT TRC20
                            </span>
                            {deposit.transactionHash && (
                              <div className="flex items-center gap-1 mt-1">
                                <span className="text-gray-300 font-mono text-xs truncate max-w-[100px]" title={deposit.transactionHash}>
                                  {deposit.transactionHash}
                                </span>
                                <button
                                  onClick={() => {
                                    navigator.clipboard.writeText(deposit.transactionHash);
                                    toast.success('Transaction hash copied!');
                                  }}
                                  className="text-[#D4AF37] hover:text-[#f0c860] transition-colors"
                                  title="Copy transaction hash"
                                >
                                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                                  </svg>
                                </button>
                              </div>
                            )}
                            {deposit.transactionHash && (
                              <a
                                href={`https://tronscan.org/#/transaction/${deposit.transactionHash}`}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="text-blue-400 hover:text-blue-300 text-xs flex items-center gap-1"
                              >
                                Verify on TronScan
                                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                                </svg>
                              </a>
                            )}
                          </div>
                        )}
                        {deposit.notes && (
                          <p className="text-xs text-gray-500 mt-1 italic">Note: {deposit.notes}</p>
                        )}
                      </td>
                      <td className="p-3 text-gray-400 hidden md:table-cell text-sm">
                        {deposit.submittedAt
                          ? new Date(deposit.submittedAt).toLocaleDateString('en-US', {
                              month: 'short',
                              day: 'numeric',
                              hour: '2-digit',
                              minute: '2-digit',
                            })
                          : '—'}
                      </td>
                      <td className="p-3">
                        <div className="flex flex-col sm:flex-row gap-2 sm:justify-end items-stretch">
                          <button
                            onClick={async () => {
                              if (!window.confirm(`Confirm deposit of $${deposit.depositRequired?.toFixed(2)} for Order ${deposit.orderId?.slice(0, 8)}?\n\nThis will unlock the order for shipping.`)) {
                                return;
                              }
                              try {
                                await api.post(`/admin/orders/${deposit.orderId}/confirm-deposit`, {
                                  approved: true
                                });
                                toast.success('Deposit confirmed! Order unlocked for shipping.');
                                fetchData();
                              } catch (error) {
                                toast.error(error.response?.data?.detail || 'Failed to confirm deposit');
                              }
                            }}
                            className="px-3 py-1.5 rounded-md text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors font-semibold whitespace-nowrap w-full sm:w-auto text-center"
                          >
                            ✓ Confirm
                          </button>
                          <button
                            onClick={async () => {
                              const reason = window.prompt('Enter rejection reason (required):');
                              if (!reason?.trim()) {
                                toast.error('Rejection reason is required');
                                return;
                              }
                              try {
                                await api.post(`/admin/orders/${deposit.orderId}/confirm-deposit`, {
                                  approved: false,
                                  rejectionReason: reason
                                });
                                toast.success('Deposit rejected. Seller has been notified.');
                                fetchData();
                              } catch (error) {
                                toast.error(error.response?.data?.detail || 'Failed to reject deposit');
                              }
                            }}
                            className="px-3 py-1.5 rounded-md text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30 transition-colors font-semibold whitespace-nowrap w-full sm:w-auto text-center"
                          >
                            ✗ Reject
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Instructions */}
          <div className="luxury-card mt-6 bg-blue-500/10 border-blue-500/30">
            <div className="flex items-start gap-3">
              <AlertTriangle className="w-5 h-5 text-blue-400 mt-0.5 flex-shrink-0" />
              <div>
                <h3 className="text-blue-300 font-semibold mb-2">Verification Instructions:</h3>
                <ul className="text-sm text-gray-300 space-y-1 list-disc list-inside">
                  <li>Click "Verify on TronScan" to check transaction on blockchain</li>
                  <li>Verify amount matches the deposit required (80% of order)</li>
                  <li>Verify transaction is sent to wallet: <code className="text-[#D4AF37] font-mono text-xs">TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU</code></li>
                  <li>Check transaction status is "SUCCESS" on TronScan</li>
                  <li>Once verified, click "Confirm" to unlock the order for shipping</li>
                  <li>If transaction is invalid or incorrect, click "Reject" with reason</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      )}


      {activeTab === 'wallets' && (
        <div className="luxury-card">
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Wallet Management</h2>
            
            {/* Wallet Recharge Requests */}
            <div className="mb-8">
              <h3 className="font-['Playfair_Display'] text-xl font-bold text-white mb-4">Recharge Requests</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[rgba(212,175,55,0.2)]">
                      <th className="text-left p-3 text-gray-400 font-medium">Buyer</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Email</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Amount</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Request Date</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                      <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {rechargeRequests.length === 0 ? (
                      <tr>
                        <td colSpan={6} className="p-4 text-center text-gray-500 text-sm">
                          No recharge requests yet.
                        </td>
                      </tr>
                    ) : (
                      rechargeRequests.map((req) => (
                        <tr key={req.id} className="border-b border-[rgba(212,175,55,0.1)]">
                          <td className="p-3 text-white">{req.buyerName || 'Unknown'}</td>
                          <td className="p-3 text-gray-400 hidden sm:table-cell">{req.buyerEmail || 'N/A'}</td>
                          <td className="p-3 text-[#D4AF37] font-semibold">${req.amount?.toFixed(2)}</td>
                          <td className="p-3 text-gray-400 hidden md:table-cell text-sm">
                            {req.createdAt ? new Date(req.createdAt).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            }) : '—'}
                          </td>
                          <td className="p-3">
                            <span className={`status-badge ${
                              req.status === 'approved' ? 'status-verified' :
                              req.status === 'rejected' ? 'status-rejected' :
                              'status-pending'
                            }`}>
                              {req.status}
                            </span>
                            {req.adminNote && req.status !== 'pending' && (
                              <p className="text-xs text-gray-500 mt-1 max-w-xs truncate">{req.adminNote}</p>
                            )}
                          </td>
                          <td className="p-3">
                            {req.status === 'pending' ? (
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={async () => {
                                    const note = window.prompt('Enter admin note (optional):') || undefined;
                                    try {
                                      await api.post(`/admin/wallet-recharge-requests/${req.id}/status`, {
                                        status: 'approved',
                                        adminNote: note
                                      });
                                      toast.success('Recharge request approved');
                                      fetchData();
                                    } catch (error) {
                                      toast.error(error.response?.data?.detail || 'Failed to approve');
                                    }
                                  }}
                                  className="px-3 py-1 rounded-md text-xs bg-green-500/20 text-green-400 hover:bg-green-500/30"
                                >
                                  Approve
                                </button>
                                <button
                                  onClick={async () => {
                                    const note = window.prompt('Enter rejection reason (optional):') || undefined;
                                    try {
                                      await api.post(`/admin/wallet-recharge-requests/${req.id}/status`, {
                                        status: 'rejected',
                                        adminNote: note
                                      });
                                      toast.success('Recharge request rejected');
                                      fetchData();
                                    } catch (error) {
                                      toast.error(error.response?.data?.detail || 'Failed to reject');
                                    }
                                  }}
                                  className="px-3 py-1 rounded-md text-xs bg-red-500/20 text-red-400 hover:bg-red-500/30"
                                >
                                  Reject
                                </button>
                              </div>
                            ) : (
                              <div className="text-right text-xs text-gray-500">
                                {req.adminActionTimestamp && `Processed: ${new Date(req.adminActionTimestamp).toLocaleDateString()}`}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Seller Wallet Recharge Requests */}
            <div className="mb-8 border-t border-[rgba(212,175,55,0.2)] pt-8">
              <h3 className="font-['Playfair_Display'] text-xl font-bold text-white mb-4">Seller Wallet Recharge Requests</h3>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-[rgba(212,175,55,0.2)]">
                      <th className="text-left p-3 text-gray-400 font-medium">Seller</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Email</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Amount</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Transaction Hash</th>
                      <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Request Date</th>
                      <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                      <th className="text-left p-3 text-gray-400 font-medium text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {sellerRechargeRequests.length === 0 ? (
                      <tr>
                        <td colSpan={7} className="p-4 text-center text-gray-500 text-sm">
                          No seller recharge requests yet.
                        </td>
                      </tr>
                    ) : (
                      sellerRechargeRequests.map((req) => (
                        <tr key={req.id} className="border-b border-[rgba(212,175,55,0.1)]">
                          <td className="p-3 text-white">{req.sellerName || 'Unknown'}</td>
                          <td className="p-3 text-gray-400 hidden sm:table-cell">{req.sellerEmail || 'N/A'}</td>
                          <td className="p-3 text-[#D4AF37] font-semibold">${req.amount?.toFixed(2)}</td>
                          <td className="p-3 text-gray-400 hidden md:table-cell text-xs font-mono max-w-[150px] truncate" title={req.transactionHash}>
                            {req.transactionHash || 'N/A'}
                          </td>
                          <td className="p-3 text-gray-400 hidden md:table-cell text-sm">
                            {req.createdAt ? new Date(req.createdAt).toLocaleDateString('en-US', {
                              year: 'numeric',
                              month: 'short',
                              day: 'numeric'
                            }) : '—'}
                          </td>
                          <td className="p-3">
                            <span className={`status-badge ${
                              req.status === 'approved' ? 'status-verified' :
                              req.status === 'rejected' ? 'status-rejected' :
                              'status-pending'
                            }`}>
                              {req.status}
                            </span>
                            {req.adminNote && req.status !== 'pending' && (
                              <p className="text-xs text-gray-500 mt-1 max-w-xs truncate">{req.adminNote}</p>
                            )}
                          </td>
                          <td className="p-3">
                            {req.status === 'pending' ? (
                              <div className="flex gap-2 justify-end">
                                <button
                                  onClick={async () => {
                                    const note = window.prompt('Enter admin note (optional):') || undefined;
                                    try {
                                      await api.post(`/admin/seller-wallet-recharge-requests/${req.id}/status`, {
                                        status: 'approved',
                                        adminNote: note
                                      });
                                      toast.success('Seller recharge request approved');
                                      fetchData();
                                    } catch (error) {
                                      toast.error(error.response?.data?.detail || 'Failed to approve request');
                                    }
                                  }}
                                  className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-sm"
                                >
                                  Approve
                                </button>
                                <button
                                  onClick={async () => {
                                    const note = window.prompt('Enter reason for rejection:') || undefined;
                                    try {
                                      await api.post(`/admin/seller-wallet-recharge-requests/${req.id}/status`, {
                                        status: 'rejected',
                                        adminNote: note
                                      });
                                      toast.success('Seller recharge request rejected');
                                      fetchData();
                                    } catch (error) {
                                      toast.error(error.response?.data?.detail || 'Failed to reject request');
                                    }
                                  }}
                                  className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-sm"
                                >
                                  Reject
                                </button>
                              </div>
                            ) : (
                              <div className="text-right text-xs text-gray-500">
                                {req.updatedAt && `Processed: ${new Date(req.updatedAt).toLocaleDateString()}`}
                              </div>
                            )}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Password Reset Modal */}
      {passwordResetModal && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/70 backdrop-blur-sm"
          onClick={passwordResetLoading ? undefined : closePasswordResetModal}
        >
          <div
            className="w-full max-w-lg bg-[rgba(18,18,18,0.98)] border border-[rgba(212,175,55,0.25)] rounded-xl shadow-2xl p-6"
            onClick={(e) => e.stopPropagation()}
          >
            {!passwordResetResult ? (
              <>
                <h3 className="text-xl font-semibold text-[#D4AF37] mb-2">Send Password Reset</h3>
                <p className="text-gray-400 text-sm mb-5">
                  This will generate a secure one-time reset link and email it to{' '}
                  <span className="text-white">{passwordResetModal.email}</span>
                  {passwordResetModal.name ? (
                    <> ({passwordResetModal.name})</>
                  ) : null}
                  . The link expires in 1 hour. The user's current password will not change until they open the link and choose a new one.
                </p>
                <div className="flex flex-wrap gap-2 justify-end">
                  <button
                    onClick={closePasswordResetModal}
                    disabled={passwordResetLoading}
                    className="px-4 py-2 rounded-md text-sm bg-[rgba(50,50,50,0.8)] text-gray-300 hover:bg-[rgba(70,70,70,0.9)] transition-colors disabled:opacity-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => handleSendPasswordReset(passwordResetModal)}
                    disabled={passwordResetLoading}
                    className="px-4 py-2 rounded-md text-sm bg-[#D4AF37] text-black font-semibold hover:bg-[#c9a531] transition-colors disabled:opacity-60"
                    data-testid="confirm-reset-password-btn"
                  >
                    {passwordResetLoading ? 'Sending...' : 'Send Reset Email'}
                  </button>
                </div>
              </>
            ) : (
              <>
                <h3 className="text-xl font-semibold text-[#D4AF37] mb-2">
                  {passwordResetResult.email_sent ? 'Reset Email Sent' : 'Reset Link Generated'}
                </h3>
                <p className="text-gray-400 text-sm mb-4">
                  {passwordResetResult.email_sent ? (
                    <>
                      A password reset email has been sent to{' '}
                      <span className="text-white">{passwordResetResult.email}</span>. The link
                      expires in 1 hour.
                    </>
                  ) : (
                    <>
                      Email delivery was not confirmed. You can share this one-time reset link with{' '}
                      <span className="text-white">{passwordResetResult.email}</span> manually via
                      WhatsApp, SMS, or in person. The link expires in 1 hour.
                    </>
                  )}
                </p>
                {passwordResetResult.reset_link ? (
                  <div className="mb-5">
                    <label className="block text-xs uppercase tracking-wide text-gray-500 mb-1">
                      Reset Link
                    </label>
                    <div className="flex gap-2">
                      <input
                        readOnly
                        value={passwordResetResult.reset_link}
                        onFocus={(e) => e.target.select()}
                        className="luxury-input flex-1 text-xs"
                        data-testid="reset-link-input"
                      />
                      <button
                        onClick={copyResetLink}
                        className="px-3 py-2 rounded-md text-xs bg-[#D4AF37] text-black font-semibold hover:bg-[#c9a531] transition-colors whitespace-nowrap"
                        data-testid="copy-reset-link-btn"
                      >
                        {resetLinkCopied ? 'Copied ✓' : 'Copy'}
                      </button>
                    </div>
                    <p className="text-xs text-gray-500 mt-2">
                      ⚠️ Treat this link like a password. Anyone with it can reset this account.
                    </p>
                  </div>
                ) : null}
                <div className="flex justify-end">
                  <button
                    onClick={closePasswordResetModal}
                    className="px-4 py-2 rounded-md text-sm bg-[#D4AF37] text-black font-semibold hover:bg-[#c9a531] transition-colors"
                  >
                    Done
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
 );
};

export default AdminDashboard;
