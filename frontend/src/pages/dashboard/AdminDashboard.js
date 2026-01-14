import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { Users, Package, ShoppingCart, Code, CheckCircle, XCircle, Eye, Clock, DollarSign, Trash2 } from 'lucide-react';

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
  const [loading, setLoading] = useState(true);

  const USERS_PER_PAGE = 10;

  // Calculate pagination for users (client-side)
  const usersTotalPages = Math.max(1, Math.ceil(allUsers.length / USERS_PER_PAGE));
  const startIndex = (usersPage - 1) * USERS_PER_PAGE;
  const endIndex = startIndex + USERS_PER_PAGE;
  const users = allUsers.slice(startIndex, endIndex);

  useEffect(() => {
    fetchData();
  }, []);

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
      api.get('/admin/store-name-requests').catch(err => ({ error: err }))
    ]);

    // Handle each result independently
    try {
      // Users (fetch all, pagination handled on frontend)
      if (results[0].status === 'fulfilled' && !results[0].value.error) {
        const usersResponse = results[0].value.data;
        setAllUsers(usersResponse?.users || []);
      } else {
        setAllUsers([]);
      }

      // Orders
      if (results[1].status === 'fulfilled' && !results[1].value.error) {
        setOrders(results[1].value.data?.orders || []);
      } else {
        setOrders([]);
      }

      // Products
      if (results[2].status === 'fulfilled' && !results[2].value.error) {
        setProducts(results[2].value.data?.products || []);
      } else {
        toast.error('Failed to load products. Check backend logs.');
        setProducts([]);
      }
      // Verification Documents
      if (results[3].status === 'fulfilled' && !results[3].value.error) {
        setVerificationDocs(results[3].value.data?.documents || []);
      } else {
        setVerificationDocs([]);
      }

      // Invite Codes
      if (results[4].status === 'fulfilled' && !results[4].value.error) {
        setInviteCodes(results[4].value.data?.codes || []);
      } else {
        setInviteCodes([]);
      }

      // Store name change requests
      if (results[5].status === 'fulfilled' && !results[5].value.error) {
        setStoreNameRequests(results[5].value.data?.requests || []);
      } else {
        setStoreNameRequests([]);
      }
    } catch (error) {
      // Silently handle errors - individual requests already handled above
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
    if (!window.confirm(`Are you sure you want to remove "${productTitle}" from the marketplace?`)) return;
    try {
      await api.delete(`/products/${productId}`);
      toast.success('Product removed from marketplace');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete product');
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

  const handleCompleteOrder = async (orderId) => {
    try {
      await api.put(`/orders/${orderId}/status`, { status: 'completed' });
      toast.success('✅ Order marked as completed!');
      fetchData();
    } catch (error) {
      toast.error('Failed to complete order');
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;
    
    try {
      await api.put(`/orders/${orderId}/status`, { status: 'cancelled' });
      toast.success('Order cancelled');
      fetchData();
    } catch (error) {
      toast.error('Failed to cancel order');
    }
  };

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

  const bannedUsers = allUsers.filter(
    (u) => u.banStatus && u.banStatus !== 'active'
  );

  const stats = [
    { label: 'Total Users', value: allUsers.length, icon: Users, color: 'text-blue-400' },
    { label: 'Total Products', value: products.length, icon: Package, color: 'text-purple-400' },
    { label: 'Pending Payments', value: pendingPaymentOrders.length, icon: Clock, color: 'text-yellow-400' },
    { label: 'Pending Verifications', value: verificationDocs.filter(d => d.status === 'pending').length, icon: CheckCircle, color: 'text-orange-400' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-2" data-testid="admin-dashboard-title">
          Admin Dashboard
        </h1>
        <p className="text-gray-400">Welcome back, {user.name}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {stats.map((stat) => (
          <div key={stat.label} className="luxury-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-gray-400 text-sm mb-1">{stat.label}</p>
                <p className={`text-3xl font-bold ${stat.color}`}>{stat.value}</p>
              </div>
              <stat.icon className={`w-12 h-12 ${stat.color} opacity-50`} />
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 flex-wrap">
        {['overview', 'orders', 'products', 'users', 'verifications', 'inviteCodes', 'bannedUsers', 'storeRequests'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 rounded-lg font-medium transition-all ${
              activeTab === tab
                ? 'bg-[#D4AF37] text-[#0a0a0a]'
                : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
            }`}
            data-testid={`tab-${tab}`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1).replace(/([A-Z])/g, ' $1')}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      <div className="luxury-card">
        {activeTab === 'overview' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Overview</h2>
            <div className="space-y-4">
              <div className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg border border-yellow-500/30">
                <div className="flex items-center gap-3 mb-2">
                  <Clock className="w-6 h-6 text-yellow-400" />
                  <h3 className="font-semibold text-white text-lg">Pending Payment Confirmations</h3>
                </div>
                <p className="text-gray-400 mb-2">{pendingPaymentOrders.length} orders awaiting payment verification</p>
                {pendingPaymentOrders.length > 0 && (
                  <button
                    onClick={() => setActiveTab('orders')}
                    className="text-[#D4AF37] hover:underline text-sm"
                  >
                    View Pending Orders →
                  </button>
                )}
              </div>

              <div className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg">
                <h3 className="font-semibold text-white mb-2">Quick Stats</h3>
                <ul className="text-gray-400 space-y-2">
                  <li>• Total Orders: {orders.length}</li>
                  <li>• Paid Orders: {paidOrders.length}</li>
                  <li>• Completed Orders: {completedOrders.length}</li>
                  <li>• Pending Verifications: {verificationDocs.filter(d => d.status === 'pending').length}</li>
                </ul>
              </div>
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
                        {order.order_items && order.order_items.length > 0 && (
                          <div className="mb-4 p-3 bg-[rgba(20,20,20,0.4)] rounded-lg">
                            <p className="text-sm text-gray-400 mb-2">Order Items:</p>
                            {order.order_items.map((item, idx) => (
                              <div key={idx} className="text-sm text-gray-300">
                                • {item.products?.title || 'Product'} x {item.quantity} - ${(item.price * item.quantity).toFixed(2)}
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

        {activeTab === 'products' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">
              All Products ({products.length})
            </h2>
            <p className="text-gray-400 text-sm mb-6">
              Manage all products in the marketplace. Remove products that violate policies.
            </p>
            
            {products.length === 0 ? (
              <div className="text-center py-12">
                <Package className="w-16 h-16 mx-auto text-gray-600 mb-4" />
                <p className="text-gray-400">No products in the marketplace yet</p>
              </div>
            ) : (
              <div className="space-y-4">
                {products.map((product) => (
                  <div key={product.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg border border-[rgba(212,175,55,0.1)]">
                    <div className="flex gap-4">
                      {/* Product Image */}
                      <div className="flex-shrink-0">
                        {product.images && product.images.length > 0 ? (
                          <img
                            src={product.images[0]}
                            alt={product.title}
                            className="w-20 h-20 object-cover rounded-lg"
                          />
                        ) : (
                          <div className="w-20 h-20 bg-[rgba(50,50,50,0.6)] rounded-lg flex items-center justify-center">
                            <Package className="w-8 h-8 text-gray-500" />
                          </div>
                        )}
                      </div>
                      
                      {/* Product Info */}
                      <div className="flex-1 min-w-0">
                        <h3 className="font-semibold text-white text-lg truncate">{product.title}</h3>
                        <p className="text-gray-400 text-sm line-clamp-1">{product.description}</p>
                        <div className="flex flex-wrap gap-2 mt-2">
                          <span className="text-[#D4AF37] font-bold">${product.price?.toFixed(2)}</span>
                          {product.categoryName && (
                            <span className="px-2 py-0.5 bg-[rgba(212,175,55,0.1)] text-[#D4AF37] rounded text-xs">
                              {product.categoryIcon} {product.categoryName}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {product.users?.storeName ? (
                            <>Store: {product.users.storeName} ({product.users?.email || 'N/A'})</>
                          ) : (
                            <>Seller: {product.users?.name || 'Unknown'} ({product.users?.email || 'N/A'})</>
                          )}
                          {product.users?.verificationStatus === 'verified' && (
                            <span className="ml-2 text-green-400">✓ Verified</span>
                          )}
                        </p>
                      </div>
                      
                      {/* Actions */}
                      <div className="flex-shrink-0 flex items-center">
                        <button
                          onClick={() => handleDeleteProduct(product.id, product.title)}
                          className="p-3 bg-red-500/10 hover:bg-red-500/20 text-red-400 rounded-lg transition-colors flex items-center gap-2"
                          data-testid="admin-delete-product-btn"
                          title="Remove from marketplace"
                        >
                          <Trash2 className="w-5 h-5" />
                          <span className="hidden sm:inline">Remove</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'users' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">
              All Users
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[rgba(212,175,55,0.2)]">
                    <th className="text-left p-3 text-gray-400 font-medium">Name</th>
                    <th className="text-left p-3 text-gray-400 font-medium">Email</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden sm:table-cell">Role</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden md:table-cell">Verification</th>
                    <th className="text-left p-3 text-gray-400 font-medium hidden lg:table-cell">Store</th>
                    <th className="text-left p-3 text-gray-400 font-medium">status</th>
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
                        <span className={`status-badge ${
                          u.verificationStatus === 'verified' ? 'status-verified' :
                          u.verificationStatus === 'pending' ? 'status-pending' :
                          u.verificationStatus === 'rejected' ? 'status-rejected' :
                          'bg-gray-500/20 text-gray-400'
                        }`}>
                          {u.verificationStatus}
                        </span>
                      </td>
                      <td className="p-3 hidden lg:table-cell">
                        {u.role === 'seller' ? (
                          <span className="text-gray-300">{u.storeName || '—'}</span>
                        ) : (
                          <span className="text-gray-500">—</span>
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
              {/* Pagination controls - show only page numbers (1, 2, 3, ...) */}
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

        {activeTab === 'verifications' && (
          <div>
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
                  
                  {doc.documentUrl ? (
                    <a
                      href={doc.documentUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 text-[#D4AF37] hover:underline mb-3"
                      data-testid="view-document-link"
                    >
                      <Eye className="w-4 h-4" />
                      View Document (Signed URL - expires in 1 hour)
                    </a>
                  ) : (
                    <p className="text-gray-500 text-sm mb-3">Document URL unavailable</p>
                  )}
                  
                  {doc.status === 'pending' && (
                    <div className="flex gap-2">
                      <button
                        onClick={() => handleReviewVerification(doc.id, 'verified')}
                        className="btn-gold text-sm px-4 py-2"
                        data-testid="approve-verification-btn"
                      >
                        <CheckCircle className="w-4 h-4 inline mr-1" />
                        Approve
                      </button>
                      <button
                        onClick={() => {
                          const reason = prompt('Rejection reason:');
                          if (reason) handleReviewVerification(doc.id, 'rejected', reason);
                        }}
                        className="bg-red-500/20 text-red-400 text-sm px-4 py-2 rounded-lg hover:bg-red-500/30 transition-colors"
                        data-testid="reject-verification-btn"
                      >
                        <XCircle className="w-4 h-4 inline mr-1" />
                        Reject
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'inviteCodes' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Merchant Invite Codes</h2>
              <button
                onClick={handleCreateInviteCode}
                className="btn-gold"
                data-testid="create-invite-code-btn"
              >
                Create New Code
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {inviteCodes.map((code) => (
                <div
                  key={code.id}
                  className={`p-4 rounded-lg border-2 ${
                    code.isUsed
                      ? 'bg-[rgba(30,30,30,0.3)] border-gray-600'
                      : 'bg-[rgba(212,175,55,0.1)] border-[#D4AF37]'
                  }`}
                  data-testid="invite-code"
                >
                  <div className="text-center">
                    <p className="text-2xl font-mono font-bold text-[#D4AF37] mb-2">{code.code}</p>
                    <span className={`status-badge ${
                      code.isUsed ? 'bg-gray-500/20 text-gray-400' : 'status-pending'
                    }`}>
                      {code.isUsed ? 'Used' : 'Available'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminDashboard;