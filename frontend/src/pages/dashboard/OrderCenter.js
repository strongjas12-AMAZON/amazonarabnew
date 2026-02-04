import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { supabase } from '../../lib/supabase';
import { toast } from 'sonner';
import {
  Package, Truck, Clock, CheckCircle, AlertTriangle, RefreshCw,
  ShoppingBag, MapPin, Calendar, DollarSign, User, ChevronRight,
  Send, X, Search, Filter, Eye, MessageSquare, Wallet
} from 'lucide-react';

// Order status configuration
const ORDER_STATUSES = {
  pending_payment: {
    label: 'Pending Payment',
    icon: Clock,
    color: 'yellow',
    bgColor: 'bg-yellow-500/10',
    borderColor: 'border-yellow-500/30',
    textColor: 'text-yellow-400',
    description: 'Waiting for buyer payment'
  },
  to_be_shipped: {
    label: 'To Be Shipped',
    icon: Package,
    color: 'blue',
    bgColor: 'bg-blue-500/10',
    borderColor: 'border-blue-500/30',
    textColor: 'text-blue-400',
    description: 'Ready to ship'
  },
  to_be_received: {
    label: 'To Be Received',
    icon: Truck,
    color: 'purple',
    bgColor: 'bg-purple-500/10',
    borderColor: 'border-purple-500/30',
    textColor: 'text-purple-400',
    description: 'In transit'
  },
  to_be_evaluated: {
    label: 'To Be Evaluated',
    icon: MessageSquare,
    color: 'indigo',
    bgColor: 'bg-indigo-500/10',
    borderColor: 'border-indigo-500/30',
    textColor: 'text-indigo-400',
    description: 'Awaiting buyer review'
  },
  after_sales: {
    label: 'After-Sales',
    icon: AlertTriangle,
    color: 'orange',
    bgColor: 'bg-orange-500/10',
    borderColor: 'border-orange-500/30',
    textColor: 'text-orange-400',
    description: 'Refund/Return requests'
  },
  completed: {
    label: 'Completed',
    icon: CheckCircle,
    color: 'green',
    bgColor: 'bg-green-500/10',
    borderColor: 'border-green-500/30',
    textColor: 'text-green-400',
    description: 'Order completed'
  }
};

// Courier options
const COURIERS = [
  { code: 'dhl', name: 'DHL Express', icon: '📦' },
  { code: 'fedex', name: 'FedEx', icon: '📫' },
  { code: 'ups', name: 'UPS', icon: '📬' },
  { code: 'aramex', name: 'Aramex', icon: '🚚' },
  { code: 'smsa', name: 'SMSA Express', icon: '📮' },
  { code: 'sf_express', name: 'SF Express', icon: '🏃' },
  { code: 'other', name: 'Other Courier', icon: '📨' },
];

