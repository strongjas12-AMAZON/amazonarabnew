import React, { useState, useEffect } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../lib/api';
import { toast } from 'sonner';
import { ShoppingBag, Clock, CheckCircle, XCircle } from 'lucide-react';

const BuyerDashboard = () => {
  const { user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOrders();
  }, []);

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
          My Orders
        </h1>
        <p className="text-gray-400">Welcome back, {user.name}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 mb-8">
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

      {/* Orders List */}
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
                {order.order_items && order.order_items.length > 0 && (
                  <div className="space-y-2 border-t border-[rgba(212,175,55,0.1)] pt-4">
                    {order.order_items.map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center">
                        <div className="flex items-center gap-3">
                          {item.products?.images?.[0] && (
                            <img
                              src={item.products.images[0]}
                              alt={item.products.title}
                              className="w-12 h-12 object-cover rounded"
                            />
                          )}
                          <div>
                            <p className="text-white text-sm">{item.products?.title || 'Product'}</p>
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
                  <p className="text-[#D4AF37] font-medium">USDT (TRC20)</p>
                  {order.paymentStatus === 'pending_payment' && (
                    <p className="text-xs text-yellow-500 mt-2">
                      ⏳ Awaiting admin payment confirmation
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default BuyerDashboard;
