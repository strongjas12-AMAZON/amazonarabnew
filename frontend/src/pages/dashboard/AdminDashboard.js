import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { 
  Users, Package, ShoppingCart, Code, CheckCircle, XCircle, Eye, 
  Clock, DollarSign, Trash2, Plus, Edit, Search, Database, 
  ToggleLeft, ToggleRight, X, Save
} from 'lucide-react';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState([]);
  const [verificationDocs, setVerificationDocs] = useState([]);
  const [inviteCodes, setInviteCodes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [categories, setCategories] = useState([]);
  
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

  useEffect(() => {
    fetchData();
    fetchCategories();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories');
      setCategories(response.data.categories || []);
    } catch (error) {
      console.error('Failed to load categories');
    }
  };

  const fetchData = async () => {
    try {
      const [usersRes, ordersRes, productsRes, docsRes, codesRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/orders/my'),
        api.get('/admin/products'),
        api.get('/verification/documents'),
        api.get('/admin/invite-codes')
      ]);

      setUsers(usersRes.data.users || []);
      setOrders(ordersRes.data.orders || []);
      setProducts(productsRes.data.products || []);
      setVerificationDocs(docsRes.data.documents || []);
      setInviteCodes(codesRes.data.codes || []);
    } catch (error) {
      toast.error('Failed to load data');
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

  const stats = {
    totalUsers: users.length,
    buyers: users.filter(u => u.role === 'buyer').length,
    sellers: users.filter(u => u.role === 'seller').length,
    verifiedSellers: users.filter(u => u.role === 'seller' && u.verificationStatus === 'verified').length,
    pendingVerifications: verificationDocs.filter(d => d.status === 'pending').length,
    totalProducts: products.length,
    totalOrders: orders.length,
    pendingPayments: orders.filter(o => o.paymentStatus === 'pending_payment').length,
    paidOrders: orders.filter(o => o.paymentStatus === 'paid').length,
    completedOrders: orders.filter(o => o.paymentStatus === 'completed').length,
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
      <div className="flex flex-wrap gap-2 mb-8">
        {['overview', 'products', 'orders', 'users', 'verifications', 'inviteCodes'].map((tab) => (
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
            {tab.charAt(0).toUpperCase() + tab.slice(1).replace(/([A-Z])/g, ' $1')}
          </button>
        ))}
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
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
            <p className="text-gray-400 text-sm mb-1">Completed Orders</p>
            <p className="text-3xl font-bold text-green-400">{stats.completedOrders}</p>
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
                  <th className="text-left p-3 text-gray-400 font-medium">Role</th>
                  <th className="text-left p-3 text-gray-400 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id} className="border-b border-[rgba(212,175,55,0.1)]">
                    <td className="p-3 text-white">{u.name}</td>
                    <td className="p-3 text-gray-400">{u.email}</td>
                    <td className="p-3">
                      <span className={`status-badge ${
                        u.role === 'admin' ? 'bg-purple-500/20 text-purple-400' :
                        u.role === 'seller' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-green-500/20 text-green-400'
                      }`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="p-3">
                      <span className={`status-badge ${
                        u.verificationStatus === 'verified' ? 'status-verified' :
                        u.verificationStatus === 'pending' ? 'status-pending' :
                        u.verificationStatus === 'rejected' ? 'status-rejected' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>
                        {u.verificationStatus}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
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

      {/* Invite Codes Tab */}
      {activeTab === 'inviteCodes' && (
        <div className="luxury-card">
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

      {/* Product Form Modal */}
      {(showProductForm || editingProduct) && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-lg w-full max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">
                {editingProduct ? 'Edit Product' : 'Add New Product'}
              </h2>
              <button
                onClick={() => {
                  setShowProductForm(false);
                  setEditingProduct(null);
                  resetProductForm();
                }}
                className="text-gray-400 hover:text-white"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
                <input
                  type="text"
                  required
                  value={productForm.title}
                  onChange={(e) => setProductForm({ ...productForm, title: e.target.value })}
                  className="luxury-input w-full"
                  placeholder="Product title"
                  data-testid="product-title-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                <textarea
                  required
                  value={productForm.description}
                  onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
                  className="luxury-input w-full min-h-[100px]"
                  placeholder="Product description"
                  data-testid="product-description-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                <select
                  value={productForm.category}
                  onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                  className="luxury-input w-full"
                  data-testid="product-category-input"
                >
                  <option value="">Select a category</option>
                  {categories.map((cat) => (
                    <option key={cat.id} value={cat.id}>
                      {cat.icon} {cat.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Price ($)</label>
                <input
                  type="number"
                  step="0.01"
                  min="0"
                  required
                  value={productForm.price}
                  onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                  className="luxury-input w-full"
                  placeholder="0.00"
                  data-testid="product-price-input"
                />
              </div>
              <div className="flex gap-2 pt-4">
                <button type="submit" className="btn-gold flex-1" data-testid="save-product-btn">
                  <Save className="w-4 h-4 inline mr-2" />
                  {editingProduct ? 'Update Product' : 'Create Product'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowProductForm(false);
                    setEditingProduct(null);
                    resetProductForm();
                  }}
                  className="btn-gold-outline flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
