import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { Users, Package, ShoppingCart, Code, CheckCircle, XCircle, Eye } from 'lucide-react';

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [users, setUsers] = useState([]);
  const [orders, setOrders] = useState([]);
  const [verificationDocs, setVerificationDocs] = useState([]);
  const [inviteCodes, setInviteCodes] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [usersRes, ordersRes, docsRes, codesRes] = await Promise.all([
        api.get('/admin/users'),
        api.get('/orders/my'),
        api.get('/verification/documents'),
        api.get('/admin/invite-codes')
      ]);

      setUsers(usersRes.data.users || []);
      setOrders(ordersRes.data.orders || []);
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

  const handleUpdateOrderStatus = async (orderId, status) => {
    try {
      await api.put(`/orders/${orderId}/status`, { status });
      toast.success('Order status updated');
      fetchData();
    } catch (error) {
      toast.error('Failed to update order status');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  const stats = [
    { label: 'Total Users', value: users.length, icon: Users },
    { label: 'Total Orders', value: orders.length, icon: ShoppingCart },
    { label: 'Pending Verifications', value: verificationDocs.filter(d => d.status === 'pending').length, icon: CheckCircle },
    { label: 'Invite Codes', value: inviteCodes.filter(c => !c.isUsed).length, icon: Code }
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
                <p className="text-3xl font-bold text-[#D4AF37]">{stat.value}</p>
              </div>
              <stat.icon className="w-12 h-12 text-[#D4AF37] opacity-50" />
            </div>
          </div>
        ))}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 flex-wrap">
        {['overview', 'users', 'orders', 'verifications', 'inviteCodes'].map((tab) => (
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
              <div className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg">
                <h3 className="font-semibold text-white mb-2">Recent Activity</h3>
                <p className="text-gray-400">Monitor your marketplace performance</p>
              </div>
              <div className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg">
                <h3 className="font-semibold text-white mb-2">Pending Actions</h3>
                <ul className="text-gray-400 space-y-2">
                  <li>• {verificationDocs.filter(d => d.status === 'pending').length} pending verifications</li>
                  <li>• {orders.filter(o => o.paymentStatus === 'pending_payment').length} orders awaiting confirmation</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'users' && (
          <div>
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

        {activeTab === 'orders' && (
          <div>
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">All Orders</h2>
            <div className="space-y-4">
              {orders.map((order) => (
                <div key={order.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg" data-testid="order-item">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <p className="text-white font-semibold">Order #{order.id.slice(0, 8)}</p>
                      <p className="text-sm text-gray-400">Buyer: {order.users?.name || 'N/A'}</p>
                      <p className="text-sm text-gray-400">Email: {order.users?.email || 'N/A'}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-[#D4AF37] font-bold text-xl">${order.totalAmount.toFixed(2)}</p>
                      <span className={`status-badge ${
                        order.paymentStatus === 'paid' || order.paymentStatus === 'completed' ? 'status-verified' :
                        order.paymentStatus === 'pending_payment' ? 'status-pending' :
                        'status-rejected'
                      }`}>
                        {order.paymentStatus}
                      </span>
                    </div>
                  </div>
                  
                  {order.paymentStatus === 'pending_payment' && (
                    <div className="flex gap-2 mt-3">
                      <button
                        onClick={() => handleUpdateOrderStatus(order.id, 'paid')}
                        className="btn-gold text-sm px-4 py-2"
                        data-testid="confirm-payment-btn"
                      >
                        Confirm Payment
                      </button>
                      <button
                        onClick={() => handleUpdateOrderStatus(order.id, 'cancelled')}
                        className="bg-red-500/20 text-red-400 text-sm px-4 py-2 rounded-lg hover:bg-red-500/30 transition-colors"
                      >
                        Cancel Order
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
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
                  
                  <a
                    href={doc.documentUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-2 text-[#D4AF37] hover:underline mb-3"
                  >
                    <Eye className="w-4 h-4" />
                    View Document
                  </a>
                  
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
