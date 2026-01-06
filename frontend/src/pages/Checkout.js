import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';
import api from '../lib/api';
import { Copy, AlertTriangle, CheckCircle2 } from 'lucide-react';

const WALLET_ADDRESS = process.env.REACT_APP_ADMIN_WALLET;
const QR_IMAGE_URL = 'https://customer-assets.emergentagent.com/job_luxmarket-4/artifacts/aiqkmbx4_Screenshot%202025-12-12%20at%201.41.52%E2%80%AFPM.png';

const Checkout = () => {
  const { cart, getTotal, clearCart } = useCart();
  const [confirmed, setConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleCopyAddress = () => {
    navigator.clipboard.writeText(WALLET_ADDRESS);
    toast.success('Wallet address copied!');
  };

  const handlePlaceOrder = async () => {
    if (!confirmed) {
      toast.error('Please confirm that you have sent the payment');
      return;
    }

    setLoading(true);

    try {
      const orderItems = cart.map((item) => ({
        productId: item.id,
        quantity: item.quantity,
        price: item.price
      }));

      const response = await api.post('/orders', {
        items: orderItems,
        totalAmount: getTotal()
      });

      toast.success('Order placed successfully! Awaiting admin confirmation.');
      clearCart();
      navigate('/orders');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to place order');
    } finally {
      setLoading(false);
    }
  };

  if (cart.length === 0) {
    navigate('/cart');
    return null;
  }

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-8 text-center" data-testid="checkout-title">
        Checkout
      </h1>

      <div className="luxury-card mb-8">
        <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-4">Order Summary</h2>
        <div className="space-y-3 mb-4">
          {cart.map((item) => (
            <div key={item.id} className="flex justify-between text-gray-300">
              <span>{item.title} x {item.quantity}</span>
              <span className="text-[#D4AF37]">${(item.price * item.quantity).toFixed(2)}</span>
            </div>
          ))}
        </div>
        <div className="border-t border-[rgba(212,175,55,0.2)] pt-4">
          <div className="flex justify-between items-center">
            <span className="font-bold text-white text-xl">Total Amount</span>
            <span className="font-bold text-[#D4AF37] text-3xl" data-testid="checkout-total">
              ${getTotal().toFixed(2)}
            </span>
          </div>
        </div>
      </div>

      <div className="luxury-card mb-8">
        <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Payment Information</h2>
        
        {/* Payment Method */}
        <div className="bg-[rgba(212,175,55,0.1)] border border-[#D4AF37] rounded-lg p-4 mb-6">
          <h3 className="font-semibold text-[#D4AF37] mb-2">Payment Method</h3>
          <p className="text-white font-medium">USDT (TRC20 Network Only)</p>
        </div>

        {/* QR Code */}
        <div className="flex flex-col items-center mb-6">
          <div className="bg-white p-4 rounded-lg mb-4">
            <img 
              src={QR_IMAGE_URL} 
              alt="USDT Wallet QR Code" 
              className="w-64 h-64 object-contain"
              data-testid="wallet-qr-code"
            />
          </div>
          <p className="text-gray-400 text-sm text-center">Scan QR code to send USDT payment</p>
        </div>

        {/* Wallet Address */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-2">
            Wallet Address (TRC20)
          </label>
          <div className="flex gap-2">
            <input
              type="text"
              value={WALLET_ADDRESS}
              readOnly
              className="luxury-input flex-1 font-mono text-sm"
              data-testid="wallet-address"
            />
            <button
              onClick={handleCopyAddress}
              className="btn-gold-outline px-4"
              data-testid="copy-address-btn"
            >
              <Copy className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Warning */}
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-lg p-4 mb-6">
          <div className="flex gap-3">
            <AlertTriangle className="w-6 h-6 text-yellow-500 flex-shrink-0" />
            <div>
              <h4 className="font-semibold text-yellow-500 mb-2">Important Payment Instructions</h4>
              <ul className="text-yellow-100 text-sm space-y-1 list-disc list-inside">
                <li>Send USDT on TRC20 network ONLY</li>
                <li>Sending via ERC20/BEP20 will result in permanent loss</li>
                <li>Send exact amount: ${getTotal().toFixed(2)} USDT</li>
                <li>Admin will manually verify payment before processing order</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Confirmation Checkbox */}
        <label className="flex items-start gap-3 p-4 bg-[rgba(30,30,30,0.6)] rounded-lg cursor-pointer hover:bg-[rgba(30,30,30,0.8)] transition-all mb-6">
          <input
            type="checkbox"
            checked={confirmed}
            onChange={(e) => setConfirmed(e.target.checked)}
            className="mt-1 w-5 h-5 accent-[#D4AF37]"
            data-testid="payment-confirmation-checkbox"
          />
          <span className="text-gray-300">
            I confirm that I have sent <span className="text-[#D4AF37] font-bold">${getTotal().toFixed(2)} USDT</span> to the above wallet address on the TRC20 network
          </span>
        </label>

        {/* Place Order Button */}
        <button
          onClick={handlePlaceOrder}
          disabled={!confirmed || loading}
          className="btn-gold w-full disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="place-order-btn"
        >
          {loading ? 'Placing Order...' : 'Place Order'}
        </button>
      </div>

      <div className="luxury-card bg-green-500/10 border-green-500/30">
        <div className="flex gap-3">
          <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-green-500 mb-2">After Payment</h4>
            <p className="text-green-100 text-sm">
              Once you confirm your order, our admin team will manually verify your USDT payment and update your order status. You can track your order progress in the Orders section.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
