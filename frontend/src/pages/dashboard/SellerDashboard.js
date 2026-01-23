import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { useDropzone } from 'react-dropzone';
import { Package, Plus, Edit, Trash2, Upload, AlertCircle, CheckCircle, Tag, ShoppingCart, Clock, DollarSign, Wallet } from 'lucide-react';

const SellerDashboard = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [earnings, setEarnings] = useState(null);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('products');
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [productForm, setProductForm] = useState({ title: '', description: '', price: '', category: '' });
  const [uploadingImages, setUploadingImages] = useState({});
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

  useEffect(() => {
    fetchData();
    fetchCategories();
    fetchStoreNameRequest();
    fetchEarnings();
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
      const [productsRes, ordersRes] = await Promise.all([
        api.get('/products/my'),
        api.get('/orders/my')
      ]);
      setProducts(productsRes.data.products || []);
      setOrders(ordersRes.data.orders || []);
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

  const fetchStoreNameRequest = async () => {
    try {
      const res = await api.get('/seller/store-name-change');
      setStoreRequest(res.data.request || null);
    } catch (error) {
      // silently ignore
    }
  };

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      await api.post('/products', {
        ...productForm,
        price: parseFloat(productForm.price),
        category: productForm.category || null
      });
      toast.success('Product created successfully');
      setShowProductForm(false);
      setProductForm({ title: '', description: '', price: '', category: '' });
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create product');
    }
  };

  const handleUpdateProduct = async (e) => {
    e.preventDefault();
    try {
      await api.put(`/products/${editingProduct}`, {
        ...productForm,
        price: parseFloat(productForm.price),
        category: productForm.category || null
      });
      toast.success('Product updated successfully');
      setEditingProduct(null);
      setProductForm({ title: '', description: '', price: '', category: '' });
      fetchData();
    } catch (error) {
      toast.error('Failed to update product');
    }
  };

  const handleDeleteProduct = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;
    try {
      await api.delete(`/products/${productId}`);
      toast.success('Product deleted');
      fetchData();
    } catch (error) {
      toast.error('Failed to delete product');
    }
  };

  const handleImageUpload = async (productId, files) => {
    setUploadingImages(prev => ({ ...prev, [productId]: true }));
    try {
      for (const file of files) {
        const formData = new FormData();
        formData.append('file', file);
        await api.post(`/products/${productId}/upload-image`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' }
        });
      }
      toast.success('Images uploaded successfully');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to upload images');
    } finally {
      setUploadingImages(prev => ({ ...prev, [productId]: false }));
    }
  };

  const handleRemoveImage = async (productId, imageUrl) => {
    if (!window.confirm('Are you sure you want to remove this image?')) return;
    try {
      await api.delete(`/products/${productId}/remove-image`, {
        data: { imageUrl }
      });
      toast.success('Image removed successfully');
      fetchData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to remove image');
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

  const ImageDropzone = ({ productId }) => {
    const { getRootProps, getInputProps } = useDropzone({
      accept: { 'image/*': [] },
      maxFiles: 10,
      onDrop: (files) => handleImageUpload(productId, files)
    });

    return (
      <div
        {...getRootProps()}
        className="border-2 border-dashed border-[rgba(212,175,55,0.3)] rounded-lg p-4 text-center cursor-pointer hover:border-[#D4AF37] transition-colors"
      >
        <input {...getInputProps()} />
        <Upload className="w-6 h-6 mx-auto text-gray-400 mb-2" />
        <p className="text-sm text-gray-400">Drop images or click to upload (Max 10)</p>
      </div>
    );
  };

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
          <p className="text-gray-400 text-sm mb-1">Total Products</p>
          <p className="text-3xl font-bold text-[#D4AF37]">{products.length}</p>
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
            <Wallet className="w-3 h-3 text-[#D4AF37]" />
            Available: <span className="text-[#D4AF37] font-semibold ml-1">{earnings ? `$${earnings.availableBalance.toFixed(2)}` : '—'}</span>
          </p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Status</p>
          <span className={`status-badge ${user.verificationStatus === 'verified' ? 'status-verified' : 'status-pending'}`}>
            {user.verificationStatus}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 flex-wrap">
        <button
          onClick={() => setActiveTab('products')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'products'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
          data-testid="tab-products"
        >
          <Package className="w-4 h-4" />
          Products ({products.length})
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

      {/* Products Section */}
      {activeTab === 'products' && (
      <div className="luxury-card mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">My Products</h2>
          {user.verificationStatus === 'verified' && (
            <button
              onClick={() => {
                setShowProductForm(true);
                setEditingProduct(null);
                setProductForm({ title: '', description: '', price: '', category: '' });
              }}
              className="btn-gold"
              data-testid="add-product-btn"
            >
              <Plus className="w-4 h-4 inline mr-2" />
              Add Product
            </button>
          )}
        </div>

        {user.verificationStatus !== 'verified' ? (
          <p className="text-gray-400 text-center py-8">You need to be verified to add products</p>
        ) : (
          <div className="space-y-4">
            {products.map((product) => (
              <div key={product.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg" data-testid="seller-product">
                <div className="flex gap-4">
                  <div className="flex-shrink-0">
                    {product.images && product.images.length > 0 ? (
                      <img
                        src={product.images[0]}
                        alt={product.title}
                        className="w-24 h-24 object-cover rounded-lg"
                      />
                    ) : (
                      <div className="w-24 h-24 bg-[rgba(50,50,50,0.6)] rounded-lg flex items-center justify-center">
                        <Package className="w-8 h-8 text-gray-500" />
                      </div>
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-white mb-1">{product.title}</h3>
                    <p className="text-sm text-gray-400 mb-2">{product.description}</p>
                    <p className="text-[#D4AF37] font-bold">${product.price.toFixed(2)}</p>
                    <p className="text-xs text-gray-500 mt-1">
                      Images: {product.images?.length || 0}/10
                    </p>
                  </div>
                  <div className="flex flex-col gap-2">
                    <button
                      onClick={() => {
                        setEditingProduct(product.id);
                        setProductForm({
                          title: product.title,
                          description: product.description,
                          price: product.price.toString(),
                          category: product.category || ''
                        });
                      }}
                      className="p-2 hover:bg-[rgba(212,175,55,0.1)] rounded-lg transition-colors"
                      data-testid="edit-product-btn"
                    >
                      <Edit className="w-4 h-4 text-[#D4AF37]" />
                    </button>
                    <button
                      onClick={() => handleDeleteProduct(product.id)}
                      className="p-2 hover:bg-red-500/10 rounded-lg transition-colors"
                      data-testid="delete-product-btn"
                    >
                      <Trash2 className="w-4 h-4 text-red-400" />
                    </button>
                  </div>
                </div>
                
                {/* Category Badge */}
                {product.categoryName && (
                  <div className="mt-2">
                    <span className="inline-flex items-center gap-1 px-2 py-1 bg-[rgba(212,175,55,0.1)] text-[#D4AF37] rounded-full text-xs">
                      <Tag className="w-3 h-3" />
                      {product.categoryIcon} {product.categoryName}
                    </span>
                  </div>
                )}
                
                {/* Product Images Gallery with Remove Buttons */}
                {product.images && product.images.length > 0 && (
                  <div className="mt-4">
                    <p className="text-sm text-gray-400 mb-2">Product Images (click X to remove)</p>
                    <div className="flex flex-wrap gap-2">
                      {product.images.map((img, index) => (
                        <div key={index} className="relative group">
                          <img
                            src={img}
                            alt={`${product.title} - ${index + 1}`}
                            className="w-20 h-20 object-cover rounded-lg border border-gray-700"
                          />
                          <button
                            onClick={() => handleRemoveImage(product.id, img)}
                            className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center text-xs font-bold opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-600"
                            data-testid="remove-image-btn"
                            title="Remove image"
                          >
                            ✕
                          </button>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                <div className="mt-4">
                  {uploadingImages[product.id] ? (
                    <div className="text-center py-4"><div className="spinner mx-auto"></div></div>
                  ) : (
                    <ImageDropzone productId={product.id} />
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
      )}

      {/* Orders Section */}
      {activeTab === 'orders' && (
        <div className="luxury-card mb-8">
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

                  {/* Order Items (only seller's products) */}
                  <div className="space-y-3 border-t border-[rgba(212,175,55,0.1)] pt-4">
                    <p className="text-sm text-gray-400 mb-2">Your products in this order:</p>
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

                  {/* Order Total for Seller */}
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

      {/* Payouts Section */}
      {activeTab === 'payouts' && (
        <div className="luxury-card mb-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Payouts & Earnings</h2>
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
                        Your Wallet Address (TRC20)
                      </label>
                      <input
                        type="text"
                        value={payoutWallet}
                        onChange={(e) => setPayoutWallet(e.target.value)}
                        className="luxury-input w-full font-mono text-sm"
                        placeholder="Enter your TRC20 wallet address"
                        required
                      />
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

      {/* Product Form Modal */}
      {(showProductForm || editingProduct) && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-md w-full">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">
              {editingProduct ? 'Edit Product' : 'Add New Product'}
            </h2>
            <form onSubmit={editingProduct ? handleUpdateProduct : handleCreateProduct} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Title</label>
                <input
                  type="text"
                  required
                  value={productForm.title}
                  onChange={(e) => setProductForm({ ...productForm, title: e.target.value })}
                  className="luxury-input"
                  data-testid="product-title-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Description</label>
                <textarea
                  required
                  value={productForm.description}
                  onChange={(e) => setProductForm({ ...productForm, description: e.target.value })}
                  className="luxury-input min-h-[100px]"
                  data-testid="product-description-input"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Category</label>
                <select
                  value={productForm.category}
                  onChange={(e) => setProductForm({ ...productForm, category: e.target.value })}
                  className="luxury-input"
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
                  required
                  value={productForm.price}
                  onChange={(e) => setProductForm({ ...productForm, price: e.target.value })}
                  className="luxury-input"
                  data-testid="product-price-input"
                />
              </div>
              <div className="flex gap-2">
                <button type="submit" className="btn-gold flex-1" data-testid="save-product-btn">
                  {editingProduct ? 'Update' : 'Create'}
                </button>
                <button
                  type="button"
                  onClick={() => {
                    setShowProductForm(false);
                    setEditingProduct(null);
                    setProductForm({ title: '', description: '', price: '', category: '' });
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

export default SellerDashboard;
