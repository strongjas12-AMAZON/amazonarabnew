import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { useDropzone } from 'react-dropzone';
import { Package, Plus, Edit, Trash2, Upload, AlertCircle, CheckCircle } from 'lucide-react';

const SellerDashboard = () => {
  const { user } = useAuth();
  const [products, setProducts] = useState([]);
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showProductForm, setShowProductForm] = useState(false);
  const [editingProduct, setEditingProduct] = useState(null);
  const [productForm, setProductForm] = useState({ title: '', description: '', price: '' });
  const [uploadingImages, setUploadingImages] = useState({});
  const [showVerificationForm, setShowVerificationForm] = useState(false);
  const [verificationForm, setVerificationForm] = useState({
    merchantInviteCode: '',
    documentType: 'business_document'
  });

  useEffect(() => {
    fetchData();
  }, []);

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

  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      await api.post('/products', {
        ...productForm,
        price: parseFloat(productForm.price)
      });
      toast.success('Product created successfully');
      setShowProductForm(false);
      setProductForm({ title: '', description: '', price: '' });
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
        price: parseFloat(productForm.price)
      });
      toast.success('Product updated successfully');
      setEditingProduct(null);
      setProductForm({ title: '', description: '', price: '' });
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
      await api.post('/verification/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
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
        <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-2" data-testid="seller-dashboard-title">
          Seller Dashboard
        </h1>
        <p className="text-gray-400">Welcome back, {user.name}</p>
      </div>

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
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Total Products</p>
          <p className="text-3xl font-bold text-[#D4AF37]">{products.length}</p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Total Orders</p>
          <p className="text-3xl font-bold text-[#D4AF37]">{orders.length}</p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Status</p>
          <span className={`status-badge ${user.verificationStatus === 'verified' ? 'status-verified' : 'status-pending'}`}>
            {user.verificationStatus}
          </span>
        </div>
      </div>

      {/* Products Section */}
      <div className="luxury-card mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">My Products</h2>
          {user.verificationStatus === 'verified' && (
            <button
              onClick={() => {
                setShowProductForm(true);
                setEditingProduct(null);
                setProductForm({ title: '', description: '', price: '' });
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
                          price: product.price.toString()
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
                    setProductForm({ title: '', description: '', price: '' });
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
