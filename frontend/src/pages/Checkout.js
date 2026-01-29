import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { toast } from 'sonner';
import api from '../lib/api';
import { Copy, AlertTriangle, CheckCircle2, Wallet, MapPin, Plus, Trash2, Edit } from 'lucide-react';

const WALLET_ADDRESS = process.env.REACT_APP_ADMIN_WALLET;
const QR_IMAGE_URL = 'https://customer-assets.emergentagent.com/job_luxmarket-4/artifacts/aiqkmbx4_Screenshot%202025-12-12%20at%201.41.52%E2%80%AFPM.png';

const Checkout = () => {
  const { cart, getTotal, clearCart } = useCart();
  const [confirmed, setConfirmed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [paymentMethod, setPaymentMethod] = useState('crypto'); // 'crypto' or 'wallet'
  const [walletBalance, setWalletBalance] = useState(0);
  const [loadingBalance, setLoadingBalance] = useState(true);
  
  // Shipping state
  const [addresses, setAddresses] = useState([]);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [loadingAddresses, setLoadingAddresses] = useState(true);
  const [addressForm, setAddressForm] = useState({
    fullName: '',
    phone: '',
    addressLine1: '',
    addressLine2: '',
    city: '',
    state: '',
    postalCode: '',
    country: '',
    isDefault: false
  });
  
  const navigate = useNavigate();

  useEffect(() => {
    fetchWalletBalance();
    fetchAddresses();
  }, []);

  const fetchWalletBalance = async () => {
    try {
      const response = await api.get('/wallet/balance');
      setWalletBalance(response.data.balance || 0);
    } catch (error) {
      // Silently fail - user might not be a buyer or wallet might not exist
      console.error('Failed to fetch wallet balance', error);
    } finally {
      setLoadingBalance(false);
    }
  };

  const fetchAddresses = async () => {
    try {
      const response = await api.get('/buyer/addresses');
      if (response.data.success) {
        setAddresses(response.data.addresses || []);
        // Auto-select default address if exists
        const defaultAddr = response.data.addresses.find(addr => addr.isDefault);
        if (defaultAddr) {
          setSelectedAddress(defaultAddr);
        }
      }
    } catch (error) {
      console.error('Failed to fetch addresses', error);
    } finally {
      setLoadingAddresses(false);
    }
  };

  const handleSaveAddress = async () => {
    // Validate required fields
    if (!addressForm.fullName || !addressForm.phone || !addressForm.addressLine1 || 
        !addressForm.city || !addressForm.state || !addressForm.postalCode || !addressForm.country) {
      toast.error('Please fill in all required fields');
      return;
    }

    try {
      const response = await api.post('/buyer/addresses', addressForm);
      if (response.data.success) {
        toast.success('Address saved successfully');
        setAddresses([response.data.address, ...addresses]);
        setSelectedAddress(response.data.address);
        setShowAddressForm(false);
        // Reset form
        setAddressForm({
          fullName: '',
          phone: '',
          addressLine1: '',
          addressLine2: '',
          city: '',
          state: '',
          postalCode: '',
          country: '',
          isDefault: false
        });
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save address');
    }
  };

  const handleDeleteAddress = async (addressId) => {
    try {
      const response = await api.delete(`/buyer/addresses/${addressId}`);
      if (response.data.success) {
        toast.success('Address deleted');
        setAddresses(addresses.filter(addr => addr.id !== addressId));
        if (selectedAddress?.id === addressId) {
          setSelectedAddress(null);
        }
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to delete address');
    }
  };

  const handleCopyAddress = () => {
    navigator.clipboard.writeText(WALLET_ADDRESS);
    toast.success('Wallet address copied!');
  };

  const handlePlaceOrder = async () => {
    const total = getTotal();
    const useWallet = paymentMethod === 'wallet';

    // Validate shipping information
    if (!selectedAddress) {
      toast.error('Please select or add a shipping address');
      return;
    }

    if (useWallet) {
      if (walletBalance < total) {
        toast.error(`Insufficient wallet balance. Available: $${walletBalance.toFixed(2)}, Required: $${total.toFixed(2)}`);
        return;
      }
    } else {
      if (!confirmed) {
        toast.error('Please confirm that you have sent the payment');
        return;
      }
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
        totalAmount: total,
        useWallet: useWallet,
        shippingAddressId: selectedAddress.id,
        shippingName: selectedAddress.fullName,
        shippingPhone: selectedAddress.phone,
        shippingAddress: {
          fullName: selectedAddress.fullName,
          phone: selectedAddress.phone,
          addressLine1: selectedAddress.addressLine1,
          addressLine2: selectedAddress.addressLine2,
          city: selectedAddress.city,
          state: selectedAddress.state,
          postalCode: selectedAddress.postalCode,
          country: selectedAddress.country
        }
      });

      toast.success(useWallet ? 'Order placed successfully using wallet balance!' : 'Order placed successfully! Awaiting admin confirmation.');
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

  const canPlaceOrder = selectedAddress && (paymentMethod === 'wallet' ? walletBalance >= getTotal() : confirmed);

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

      {/* SHIPPING INFORMATION SECTION */}
      <div className="luxury-card mb-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-2">
            <MapPin className="w-6 h-6 text-[#D4AF37]" />
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white">Shipping Information</h2>
          </div>
          {!showAddressForm && (
            <button
              onClick={() => setShowAddressForm(true)}
              className="btn-gold-outline flex items-center gap-2 text-sm px-4 py-2"
            >
              <Plus className="w-4 h-4" />
              Add New Address
            </button>
          )}
        </div>

        {loadingAddresses ? (
          <div className="text-center py-8">
            <p className="text-gray-400">Loading addresses...</p>
          </div>
        ) : showAddressForm ? (
          <div className="bg-[rgba(30,30,30,0.6)] rounded-lg p-6">
            <h3 className="text-lg font-semibold text-white mb-4">Add New Shipping Address</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Full Name *</label>
                <input
                  type="text"
                  value={addressForm.fullName}
                  onChange={(e) => setAddressForm({...addressForm, fullName: e.target.value})}
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Phone Number *</label>
                <input
                  type="tel"
                  value={addressForm.phone}
                  onChange={(e) => setAddressForm({...addressForm, phone: e.target.value})}
                  placeholder="+1XXXXXXXXXX"
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">Address Line 1 *</label>
                <input
                  type="text"
                  value={addressForm.addressLine1}
                  onChange={(e) => setAddressForm({...addressForm, addressLine1: e.target.value})}
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div className="md:col-span-2">
                <label className="block text-sm font-medium text-gray-300 mb-2">Address Line 2 (Optional)</label>
                <input
                  type="text"
                  value={addressForm.addressLine2}
                  onChange={(e) => setAddressForm({...addressForm, addressLine2: e.target.value})}
                  className="luxury-input w-full"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">City *</label>
                <input
                  type="text"
                  value={addressForm.city}
                  onChange={(e) => setAddressForm({...addressForm, city: e.target.value})}
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">State / Province *</label>
                <input
                  type="text"
                  value={addressForm.state}
                  onChange={(e) => setAddressForm({...addressForm, state: e.target.value})}
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Postal Code *</label>
                <input
                  type="text"
                  value={addressForm.postalCode}
                  onChange={(e) => setAddressForm({...addressForm, postalCode: e.target.value})}
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">Country *</label>
                <input
                  type="text"
                  value={addressForm.country}
                  onChange={(e) => setAddressForm({...addressForm, country: e.target.value})}
                  className="luxury-input w-full"
                  required
                />
              </div>
              <div className="md:col-span-2">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={addressForm.isDefault}
                    onChange={(e) => setAddressForm({...addressForm, isDefault: e.target.checked})}
                    className="w-4 h-4 accent-[#D4AF37]"
                  />
                  <span className="text-sm text-gray-300">Set as default address</span>
                </label>
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <button
                onClick={handleSaveAddress}
                className="btn-gold flex-1"
              >
                Save Address
              </button>
              <button
                onClick={() => setShowAddressForm(false)}
                className="btn-gold-outline flex-1"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : addresses.length === 0 ? (
          <div className="text-center py-8 bg-[rgba(30,30,30,0.6)] rounded-lg">
            <MapPin size={48} className="mx-auto text-gray-600 mb-3" />
            <p className="text-gray-400 mb-4">No saved addresses yet</p>
            <button
              onClick={() => setShowAddressForm(true)}
              className="btn-gold inline-flex items-center gap-2"
            >
              <Plus className="w-4 h-4" />
              Add Your First Address
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {addresses.map((addr) => (
              <div
                key={addr.id}
                onClick={() => setSelectedAddress(addr)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                  selectedAddress?.id === addr.id
                    ? 'border-[#D4AF37] bg-[rgba(212,175,55,0.1)]'
                    : 'border-gray-600 bg-[rgba(30,30,30,0.6)] hover:border-gray-500'
                }`}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <p className="font-semibold text-white">{addr.fullName}</p>
                      {addr.isDefault && (
                        <span className="px-2 py-0.5 bg-[#D4AF37] text-black text-xs font-semibold rounded">
                          Default
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-300">{addr.phone}</p>
                    <p className="text-sm text-gray-400 mt-1">
                      {addr.addressLine1}
                      {addr.addressLine2 && `, ${addr.addressLine2}`}
                    </p>
                    <p className="text-sm text-gray-400">
                      {addr.city}, {addr.state} {addr.postalCode}
                    </p>
                    <p className="text-sm text-gray-400">{addr.country}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteAddress(addr.id);
                    }}
                    className="p-2 text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {!selectedAddress && !showAddressForm && addresses.length > 0 && (
          <div className="mt-4 p-3 bg-red-500/10 border border-red-500/30 rounded-lg">
            <p className="text-red-400 text-sm">⚠️ Please select a shipping address to continue</p>
          </div>
        )}
      </div>

      <div className="luxury-card mb-8">
        <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Payment Information</h2>
        
        {/* Payment Method Selection */}
        <div className="mb-6">
          <label className="block text-sm font-medium text-gray-300 mb-3">Select Payment Method</label>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <button
              type="button"
              onClick={() => setPaymentMethod('crypto')}
              className={`p-4 rounded-lg border-2 transition-all ${
                paymentMethod === 'crypto'
                  ? 'border-[#D4AF37] bg-[rgba(212,175,55,0.1)]'
                  : 'border-gray-600 bg-[rgba(30,30,30,0.6)] hover:border-gray-500'
              }`}
            >
              <div className="text-left">
                <p className="font-semibold text-white mb-1">USDT (TRC20)</p>
                <p className="text-xs text-gray-400">Pay with cryptocurrency</p>
              </div>
            </button>
            <button
              type="button"
              onClick={() => setPaymentMethod('wallet')}
              disabled={loadingBalance || walletBalance < getTotal()}
              className={`p-4 rounded-lg border-2 transition-all ${
                paymentMethod === 'wallet'
                  ? 'border-[#D4AF37] bg-[rgba(212,175,55,0.1)]'
                  : 'border-gray-600 bg-[rgba(30,30,30,0.6)] hover:border-gray-500'
              } ${(loadingBalance || walletBalance < getTotal()) ? 'opacity-50 cursor-not-allowed' : ''}`}
            >
              <div className="text-left">
                <div className="flex items-center gap-2 mb-1">
                  <Wallet className="w-4 h-4 text-[#D4AF37]" />
                  <p className="font-semibold text-white">Wallet Balance</p>
                </div>
                {loadingBalance ? (
                  <p className="text-xs text-gray-400">Loading...</p>
                ) : (
                  <p className="text-xs text-gray-400">
                    Available: ${walletBalance.toFixed(2)}
                    {walletBalance < getTotal() && (
                      <span className="text-red-400 ml-1">(Insufficient)</span>
                    )}
                  </p>
                )}
              </div>
            </button>
          </div>
        </div>

        {/* Payment Method Info */}
        {paymentMethod === 'crypto' && (
          <div className="bg-[rgba(212,175,55,0.1)] border border-[#D4AF37] rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-[#D4AF37] mb-2">Payment Method</h3>
            <p className="text-white font-medium">USDT (TRC20 Network Only)</p>
          </div>
        )}

        {paymentMethod === 'wallet' && (
          <div className="bg-[rgba(212,175,55,0.1)] border border-[#D4AF37] rounded-lg p-4 mb-6">
            <h3 className="font-semibold text-[#D4AF37] mb-2">Payment Method</h3>
            <p className="text-white font-medium">Wallet Balance</p>
            <p className="text-sm text-gray-400 mt-1">
              Your balance: <span className="text-[#D4AF37] font-semibold">${walletBalance.toFixed(2)}</span>
            </p>
            {walletBalance < getTotal() && (
              <p className="text-sm text-red-400 mt-2">
                ⚠️ Insufficient balance. Please recharge your wallet or use USDT payment.
              </p>
            )}
          </div>
        )}

        {/* Crypto Payment Details - Only show if crypto method selected */}
        {paymentMethod === 'crypto' && (
          <>
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
          </>
        )}

        {/* Place Order Button */}
        <button
          onClick={handlePlaceOrder}
          disabled={loading || !canPlaceOrder}
          className="btn-gold w-full disabled:opacity-50 disabled:cursor-not-allowed"
          data-testid="place-order-btn"
        >
          {loading ? 'Placing Order...' : paymentMethod === 'wallet' ? 'Place Order with Wallet' : 'Place Order'}
        </button>
        
        {!selectedAddress && (
          <p className="text-red-400 text-sm text-center mt-3">
            ⚠️ Please complete shipping information above to place order
          </p>
        )}
      </div>

      <div className="luxury-card bg-green-500/10 border-green-500/30">
        <div className="flex gap-3">
          <CheckCircle2 className="w-6 h-6 text-green-500 flex-shrink-0" />
          <div>
            <h4 className="font-semibold text-green-500 mb-2">After Payment</h4>
            <p className="text-green-100 text-sm">
              {paymentMethod === 'wallet' 
                ? 'Your order will be placed immediately using your wallet balance. You can track your order progress in the Orders section.'
                : 'Once you confirm your order, our admin team will manually verify your USDT payment and update your order status. You can track your order progress in the Orders section.'}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;