const OrderCenter = ({ onDepositSubmitted }) => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('to_be_shipped');
  const [orders, setOrders] = useState([]);
  const [counts, setCounts] = useState({});
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [showShipModal, setShowShipModal] = useState(false);
  const [showRefundModal, setShowRefundModal] = useState(false);
  const [shipmentForm, setShipmentForm] = useState({
    trackingNumber: '',
    courierName: '',
    courierCode: '',
    estimatedDelivery: '',
    deliveryNotes: ''
  });
  const [refundResponse, setRefundResponse] = useState({
    action: '',
    sellerResponse: '',
    approvedAmount: ''
  });
  const [depositingOrderId, setDepositingOrderId] = useState(null);
  const [walletBalance, setWalletBalance] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [refunds, setRefunds] = useState([]);
  const [refundCounts, setRefundCounts] = useState({});
  
  // USDT Deposit Payment States
  const [showUsdtDepositModal, setShowUsdtDepositModal] = useState(false);
  const [usdtDepositForm, setUsdtDepositForm] = useState({
    transactionHash: '',
    notes: ''
  });
  const [submittingUsdtDeposit, setSubmittingUsdtDeposit] = useState(false);

  // Fetch orders for Order Center
  const fetchOrders = useCallback(async (status = null) => {
    try {
      setLoading(true);
      const params = status ? { status } : {};
      const response = await api.get('/seller/order-center', { params });
      setOrders(response.data.orders || []);
      setCounts(response.data.counts || {});
    } catch (error) {
      console.error('Failed to fetch orders:', error);
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  }, []);

  // Fetch refunds
  const fetchRefunds = useCallback(async () => {
    try {
      const response = await api.get('/seller/refunds');
      setRefunds(response.data.refunds || []);
      setRefundCounts(response.data.counts || {});
    } catch (error) {
      console.error('Failed to fetch refunds:', error);
    }
  }, []);

  // NEW: Fetch wallet balance
  const fetchWalletBalance = async () => {
    try {
      const res = await api.get('/seller/wallet/balance');
      setWalletBalance(res.data.wallet || null);
    } catch (error) {
      console.error('Failed to load wallet balance', error);
    }
  };
  
  // NEW: Handle deposit for order
  const handleDepositForOrder = async (orderId, depositAmount) => {
    if (!window.confirm(`Deposit $${depositAmount.toFixed(2)} to unlock this order and proceed with fulfillment?`)) {
      return;
    }
    
    try {
      setDepositingOrderId(orderId);
      await api.post('/seller/wallet/deposit-for-order', {
        orderId: orderId,
        amount: depositAmount
      });
      toast.success('Deposit successful! Order unlocked and ready for shipment.');
      await fetchOrders(activeTab === 'after_sales' ? null : activeTab);
      await fetchWalletBalance();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to deposit';
      toast.error(errorMsg);
    } finally {
      setDepositingOrderId(null);
    }
  };

  // Submit USDT Deposit Payment Proof
  const handleSubmitUsdtDeposit = async () => {
    if (!usdtDepositForm.transactionHash.trim()) {
      toast.error('Transaction hash is required');
      return;
    }
    
    // Basic validation for transaction hash format
    const hash = usdtDepositForm.transactionHash.trim();
    if (hash.length < 30) {
      toast.error('Transaction hash appears to be invalid. Please check and try again.');
      return;
    }
    
    try {
      setSubmittingUsdtDeposit(true);
      
      await api.post(`/seller/orders/${selectedOrder.id}/submit-usdt-deposit`, {
        orderId: selectedOrder.id,
        transactionHash: hash,
        notes: usdtDepositForm.notes.trim() || null
      });
      
      toast.success('Payment proof submitted successfully! Awaiting admin confirmation.');
      setShowUsdtDepositModal(false);
      setUsdtDepositForm({ transactionHash: '', notes: '' });
      
      // Refresh orders to show updated status
      await fetchOrders(activeTab === 'after_sales' ? null : activeTab);
      
      // Notify parent component to refresh pending deposit orders
      if (onDepositSubmitted) {
        await onDepositSubmitted();
      }
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to submit payment proof';
      toast.error(errorMsg);
    } finally {
      setSubmittingUsdtDeposit(false);
    }
  };


  // Initial data load
  useEffect(() => {
    if (user) {
      fetchOrders(activeTab === 'after_sales' ? null : activeTab);
      fetchRefunds();
      fetchWalletBalance();
    }
  }, [user, activeTab, fetchOrders, fetchRefunds]);

  // Real-time subscription for order updates
  useEffect(() => {
    if (!user) return;

    const ordersChannel = supabase
      .channel('orders-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'orders'
      }, (payload) => {
        console.log('Order update:', payload);
        fetchOrders(activeTab === 'after_sales' ? null : activeTab);
      })
      .subscribe();

    const shipmentsChannel = supabase
      .channel('shipments-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'shipments'
      }, (payload) => {
        console.log('Shipment update:', payload);
        fetchOrders(activeTab === 'after_sales' ? null : activeTab);
      })
      .subscribe();

    const refundsChannel = supabase
      .channel('refunds-changes')
      .on('postgres_changes', {
        event: '*',
        schema: 'public',
        table: 'refunds'
      }, (payload) => {
        console.log('Refund update:', payload);
        fetchRefunds();
        if (activeTab === 'after_sales') {
          fetchOrders(null);
        }
      })
      .subscribe();

    return () => {
      supabase.removeChannel(ordersChannel);
      supabase.removeChannel(shipmentsChannel);
      supabase.removeChannel(refundsChannel);
    };
  }, [user, activeTab, fetchOrders, fetchRefunds]);

  // Handle ship order
  const handleShipOrder = async () => {
    if (!selectedOrder || !shipmentForm.trackingNumber || !shipmentForm.courierName) {
      toast.error('Please fill in tracking number and courier');
      return;
    }

    try {
      setSubmitting(true);
      await api.post(`/seller/orders/${selectedOrder.id}/ship`, shipmentForm);
      toast.success('Order shipped successfully!');
      setShowShipModal(false);
      setSelectedOrder(null);
      setShipmentForm({
        trackingNumber: '',
        courierName: '',
        courierCode: '',
        estimatedDelivery: '',
        deliveryNotes: ''
      });
      fetchOrders(activeTab);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to ship order');
    } finally {
      setSubmitting(false);
    }
  };

  // Handle refund response
  const handleRefundResponse = async (refundId) => {
    if (!refundResponse.action) {
      toast.error('Please select an action');
      return;
    }

    try {
      setSubmitting(true);
      await api.put(`/seller/refunds/${refundId}`, {
        action: refundResponse.action,
        sellerResponse: refundResponse.sellerResponse,
        approvedAmount: refundResponse.action === 'approve' ? parseFloat(refundResponse.approvedAmount) : null
      });
      toast.success(`Refund ${refundResponse.action === 'approve' ? 'approved' : 'rejected'}`);
      setShowRefundModal(false);
      setRefundResponse({ action: '', sellerResponse: '', approvedAmount: '' });
      fetchRefunds();
      fetchOrders(activeTab);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to respond to refund');
    } finally {
      setSubmitting(false);
    }
  };

  // Mark order as delivered
  const handleMarkDelivered = async (orderId) => {
    try {
      await api.put(`/seller/orders/${orderId}/shipment`, {
        deliveryStatus: 'delivered'
      });
      toast.success('Order marked as delivered');
      fetchOrders(activeTab);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to update status');
    }
  };

  // Filter orders based on search
  const filteredOrders = orders.filter(order => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    return (
      order.id?.toLowerCase().includes(searchLower) ||
      order.buyer?.name?.toLowerCase().includes(searchLower) ||
      order.buyer?.email?.toLowerCase().includes(searchLower)
    );
  });

  // Get orders for current tab
  const getTabOrders = () => {
    if (activeTab === 'after_sales') {
      // For after-sales, show orders with pending refunds
      return filteredOrders.filter(order => {
        const hasRefund = refunds.some(r => 
          r.orderId === order.id && ['pending', 'seller_review'].includes(r.status)
        );
        return order.orderStatus === 'after_sales' || hasRefund;
      });
    }
    return filteredOrders.filter(order => {
      const paymentStatus = order.paymentStatus;
      const orderStatus = order.orderStatus || 'pending_payment';
      
      if (activeTab === 'pending_payment') {
        return paymentStatus === 'pending_payment' || orderStatus === 'pending_payment';
      }
      if (activeTab === 'to_be_shipped') {
        return paymentStatus === 'paid' && ['pending_payment', 'to_be_shipped', null].includes(orderStatus);
      }
      return orderStatus === activeTab;
    });
  };

  // Get status badge component
  const StatusBadge = ({ status }) => {
    const config = ORDER_STATUSES[status] || ORDER_STATUSES.pending_payment;
    const Icon = config.icon;
    return (
      <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.textColor} border ${config.borderColor}`}>
        <Icon className="w-3.5 h-3.5" />
        {config.label}
      </span>
    );
  };

  // Order card component
  const OrderCard = ({ order }) => {
    const orderStatus = order.orderStatus || (order.paymentStatus === 'paid' ? 'to_be_shipped' : 'pending_payment');
    const config = ORDER_STATUSES[orderStatus] || ORDER_STATUSES.pending_payment;
    const orderRefunds = refunds.filter(r => r.orderId === order.id);
    const pendingRefund = orderRefunds.find(r => ['pending', 'seller_review'].includes(r.status));

    return (
      <div className={`luxury-card ${config.bgColor} ${config.borderColor} p-4 sm:p-5`}>
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-3 mb-4">
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2 flex-wrap">
              <h3 className="text-white font-semibold text-lg truncate">
                Order #{order.id?.slice(0, 8).toUpperCase()}
              </h3>
              <StatusBadge status={orderStatus} />
            </div>
            <p className="text-gray-400 text-sm mt-1 flex items-center gap-1.5">
              <Calendar className="w-3.5 h-3.5" />
              {new Date(order.createdAt).toLocaleDateString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })}
            </p>
          </div>
          <div className="text-right">
            <p className="text-[#D4AF37] font-bold text-xl">${order.totalAmount?.toFixed(2)}</p>
            <p className="text-gray-500 text-xs">Total Amount</p>
          </div>
        </div>

        {/* Buyer Info */}
        {order.buyer && (
          <div className="flex items-center gap-3 p-3 bg-[rgba(20,20,20,0.5)] rounded-lg mb-4">
            <div className="w-10 h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-[#D4AF37]" />
            </div>
            <div className="min-w-0">
              <p className="text-white font-medium truncate">{order.buyer.name}</p>
              <p className="text-gray-400 text-sm truncate">{order.buyer.email}</p>
            </div>
          </div>
        )}

        {/* Order Items */}
        <div className="space-y-2 mb-4">
          <p className="text-gray-400 text-sm font-medium">Items ({order.orderItems?.length || 0})</p>
          <div className="grid gap-2">
            {order.orderItems?.slice(0, 3).map((item, idx) => (
              <div key={idx} className="flex items-center gap-3 p-2 bg-[rgba(30,30,30,0.6)] rounded-lg">
                {item.product?.images?.[0] ? (
                  <img
                    src={item.product.images[0]}
                    alt={item.product?.title}
                    className="w-12 h-12 object-cover rounded-lg"
                  />
                ) : (
                  <div className="w-12 h-12 bg-[rgba(50,50,50,0.6)] rounded-lg flex items-center justify-center">
                    <ShoppingBag className="w-5 h-5 text-gray-500" />
                  </div>
                )}
                <div className="flex-1 min-w-0">
                  <p className="text-white text-sm font-medium truncate">{item.product?.title || 'Product'}</p>
                  <p className="text-gray-400 text-xs">Qty: {item.quantity} × ${item.price?.toFixed(2)}</p>
                </div>
              </div>
            ))}
            {order.orderItems?.length > 3 && (
              <p className="text-gray-500 text-xs text-center">+{order.orderItems.length - 3} more items</p>
            )}
          </div>
        </div>

        {/* Shipment Info (if exists) */}
        {order.shipment && (
          <div className="p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg mb-4">
            <div className="flex items-center gap-2 mb-2">
              <Truck className="w-4 h-4 text-purple-400" />
              <span className="text-purple-400 font-medium text-sm">Shipment Info</span>
            </div>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <p className="text-gray-400 text-xs">Tracking #</p>
                <p className="text-white font-mono">{order.shipment.trackingNumber}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Courier</p>
                <p className="text-white">{order.shipment.courierName}</p>
              </div>
              <div>
                <p className="text-gray-400 text-xs">Status</p>
                <p className="text-purple-400 capitalize">{order.shipment.deliveryStatus?.replace('_', ' ')}</p>
              </div>
              {order.shipment.shippedAt && (
                <div>
                  <p className="text-gray-400 text-xs">Shipped</p>
                  <p className="text-white">{new Date(order.shipment.shippedAt).toLocaleDateString()}</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Pending Refund Alert */}
        {pendingRefund && (
          <div className="p-3 bg-orange-500/10 border border-orange-500/30 rounded-lg mb-4">
            <div className="flex items-center gap-2 mb-2">
              <AlertTriangle className="w-4 h-4 text-orange-400" />
              <span className="text-orange-400 font-medium text-sm">Refund Request</span>
            </div>
            <p className="text-gray-300 text-sm mb-2">{pendingRefund.reason}</p>
            <p className="text-orange-300 font-medium">Requested: ${pendingRefund.requestedAmount?.toFixed(2)}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex flex-wrap gap-2 pt-3 border-t border-[rgba(212,175,55,0.1)]">
          {/* NEW: Deposit Required Alert & Instructions */}
          {order.escrowStatus === 'awaiting_seller_deposit' && order.depositRequired && (
            <div className="w-full p-4 bg-gradient-to-br from-orange-500/10 to-red-500/10 border-2 border-orange-500/30 rounded-xl mb-2">
              <div className="flex items-center gap-2 mb-3">
                <AlertTriangle className="w-6 h-6 text-orange-400" />
                <span className="text-orange-400 font-bold text-lg">Deposit Required to Unlock Order</span>
              </div>
              
              <p className="text-sm text-gray-300 mb-4">
                Send <strong className="text-[#D4AF37]">${order.depositRequired.toFixed(2)} USDT (TRC20)</strong> to the wallet below to confirm this order and qualify for payout after delivery.
              </p>
              
              {/* Wallet Address & QR Code Section */}
              <div className="bg-[#1a1a1a] rounded-lg p-4 mb-4">
                <div className="grid md:grid-cols-2 gap-4">
                  {/* QR Code */}
                  <div className="flex flex-col items-center">
                    <p className="text-gray-400 text-sm mb-2 font-semibold">Scan QR Code</p>
                    <div className="bg-white p-3 rounded-lg">
                      <img 
                        src="/assets/usdt-wallet-qr.png" 
                        alt="Deposit Wallet QR Code" 
                        className="w-40 h-40 object-contain"
                      />
                    </div>
                  </div>
                  
                  {/* Wallet Address */}
                  <div className="flex flex-col justify-center">
                    <p className="text-gray-400 text-sm mb-2 font-semibold">Platform Deposit Wallet</p>
                    <div className="bg-[rgba(30,30,30,0.8)] p-3 rounded-lg border border-[#D4AF37]/30">
                      <p className="text-[#D4AF37] font-mono text-xs break-all mb-2">
                        TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
                      </p>
                      <button
                        onClick={() => {
                          navigator.clipboard.writeText('TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU');
                          toast.success('Wallet address copied!');
                        }}
                        className="w-full bg-[#D4AF37]/20 hover:bg-[#D4AF37]/30 text-[#D4AF37] px-3 py-2 rounded text-sm font-semibold transition-colors flex items-center justify-center gap-2"
                      >
                        📋 Copy Address
                      </button>
                    </div>
                    <p className="text-yellow-400 text-xs mt-2 flex items-center gap-1">
                      <AlertTriangle className="w-3 h-3" />
                      Network: USDT (TRC20) Only
                    </p>
                  </div>
                </div>
              </div>
              
              {/* Deposit Instructions */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 mb-3">
                <p className="text-blue-300 font-semibold mb-2 text-sm">📝 Deposit Instructions:</p>
                <ol className="text-xs text-gray-300 space-y-1.5 list-decimal list-inside">
                  <li>Send exactly <strong>${order.depositRequired.toFixed(2)} USDT</strong> via <strong>TRC20 network</strong></li>
                  <li>Scan the QR code or copy the wallet address above</li>
                  <li>Complete the transfer from your USDT wallet</li>
                  <li>After sending, save your transaction hash</li>
                  <li>Admin will verify and confirm your deposit within 24 hours</li>
                  <li>Once confirmed, platform will ship the order on your behalf</li>
                </ol>
              </div>
              
              {/* Profit Breakdown */}
              <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3">
                <p className="text-green-300 font-semibold mb-2 text-sm">💰 Profit Breakdown:</p>
                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div>
                    <p className="text-gray-400">Order Total:</p>
                    <p className="text-white font-bold">${order.totalAmount.toFixed(2)}</p>
                  </div>
                  <div>
                    <p className="text-gray-400">Your Deposit:</p>
                    <p className="text-orange-400 font-bold">-${order.depositRequired.toFixed(2)}</p>
                  </div>
                  <div className="col-span-2 border-t border-green-500/30 pt-2">
                    <p className="text-gray-400">Your Net Profit (20%):</p>
                    <p className="text-green-400 font-bold text-lg">${(order.totalAmount - order.depositRequired).toFixed(2)}</p>
                  </div>
                </div>
                <p className="text-xs text-gray-400 mt-2">
                  After buyer confirms delivery, you receive the full ${order.totalAmount.toFixed(2)} and your ${order.depositRequired.toFixed(2)} deposit is deducted.
                </p>
              </div>
              
              {/* Deposit Payment Options */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {/* Option 1: Use Wallet Balance */}
                <button
                  onClick={async () => {
                    try {
                      if (!order.depositRequired) {
                        toast.error('Deposit amount not found');
                        return;
                      }
                      
                      if (!window.confirm(`Use wallet balance to deposit $${order.depositRequired.toFixed(2)}?\n\nThis will deduct from your available wallet balance.`)) {
                        return;
                      }
                      
                      setDepositingOrderId(order.id);
                      await api.post('/seller/wallet/deposit-for-order', {
                        orderId: order.id,
                        amount: order.depositRequired
                      });
                      
                      toast.success('Deposit successful! Order unlocked.');
                      fetchOrders(activeTab === 'after_sales' ? null : activeTab);
                    } catch (error) {
                      const errorMsg = error.response?.data?.detail || 'Failed to deposit';
                      toast.error(errorMsg);
                    } finally {
                      setDepositingOrderId(null);
                    }
                  }}
                  disabled={depositingOrderId === order.id}
                  className="w-full bg-gradient-to-r from-green-600 to-green-500 hover:from-green-700 hover:to-green-600 text-white font-bold py-3 px-6 rounded-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {depositingOrderId === order.id ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Processing...
                    </>
                  ) : (
                    <>
                      <Wallet className="w-5 h-5" />
                      Use Wallet Balance
                    </>
                  )}
                </button>
                
                {/* Option 2: Pay via USDT */}
                <button
                  onClick={() => {
                    setSelectedOrder(order);
                    setShowUsdtDepositModal(true);
                    setUsdtDepositForm({ transactionHash: '', notes: '' });
                  }}
                  className="w-full bg-gradient-to-r from-[#D4AF37] to-[#F4D03F] hover:from-[#F4D03F] hover:to-[#D4AF37] text-black font-bold py-3 px-6 rounded-lg transition-all transform hover:scale-105 flex items-center justify-center gap-2 shadow-lg"
                >
                  <Send className="w-5 h-5" />
                  Pay via USDT
                </button>
              </div>
            </div>
          )}
          
          {/* Platform will ship - waiting for deposit confirmation */}
          {order.escrowStatus === 'deposit_received' && (
            <div className="w-full p-3 bg-green-500/10 border border-green-500/30 rounded-lg">
              <div className="flex items-center gap-2">
                <CheckCircle className="w-5 h-5 text-green-400" />
                <span className="text-green-400 font-semibold">Deposit Confirmed - Platform Will Ship</span>
              </div>
              <p className="text-sm text-gray-300 mt-1">
                Your deposit is confirmed. The platform will handle shipping for this order.
              </p>
            </div>
          )}
          
          {/* Platform has shipped */}
          {order.escrowStatus === 'shipped' && (
            <div className="w-full p-3 bg-purple-500/10 border border-purple-500/30 rounded-lg">
              <div className="flex items-center gap-2">
                <Truck className="w-5 h-5 text-purple-400" />
                <span className="text-purple-400 font-semibold">Shipped by Platform</span>
              </div>
              <p className="text-sm text-gray-300 mt-1">
                Order shipped. Waiting for buyer to confirm delivery.
              </p>
            </div>
          )}

          {/* Mark Delivered Button */}
          {orderStatus === 'to_be_received' && order.shipment?.deliveryStatus !== 'delivered' && !order.escrowStatus && (
            <button
              onClick={() => handleMarkDelivered(order.id)}
              className="flex-1 sm:flex-none btn-gold text-sm py-2 px-4 flex items-center justify-center gap-2"
            >
              <CheckCircle className="w-4 h-4" />
              Mark Delivered
            </button>
          )}

          {/* Respond to Refund Button */}
          {pendingRefund && (
            <button
              onClick={() => {
                setSelectedOrder(order);
                setRefundResponse({
                  action: '',
                  sellerResponse: '',
                  approvedAmount: pendingRefund.requestedAmount?.toString() || ''
                });
                setShowRefundModal(true);
              }}
              className="flex-1 sm:flex-none bg-orange-500/20 hover:bg-orange-500/30 text-orange-400 text-sm py-2 px-4 rounded-lg flex items-center justify-center gap-2 transition-colors"
            >
              <MessageSquare className="w-4 h-4" />
              Respond to Refund
            </button>
          )}

          {/* View Details */}
          <button
            onClick={() => setSelectedOrder(order)}
            className="flex-1 sm:flex-none btn-gold-outline text-sm py-2 px-4 flex items-center justify-center gap-2"
          >
            <Eye className="w-4 h-4" />
            Details
          </button>
        </div>
      </div>
    );
  };

  // Tab button component
  const TabButton = ({ status, label, count }) => {
    const config = ORDER_STATUSES[status];
    const Icon = config?.icon || Package;
    const isActive = activeTab === status;
    
    return (
      <button
        onClick={() => setActiveTab(status)}
        className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${
          isActive
            ? `${config?.bgColor || 'bg-[#D4AF37]/20'} ${config?.textColor || 'text-[#D4AF37]'} border ${config?.borderColor || 'border-[#D4AF37]/50'}`
            : 'bg-[rgba(30,30,30,0.6)] text-gray-400 hover:bg-[rgba(40,40,40,0.8)] border border-transparent'
        }`}
      >
        <Icon className="w-4 h-4" />
        <span className="hidden sm:inline">{label}</span>
        <span className={`ml-1 px-2 py-0.5 rounded-full text-xs font-bold ${
          isActive ? 'bg-white/20' : 'bg-[rgba(50,50,50,0.8)]'
        }`}>
          {count || 0}
        </span>
      </button>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h2 className="font-['Playfair_Display'] text-2xl sm:text-3xl font-bold text-white">
            Order Center
          </h2>
          <p className="text-gray-400 text-sm mt-1">Manage your orders and shipments</p>
        </div>
        <button
          onClick={() => fetchOrders(activeTab === 'after_sales' ? null : activeTab)}
          className="btn-gold-outline flex items-center gap-2 self-start sm:self-auto"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {Object.entries(ORDER_STATUSES).map(([status, config]) => {
          const Icon = config.icon;
          const count = status === 'after_sales' 
            ? (refundCounts.pending || 0) + (refundCounts.seller_review || 0)
            : (counts[status] || 0);
          
          return (
            <div
              key={status}
              onClick={() => setActiveTab(status)}
              className={`p-3 sm:p-4 rounded-xl cursor-pointer transition-all ${config.bgColor} border ${config.borderColor} hover:scale-[1.02]`}
            >
              <Icon className={`w-5 h-5 ${config.textColor} mb-2`} />
              <p className="text-2xl sm:text-3xl font-bold text-white">{count}</p>
              <p className={`text-xs ${config.textColor} truncate`}>{config.label}</p>
            </div>
          );
        })}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide">
        {Object.entries(ORDER_STATUSES).map(([status, config]) => (
          <TabButton
            key={status}
            status={status}
            label={config.label}
            count={status === 'after_sales' 
              ? (refundCounts.pending || 0) + (refundCounts.seller_review || 0)
              : (counts[status] || 0)}
          />
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Search orders by ID, buyer name or email..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="luxury-input pl-12 w-full"
        />
      </div>

      {/* Orders List */}
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="spinner"></div>
        </div>
      ) : getTabOrders().length === 0 ? (
        <div className="text-center py-12">
          <Package className="w-16 h-16 mx-auto text-gray-600 mb-4" />
          <p className="text-gray-400 text-lg">No orders in this category</p>
          <p className="text-gray-500 text-sm mt-1">
            {ORDER_STATUSES[activeTab]?.description || 'Orders will appear here'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {getTabOrders().map(order => (
            <OrderCard key={order.id} order={order} />
          ))}
        </div>
      )}

      {/* Ship Order Modal */}
      {showShipModal && selectedOrder && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">
                Ship Order
              </h2>
              <button
                onClick={() => {
                  setShowShipModal(false);
                  setSelectedOrder(null);
                }}
                className="p-2 hover:bg-[rgba(255,255,255,0.1)] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <p className="text-gray-400 text-sm mb-6">
              Order #{selectedOrder.id?.slice(0, 8).toUpperCase()}
            </p>

            <div className="space-y-4">
              {/* Courier Selection */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Courier Service *
                </label>
                <div className="grid grid-cols-2 gap-2">
                  {COURIERS.map(courier => (
                    <button
                      key={courier.code}
                      type="button"
                      onClick={() => setShipmentForm({
                        ...shipmentForm,
                        courierName: courier.name,
                        courierCode: courier.code
                      })}
                      className={`p-3 rounded-lg border text-left transition-all ${
                        shipmentForm.courierCode === courier.code
                          ? 'border-[#D4AF37] bg-[#D4AF37]/10 text-white'
                          : 'border-[rgba(212,175,55,0.2)] bg-[rgba(30,30,30,0.6)] text-gray-300 hover:border-[rgba(212,175,55,0.4)]'
                      }`}
                    >
                      <span className="text-lg mr-2">{courier.icon}</span>
                      <span className="text-sm">{courier.name}</span>
                    </button>
                  ))}
                </div>
              </div>

              {/* Tracking Number */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Tracking Number *
                </label>
                <input
                  type="text"
                  value={shipmentForm.trackingNumber}
                  onChange={(e) => setShipmentForm({ ...shipmentForm, trackingNumber: e.target.value })}
                  className="luxury-input w-full font-mono"
                  placeholder="Enter tracking number"
                  required
                />
              </div>

              {/* Estimated Delivery */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Estimated Delivery (Optional)
                </label>
                <input
                  type="date"
                  value={shipmentForm.estimatedDelivery}
                  onChange={(e) => setShipmentForm({ ...shipmentForm, estimatedDelivery: e.target.value })}
                  className="luxury-input w-full"
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Delivery Notes (Optional)
                </label>
                <textarea
                  value={shipmentForm.deliveryNotes}
                  onChange={(e) => setShipmentForm({ ...shipmentForm, deliveryNotes: e.target.value })}
                  className="luxury-input w-full"
                  rows={3}
                  placeholder="Any special delivery instructions..."
                />
              </div>

              {/* Actions */}
              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => {
                    setShowShipModal(false);
                    setSelectedOrder(null);
                  }}
                  className="flex-1 btn-gold-outline"
                >
                  Cancel
                </button>
                <button
                  onClick={handleShipOrder}
                  disabled={submitting || !shipmentForm.trackingNumber || !shipmentForm.courierName}
                  className="flex-1 btn-gold disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {submitting ? (
                    <RefreshCw className="w-4 h-4 animate-spin" />
                  ) : (
                    <Send className="w-4 h-4" />
                  )}
                  {submitting ? 'Shipping...' : 'Confirm Shipment'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Refund Response Modal */}
      {showRefundModal && selectedOrder && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-md w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">
                Respond to Refund
              </h2>
              <button
                onClick={() => {
                  setShowRefundModal(false);
                  setSelectedOrder(null);
                }}
                className="p-2 hover:bg-[rgba(255,255,255,0.1)] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            {(() => {
              const pendingRefund = refunds.find(r => 
                r.orderId === selectedOrder.id && ['pending', 'seller_review'].includes(r.status)
              );
              
              if (!pendingRefund) return null;

              return (
                <div className="space-y-4">
                  {/* Refund Details */}
                  <div className="p-4 bg-orange-500/10 border border-orange-500/30 rounded-lg">
                    <p className="text-orange-400 font-medium mb-2">Refund Request</p>
                    <p className="text-white text-sm mb-2">{pendingRefund.reason}</p>
                    {pendingRefund.description && (
                      <p className="text-gray-400 text-sm mb-2">{pendingRefund.description}</p>
                    )}
                    <p className="text-orange-300 font-bold">
                      Requested Amount: ${pendingRefund.requestedAmount?.toFixed(2)}
                    </p>
                    <p className="text-gray-400 text-xs mt-2">
                      Requested: {new Date(pendingRefund.createdAt).toLocaleDateString()}
                    </p>
                  </div>

                  {/* Action Selection */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Your Decision *
                    </label>
                    <div className="grid grid-cols-2 gap-3">
                      <button
                        type="button"
                        onClick={() => setRefundResponse({ ...refundResponse, action: 'approve' })}
                        className={`p-4 rounded-lg border text-center transition-all ${
                          refundResponse.action === 'approve'
                            ? 'border-green-500 bg-green-500/20 text-green-400'
                            : 'border-[rgba(212,175,55,0.2)] bg-[rgba(30,30,30,0.6)] text-gray-300 hover:border-green-500/50'
                        }`}
                      >
                        <CheckCircle className="w-6 h-6 mx-auto mb-2" />
                        <span className="text-sm font-medium">Approve</span>
                      </button>
                      <button
                        type="button"
                        onClick={() => setRefundResponse({ ...refundResponse, action: 'reject' })}
                        className={`p-4 rounded-lg border text-center transition-all ${
                          refundResponse.action === 'reject'
                            ? 'border-red-500 bg-red-500/20 text-red-400'
                            : 'border-[rgba(212,175,55,0.2)] bg-[rgba(30,30,30,0.6)] text-gray-300 hover:border-red-500/50'
                        }`}
                      >
                        <X className="w-6 h-6 mx-auto mb-2" />
                        <span className="text-sm font-medium">Reject</span>
                      </button>
                    </div>
                  </div>

                  {/* Approved Amount (if approving) */}
                  {refundResponse.action === 'approve' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-300 mb-2">
                        Approved Amount
                      </label>
                      <input
                        type="number"
                        step="0.01"
                        value={refundResponse.approvedAmount}
                        onChange={(e) => setRefundResponse({ ...refundResponse, approvedAmount: e.target.value })}
                        className="luxury-input w-full"
                        placeholder="Enter approved amount"
                      />
                    </div>
                  )}

                  {/* Response Message */}
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Your Response (Optional)
                    </label>
                    <textarea
                      value={refundResponse.sellerResponse}
                      onChange={(e) => setRefundResponse({ ...refundResponse, sellerResponse: e.target.value })}
                      className="luxury-input w-full"
                      rows={3}
                      placeholder="Add a message to the buyer..."
                    />
                  </div>

                  {/* Actions */}
                  <div className="flex gap-3 pt-4">
                    <button
                      type="button"
                      onClick={() => {
                        setShowRefundModal(false);
                        setSelectedOrder(null);
                      }}
                      className="flex-1 btn-gold-outline"
                    >
                      Cancel
                    </button>
                    <button
                      onClick={() => handleRefundResponse(pendingRefund.id)}
                      disabled={submitting || !refundResponse.action}
                      className={`flex-1 ${
                        refundResponse.action === 'approve' 
                          ? 'bg-green-500 hover:bg-green-600 text-white' 
                          : refundResponse.action === 'reject'
                            ? 'bg-red-500 hover:bg-red-600 text-white'
                            : 'btn-gold'
                      } rounded-lg py-3 font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2`}
                    >
                      {submitting ? (
                        <RefreshCw className="w-4 h-4 animate-spin" />
                      ) : refundResponse.action === 'approve' ? (
                        <CheckCircle className="w-4 h-4" />
                      ) : (
                        <X className="w-4 h-4" />
                      )}
                      {submitting ? 'Processing...' : refundResponse.action === 'approve' ? 'Approve Refund' : 'Reject Refund'}
                    </button>
                  </div>
                </div>
              );
            })()}
          </div>
        </div>
      )}

      {/* Order Detail Modal */}
      {selectedOrder && !showShipModal && !showRefundModal && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="luxury-card max-w-2xl w-full max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">
                Order Details
              </h2>
              <button
                onClick={() => setSelectedOrder(null)}
                className="p-2 hover:bg-[rgba(255,255,255,0.1)] rounded-lg transition-colors"
              >
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>

            <div className="space-y-6">
              {/* Order Info */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p className="text-gray-400 text-sm">Order ID</p>
                  <p className="text-white font-mono">#{selectedOrder.id?.slice(0, 8).toUpperCase()}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Status</p>
                  <StatusBadge status={selectedOrder.orderStatus || 'pending_payment'} />
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Created</p>
                  <p className="text-white">{new Date(selectedOrder.createdAt).toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-gray-400 text-sm">Total Amount</p>
                  <p className="text-[#D4AF37] font-bold text-lg">${selectedOrder.totalAmount?.toFixed(2)}</p>
                </div>
              </div>

              {/* Buyer Info */}
              {selectedOrder.buyer && (
                <div className="p-4 bg-[rgba(30,30,30,0.6)] rounded-lg">
                  <p className="text-gray-400 text-sm mb-2">Buyer Information</p>
                  <p className="text-white font-medium">{selectedOrder.buyer.name}</p>
                  <p className="text-gray-400 text-sm">{selectedOrder.buyer.email}</p>
                </div>
              )}

              {/* Order Items */}
              <div>
                <p className="text-gray-400 text-sm mb-3">Order Items</p>
                <div className="space-y-3">
                  {selectedOrder.orderItems?.map((item, idx) => (
                    <div key={idx} className="flex items-center gap-4 p-3 bg-[rgba(30,30,30,0.6)] rounded-lg">
                      {item.product?.images?.[0] ? (
                        <img
                          src={item.product.images[0]}
                          alt={item.product?.title}
                          className="w-16 h-16 object-cover rounded-lg"
                        />
                      ) : (
                        <div className="w-16 h-16 bg-[rgba(50,50,50,0.6)] rounded-lg flex items-center justify-center">
                          <ShoppingBag className="w-6 h-6 text-gray-500" />
                        </div>
                      )}
                      <div className="flex-1">
                        <p className="text-white font-medium">{item.product?.title || 'Product'}</p>
                        <p className="text-gray-400 text-sm">Qty: {item.quantity}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-[#D4AF37] font-bold">${(item.price * item.quantity).toFixed(2)}</p>
                        <p className="text-gray-500 text-xs">${item.price?.toFixed(2)} each</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Shipment Info */}
              {selectedOrder.shipment && (
                <div className="p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <p className="text-purple-400 font-medium mb-3">Shipment Details</p>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div>
                      <p className="text-gray-400">Tracking Number</p>
                      <p className="text-white font-mono">{selectedOrder.shipment.trackingNumber}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Courier</p>
                      <p className="text-white">{selectedOrder.shipment.courierName}</p>
                    </div>
                    <div>
                      <p className="text-gray-400">Status</p>
                      <p className="text-purple-400 capitalize">{selectedOrder.shipment.deliveryStatus?.replace('_', ' ')}</p>
                    </div>
                    {selectedOrder.shipment.shippedAt && (
                      <div>
                        <p className="text-gray-400">Shipped At</p>
                        <p className="text-white">{new Date(selectedOrder.shipment.shippedAt).toLocaleString()}</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Close Button */}
              <div className="flex justify-end">
                <button
                  onClick={() => setSelectedOrder(null)}
                  className="btn-gold-outline"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* USDT Deposit Payment Modal */}
      {showUsdtDepositModal && selectedOrder && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center p-4 z-50 backdrop-blur-sm">
          <div className="bg-gradient-to-br from-[#1a1a1a] to-[#2d2d2d] border-2 border-[#D4AF37] rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl">
            <div className="p-6">
              {/* Header */}
              <div className="flex justify-between items-center mb-6 pb-4 border-b border-[#D4AF37]/30">
                <div>
                  <h2 className="text-2xl font-bold bg-gradient-to-r from-[#D4AF37] to-[#F4D03F] text-transparent bg-clip-text">
                    Submit USDT Payment Proof
                  </h2>
                  <p className="text-gray-400 text-sm mt-1">Order #{selectedOrder.id?.slice(0, 8)}</p>
                </div>
                <button
                  onClick={() => setShowUsdtDepositModal(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Deposit Amount */}
              <div className="bg-gradient-to-br from-orange-500/10 to-yellow-500/10 border border-orange-500/30 rounded-lg p-4 mb-6">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="text-gray-400 text-sm">Deposit Amount Required</p>
                    <p className="text-3xl font-bold text-[#D4AF37] mt-1">
                      ${selectedOrder.depositRequired?.toFixed(2)} USDT
                    </p>
                  </div>
                  <DollarSign className="w-12 h-12 text-[#D4AF37] opacity-50" />
                </div>
                <div className="mt-3 pt-3 border-t border-orange-500/20">
                  <p className="text-xs text-gray-400">Network: USDT (TRC20) Only</p>
                </div>
              </div>

              {/* Payment Instructions */}
              <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-4 mb-6">
                <p className="text-blue-300 font-semibold mb-2 flex items-center gap-2">
                  <AlertTriangle className="w-5 h-5" />
                  Payment Instructions
                </p>
                <ol className="text-sm text-gray-300 space-y-2 list-decimal list-inside">
                  <li>Transfer <strong>${selectedOrder.depositRequired?.toFixed(2)} USDT</strong> via <strong>TRC20 network</strong></li>
                  <li>Use wallet address: <code className="text-[#D4AF37] font-mono text-xs">TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU</code></li>
                  <li>After transfer, copy your transaction hash from your wallet</li>
                  <li>Paste the transaction hash in the form below</li>
                  <li>Admin will verify and confirm within 24 hours</li>
                </ol>
              </div>

              {/* Wallet Address Display */}
              <div className="bg-[#0a0a0a] border border-[#D4AF37]/30 rounded-lg p-4 mb-6">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-gray-400 text-sm font-semibold">Platform Wallet Address:</p>
                  <button
                    onClick={() => {
                      navigator.clipboard.writeText('TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU');
                      toast.success('Wallet address copied!');
                    }}
                    className="text-[#D4AF37] hover:text-[#F4D03F] text-xs flex items-center gap-1"
                  >
                    📋 Copy
                  </button>
                </div>
                <p className="font-mono text-[#D4AF37] text-xs break-all bg-black/50 p-3 rounded">
                  TY8Z91NMCjREyZVj9NjDsF8hVjyqfxFFRU
                </p>
              </div>

              {/* Form */}
              <div className="space-y-4 mb-6">
                {/* Transaction Hash */}
                <div>
                  <label className="block text-gray-300 mb-2 font-semibold">
                    Transaction Hash <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="text"
                    value={usdtDepositForm.transactionHash}
                    onChange={(e) => setUsdtDepositForm({...usdtDepositForm, transactionHash: e.target.value})}
                    placeholder="Enter transaction hash from your USDT wallet"
                    className="w-full bg-[#0a0a0a] border border-[#D4AF37]/30 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-[#D4AF37] font-mono text-sm"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Example: 0x1234567890abcdef... or abc123def456...
                  </p>
                </div>

                {/* Notes (Optional) */}
                <div>
                  <label className="block text-gray-300 mb-2 font-semibold">
                    Additional Notes <span className="text-gray-500">(Optional)</span>
                  </label>
                  <textarea
                    value={usdtDepositForm.notes}
                    onChange={(e) => setUsdtDepositForm({...usdtDepositForm, notes: e.target.value})}
                    placeholder="Any additional information (e.g., wallet used, time of transfer)"
                    rows={3}
                    className="w-full bg-[#0a0a0a] border border-[#D4AF37]/30 text-white px-4 py-3 rounded-lg focus:outline-none focus:border-[#D4AF37] resize-none"
                  />
                </div>
              </div>

              {/* Verification Link Helper */}
              {usdtDepositForm.transactionHash.trim().length > 30 && (
                <div className="bg-green-500/10 border border-green-500/30 rounded-lg p-3 mb-6">
                  <p className="text-green-300 text-sm font-semibold mb-2">✓ Verify Your Transaction:</p>
                  <a
                    href={`https://tronscan.org/#/transaction/${usdtDepositForm.transactionHash.trim()}`}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-400 hover:text-blue-300 text-xs underline break-all"
                  >
                    https://tronscan.org/#/transaction/{usdtDepositForm.transactionHash.trim()}
                  </a>
                  <p className="text-xs text-gray-400 mt-2">
                    Click to verify your transaction on TronScan blockchain explorer
                  </p>
                </div>
              )}

              {/* Action Buttons */}
              <div className="flex gap-3">
                <button
                  onClick={() => setShowUsdtDepositModal(false)}
                  className="flex-1 bg-gray-700 hover:bg-gray-600 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
                  disabled={submittingUsdtDeposit}
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitUsdtDeposit}
                  disabled={submittingUsdtDeposit || !usdtDepositForm.transactionHash.trim()}
                  className="flex-1 bg-gradient-to-r from-[#D4AF37] to-[#F4D03F] hover:from-[#F4D03F] hover:to-[#D4AF37] text-black font-bold py-3 px-6 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {submittingUsdtDeposit ? (
                    <>
                      <RefreshCw className="w-5 h-5 animate-spin" />
                      Submitting...
                    </>
                  ) : (
                    <>
                      <Send className="w-5 h-5" />
                      Submit Payment Proof
                    </>
                  )}
                </button>
              </div>

              {/* Footer Note */}
              <div className="mt-6 pt-4 border-t border-[#D4AF37]/20">
                <p className="text-xs text-gray-500 text-center">
                  After submission, our admin will verify your transaction on the blockchain and confirm your deposit within 24 hours.
                  You will receive an email notification once confirmed.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default OrderCenter;
