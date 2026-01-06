import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import { toast } from 'sonner';
import { ShoppingBag, Clock, CheckCircle, XCircle } from 'lucide-react';

const Orders = () => {
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
      <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-8" data-testid="orders-title">
        My Orders
      </h1>

      {orders.length === 0 ? (
        <div className="luxury-card text-center py-20">
          <ShoppingBag className="w-24 h-24 mx-auto text-gray-600 mb-6" />
          <h2 className="font-['Playfair_Display'] text-3xl font-bold text-white mb-4">No Orders Yet</h2>
          <p className="text-gray-400">Start shopping to see your orders here</p>
        </div>
      ) : (
        <div className="space-y-6">
          {orders.map((order) => (
            <div key={order.id} className="luxury-card" data-testid="order-card">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <p className="text-white font-semibold text-lg">Order #{order.id.slice(0, 8).toUpperCase()}</p>
                    {getStatusIcon(order.paymentStatus)}
                  </div>
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
                  <p className="text-[#D4AF37] font-bold text-3xl">${order.totalAmount.toFixed(2)}</p>
                  <span className={`status-badge mt-2 inline-block ${
                    order.paymentStatus === 'paid' || order.paymentStatus === 'completed' ? 'status-verified' :
                    order.paymentStatus === 'pending_payment' ? 'status-pending' :
                    'status-rejected'
                  }`}>
                    {order.paymentStatus.replace('_', ' ')}
                  </span>
                </div>
              </div>

              {order.order_items && order.order_items.length > 0 && (
                <div className="space-y-3 border-t border-[rgba(212,175,55,0.1)] pt-4">
                  {order.order_items.map((item, idx) => (
                    <div key={idx} className="flex justify-between items-center p-3 bg-[rgba(30,30,30,0.4)] rounded-lg">
                      <div className="flex items-center gap-4">
                        {item.products?.images?.[0] && (
                          <img
                            src={item.products.images[0]}
                            alt={item.products.title}
                            className="w-16 h-16 object-cover rounded-lg"
                          />
                        )}
                        <div>
                          <p className="text-white font-medium">{item.products?.title || 'Product'}</p>
                          <p className="text-gray-400 text-sm">Quantity: {item.quantity}</p>
                          <p className="text-gray-500 text-xs">${item.price.toFixed(2)} each</p>
                        </div>
                      </div>
                      <p className="text-[#D4AF37] font-semibold">${(item.price * item.quantity).toFixed(2)}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="mt-4 p-4 bg-[rgba(20,20,20,0.6)] rounded-lg">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-400">Payment Method</span>
                  <span className="text-[#D4AF37] font-medium">USDT (TRC20)</span>
                </div>
                {order.paymentStatus === 'pending_payment' && (
                  <p className="text-sm text-yellow-500 mt-2">
                    ⏳ Awaiting admin payment confirmation. This usually takes a few hours.
                  </p>
                )}
                {(order.paymentStatus === 'paid' || order.paymentStatus === 'completed') && (
                  <p className="text-sm text-green-500 mt-2">
                    ✓ Payment confirmed by admin
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Orders;
