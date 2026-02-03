import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { ShoppingBag, Clock, CheckCircle, XCircle, Wallet, Plus, ArrowUp, ArrowDown, Copy, AlertTriangle } from 'lucide-react';

const ADMIN_WALLET_ADDRESS = process.env.REACT_APP_ADMIN_WALLET || 'TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU';

const BuyerDashboard = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [walletBalance, setWalletBalance] = useState(0);
  const [transactions, setTransactions] = useState([]);
  const [rechargeRequests, setRechargeRequests] = useState([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('orders');
  const [showRechargeModal, setShowRechargeModal] = useState(false);
  const [rechargeAmount, setRechargeAmount] = useState('');
  const [rechargeSubmitting, setRechargeSubmitting] = useState(false);
  const [confirmingDelivery, setConfirmingDelivery] = useState(null);

  useEffect(() => {
    fetchOrders();
    fetchWalletData();
  }, []);
  
  // NEW: Confirm delivery handler
  const handleConfirmDelivery = async (orderId) => {
    if (!window.confirm('Confirm that you have received this order?')) {
      return;
    }
    
    try {
      setConfirmingDelivery(orderId);
      await api.post(`/orders/${orderId}/confirm-delivery`);
      toast.success('Delivery confirmed! Seller payout initiated.');
      await fetchOrders();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to confirm delivery';
      toast.error(errorMsg);
    } finally {
      setConfirmingDelivery(null);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders/my');
      setOrders(response.data.orders || []);
    } catch (error) {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const fetchWalletData = async () => {
    try {
      const [balanceRes, transactionsRes, rechargeRes] = await Promise.all([
        api.get('/wallet/balance').catch(() => ({ data: { balance: 0 } })),
        api.get('/wallet/transactions').catch(() => ({ data: { transactions: [] } })),
        api.get('/wallet/recharge-requests').catch(() => ({ data: { rechargeRequests: [] } }))
      ]);
      setWalletBalance(balanceRes.data.balance || 0);
      setTransactions(transactionsRes.data.transactions || []);
      setRechargeRequests(rechargeRes.data.rechargeRequests || []);
    } catch (error) {
      console.error('Failed to load wallet data', error);
    }
  };

  const handleCopyWalletAddress = () => {
    navigator.clipboard.writeText(ADMIN_WALLET_ADDRESS);
    toast.success('Wallet address copied to clipboard!');
  };

  const handleRecharge = async (e) => {
    e.preventDefault();
    const amount = parseFloat(rechargeAmount || '0');
    if (!amount || amount <= 0) {
      toast.error('Enter a valid amount');
      return;
    }
    try {
      setRechargeSubmitting(true);
      await api.post('/wallet/recharge', {
        amount,
        paymentMethod: 'USDT_TRON'
      });
      toast.success('Recharge request submitted. Awaiting admin approval.');
      setRechargeAmount('');
      setShowRechargeModal(false);
      fetchWalletData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to submit recharge request');
    } finally {
      setRechargeSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending_payment':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'paid':
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'cancelled':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="mb-8">
        <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-2" data-testid="buyer-dashboard-title">
          Buyer Dashboard
        </h1>
        <p className="text-gray-400">Welcome back, {user.name}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-4 gap-6 mb-8">
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Wallet Balance</p>
          <p className="text-3xl font-bold text-[#D4AF37]">${walletBalance.toFixed(2)}</p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Total Orders</p>
          <p className="text-3xl font-bold text-[#D4AF37]">{orders.length}</p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Pending</p>
          <p className="text-3xl font-bold text-yellow-500">
            {orders.filter(o => o.paymentStatus === 'pending_payment').length}
          </p>
        </div>
        <div className="luxury-card">
          <p className="text-gray-400 text-sm mb-1">Completed</p>
          <p className="text-3xl font-bold text-green-500">
            {orders.filter(o => o.paymentStatus === 'completed' || o.paymentStatus === 'paid').length}
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8 flex-wrap">
        <button
          onClick={() => setActiveTab('orders')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'orders'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
        >
          <ShoppingBag className="w-4 h-4" />
          Orders ({orders.length})
        </button>
        <button
          onClick={() => setActiveTab('wallet')}
          className={`px-6 py-3 rounded-lg font-medium transition-all flex items-center gap-2 ${
            activeTab === 'wallet'
              ? 'bg-[#D4AF37] text-[#0a0a0a]'
              : 'bg-[rgba(30,30,30,0.6)] text-gray-300 hover:bg-[rgba(30,30,30,0.8)]'
          }`}
        >
          <Wallet className="w-4 h-4" />
          Wallet
        </button>
      </div>

      {/* Orders Tab */}
      {activeTab === 'orders' && (
      <div className="luxury-card">
        <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Order History</h2>
        
        {orders.length === 0 ? (
          <div className="text-center py-12">
            <ShoppingBag className="w-16 h-16 mx-auto text-gray-600 mb-4" />
            <p className="text-gray-400">No orders yet</p>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="p-6 bg-[rgba(30,30,30,0.6)] rounded-lg" data-testid="buyer-order">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <p className="text-white font-semibold">Order #{order.id.slice(0, 8).toUpperCase()}</p>
                      {getStatusIcon(order.paymentStatus)}
                    </div>
                    <p className="text-sm text-gray-400">
                      {new Date(order.createdAt).toLocaleDateString('en-US', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-[#D4AF37] font-bold text-2xl" data-testid="order-total">
                      ${order.totalAmount.toFixed(2)}
                    </p>
                    <span className={`status-badge mt-2 inline-block ${
                      order.paymentStatus === 'paid' || order.paymentStatus === 'completed' ? 'status-verified' :
                      order.paymentStatus === 'pending_payment' ? 'status-pending' :
                      'status-rejected'
                    }`}>
                      {order.paymentStatus.replace('_', ' ')}
                    </span>
                  </div>
                </div>

                {/* Order Items */}
                {order.orderItems && order.orderItems.length > 0 && (
                  <div className="space-y-2 border-t border-[rgba(212,175,55,0.1)] pt-4">
                    {order.orderItems.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          {item.product?.images?.[0] && (
                            <img
                              src={item.product.images[0]}
                              alt={item.product.title}
                              className="w-12 h-12 object-cover rounded"
                            />
                          )}
                          <div>
                            <p className="text-white text-sm">{item.product?.title || 'Product'}</p>
                            <p className="text-gray-500 text-xs">Quantity: {item.quantity}</p>
                          </div>
                        </div>
                        <p className="text-gray-400">${(item.price * item.quantity).toFixed(2)}</p>
                      </div>
                    ))}
                  </div>
                )}

                {/* Payment Info */}
                <div className="mt-4 p-3 bg-[rgba(20,20,20,0.6)] rounded-lg">
                  <p className="text-sm text-gray-400 mb-1">Payment Method</p>
                  <p className="text-[#D4AF37] font-medium">
                    {order.paymentMethod === 'WALLET' ? 'Wallet Balance' : 'USDT (TRC20)'}
                  </p>
                  {order.paymentStatus === 'pending_payment' && order.paymentMethod !== 'WALLET' && (
                    <p className="text-xs text-yellow-500 mt-2">
                      ⏳ Awaiting admin payment confirmation
                    </p>
                  )}
                </div>
                
                {/* NEW: Confirm Delivery Button */}
                {order.escrowStatus === 'shipped' && (
                  <div className="mt-4">
                    <button
                      onClick={() => handleConfirmDelivery(order.id)}
                      disabled={confirmingDelivery === order.id}
                      className="w-full bg-green-600 hover:bg-green-700 text-white py-3 px-6 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-green-600/50"
                    >
                      {confirmingDelivery === order.id ? 'Processing...' : '✓ Confirm Delivery Received'}
                    </button>
                    <p className="text-xs text-gray-400 mt-2 text-center">
                      Click to confirm you received the order. This will release payment to the seller.
                    </p>
                  </div>
                )}
                
                {/* Order Status Info */}
                {order.escrowStatus && (
                  <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
                    <p className="text-sm text-gray-400 mb-1">Order Status</p>
                    <div className="flex items-center gap-2">
                      {order.escrowStatus === 'awaiting_seller_deposit' && (
                        <>
                          <Clock className="w-4 h-4 text-orange-400" />
                          <span className="text-orange-400">Awaiting seller deposit confirmation</span>
                        </>
                      )}
                      {order.escrowStatus === 'deposit_received' && (
                        <>
                          <CheckCircle className="w-4 h-4 text-blue-400" />
                          <span className="text-blue-400">Ready for shipment</span>
                        </>
                      )}
                      {order.escrowStatus === 'shipped' && (
                        <>
                          <ShoppingBag className="w-4 h-4 text-purple-400" />
                          <span className="text-purple-400">Shipped by platform - awaiting your confirmation</span>
                        </>
                      )}
                      {order.escrowStatus === 'delivered' && (
                        <>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          <span className="text-green-400">Delivered & Confirmed</span>
                        </>
                      )}
                      {order.escrowStatus === 'settled' && (
                        <>
                          <CheckCircle className="w-4 h-4 text-green-400" />
                          <span className="text-green-400">Completed - Seller paid</span>
                        </>
                      )}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
      )}

      {/* Wallet Tab */}
      {activeTab === 'wallet' && (
        <div className="space-y-6">
          {/* Wallet Balance Card */}
          <div className="luxury-card">
            <div className="flex justify-between items-center mb-6">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Wallet Balance</h2>
              <button
                onClick={() => setShowRechargeModal(true)}
                className="btn-gold flex items-center gap-2"
              >
                <Plus className="w-4 h-4" />
                Recharge Wallet
              </button>
            </div>
            <div className="text-center py-8">
              <Wallet className="w-16 h-16 mx-auto text-[#D4AF37] mb-4" />
              <p className="text-5xl font-bold text-[#D4AF37] mb-2">${walletBalance.toFixed(2)}</p>
              <p className="text-gray-400">Available Balance</p>
            </div>
          </div>

          {/* Recharge Requests */}
          <div className="luxury-card">
            <h3 className="font-['Playfair_Display'] text-xl font-bold text-white mb-4">Recharge Requests</h3>
            {rechargeRequests.length === 0 ? (
              <p className="text-gray-400 text-sm">No recharge requests yet.</p>
            ) : (
              <div className="space-y-3">
                {rechargeRequests.map((req) => (
                  <div key={req.id} className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <p className="text-white font-semibold">${req.amount.toFixed(2)}</p>
                        <p className="text-xs text-gray-400">
                          {new Date(req.createdAt).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </p>
                      </div>
                      <span className={`status-badge ${
                        req.status === 'approved' ? 'status-verified' :
                        req.status === 'rejected' ? 'status-rejected' :
                        'status-pending'
                      }`}>
                        {req.status}
                      </span>
                    </div>
                    {req.adminNote && (
                      <p className="text-xs text-gray-500 mt-2">Note: {req.adminNote}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Transaction History */}
          <div className="luxury-card">
            <h3 className="font-['Playfair_Display'] text-xl font-bold text-white mb-4">Transaction History</h3>
            {transactions.length === 0 ? (
              <p className="text-gray-400 text-sm">No transactions yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="text-left text-gray-400 border-b border-[rgba(212,175,55,0.1)]">
                      <th className="py-2 pr-4">Date</th>
                      <th className="py-2 pr-4">Type</th>
                      <th className="py-2 pr-4">Amount</th>
                      <th className="py-2 pr-4">Balance</th>
                      <th className="py-2 pr-4">Description</th>
                    </tr>
                  </thead>
                  <tbody>
                    {transactions.map((t) => (
                      <tr key={t.id} className="border-b border-[rgba(212,175,55,0.05)]">
                        <td className="py-2 pr-4 text-gray-300">
                          {new Date(t.createdAt).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'short',
                            day: 'numeric',
                            hour: '2-digit',
                            minute: '2-digit'
                          })}
                        </td>
                        <td className="py-2 pr-4">
                          <span className={`inline-flex items-center gap-1 ${
                            t.type === 'recharge' ? 'text-green-400' :
                            t.type === 'purchase' ? 'text-red-400' :
                            'text-gray-400'
                          }`}>
                            {t.type === 'recharge' ? <ArrowUp className="w-3 h-3" /> :
                             t.type === 'purchase' ? <ArrowDown className="w-3 h-3" /> : null}
                            {t.type}
                          </span>
                        </td>
                        <td className={`py-2 pr-4 font-semibold ${
                          t.amount >= 0 ? 'text-green-400' : 'text-red-400'
                        }`}>
                          {t.amount >= 0 ? '+' : ''}${t.amount.toFixed(2)}
                        </td>
                        <td className="py-2 pr-4 text-[#D4AF37]">${t.newBalance.toFixed(2)}</td>
                        <td className="py-2 pr-4 text-gray-400 text-xs">{t.description || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recharge Modal */}
      {showRechargeModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-md w-full">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">Recharge Wallet</h2>
            <p className="text-sm text-gray-400 mb-6">
              Recharge requests require admin approval. You'll be notified once approved.
            </p>

            {/* Wallet Address Section */}
            <div className="mb-6 p-4 bg-[rgba(20,20,20,0.6)] rounded-lg border border-[rgba(212,175,55,0.2)]">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Send USDT (TRC20) to this address:
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={ADMIN_WALLET_ADDRESS}
                  readOnly
                  className="luxury-input flex-1 font-mono text-sm text-[#D4AF37]"
                  data-testid="wallet-address-input"
                />
                <button
                  type="button"
                  onClick={handleCopyWalletAddress}
                  className="btn-gold-outline px-4 flex items-center gap-2"
                  data-testid="copy-wallet-btn"
                >
                  <Copy className="w-4 h-4" />
                </button>
              </div>
            </div>

          <div className="mb-6 w-full flex justify-center items-center ">
  <img
    src="/adminWallet.png"
    alt="admin wallet"
    className="w-1/2 h-1/2 object-cover "
  />
</div>


            {/* Warning Message */}
            <div className="mb-6 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg flex gap-2">
              <AlertTriangle className="w-5 h-5 text-yellow-500 flex-shrink-0" />
              <div className="text-sm text-yellow-200">
                <p className="font-semibold mb-1">Important:</p>
                <p>Only send USDT on the TRC20 network. After sending, submit your recharge request below.</p>
              </div>
            </div>

            <form onSubmit={handleRecharge} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Amount (USD)
                </label>
                <input
                  type="number"
                  min="0.01"
                  step="0.01"
                  value={rechargeAmount}
                  onChange={(e) => setRechargeAmount(e.target.value)}
                  className="luxury-input w-full"
                  placeholder="Enter amount you sent"
                  required
                />
              </div>
              <div className="flex gap-2">
                <button
                  type="button"
                  onClick={() => {
                    setShowRechargeModal(false);
                    setRechargeAmount('');
                  }}
                  className="btn-gold-outline flex-1"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={rechargeSubmitting}
                  className="btn-gold flex-1 disabled:opacity-50"
                >
                  {rechargeSubmitting ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default BuyerDashboard;
