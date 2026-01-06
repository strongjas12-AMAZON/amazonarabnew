import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useCart } from '../context/CartContext';
import { Trash2, Plus, Minus, ShoppingBag } from 'lucide-react';
import { toast } from 'sonner';

const Cart = () => {
  const { cart, updateQuantity, removeFromCart, getTotal, clearCart } = useCart();
  const navigate = useNavigate();

  const handleCheckout = () => {
    if (cart.length === 0) {
      toast.error('Your cart is empty');
      return;
    }
    navigate('/checkout');
  };

  if (cart.length === 0) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="luxury-card text-center py-20">
          <ShoppingBag className="w-24 h-24 mx-auto text-gray-600 mb-6" />
          <h2 className="font-['Playfair_Display'] text-3xl font-bold text-white mb-4">Your Cart is Empty</h2>
          <p className="text-gray-400 mb-8">Add some products to get started</p>
          <button
            onClick={() => navigate('/products')}
            className="btn-gold"
            data-testid="browse-products-btn"
          >
            Browse Products
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <h1 className="font-['Playfair_Display'] text-5xl font-bold text-gold-gradient mb-8" data-testid="cart-title">
        Shopping Cart
      </h1>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Cart Items */}
        <div className="lg:col-span-2 space-y-4">
          {cart.map((item) => (
            <div key={item.id} className="luxury-card flex gap-4" data-testid="cart-item">
              <img
                src={item.images?.[0] || 'https://via.placeholder.com/100'}
                alt={item.title}
                className="w-24 h-24 object-cover rounded-lg"
                onError={(e) => {
                  e.target.src = 'https://via.placeholder.com/100';
                }}
              />
              
              <div className="flex-1">
                <h3 className="font-semibold text-white mb-1" data-testid="cart-item-title">{item.title}</h3>
                <p className="text-sm text-gray-400 mb-2">${item.price.toFixed(2)} each</p>
                
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2 bg-[rgba(30,30,30,0.6)] rounded-lg p-1">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="p-1 hover:bg-[rgba(212,175,55,0.1)] rounded transition-colors"
                      data-testid="decrease-quantity-btn"
                    >
                      <Minus className="w-4 h-4" />
                    </button>
                    <span className="w-8 text-center" data-testid="cart-item-quantity">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="p-1 hover:bg-[rgba(212,175,55,0.1)] rounded transition-colors"
                      data-testid="increase-quantity-btn"
                    >
                      <Plus className="w-4 h-4" />
                    </button>
                  </div>
                  
                  <button
                    onClick={() => {
                      removeFromCart(item.id);
                      toast.success('Item removed from cart');
                    }}
                    className="p-2 hover:bg-red-500/10 rounded-lg transition-colors text-red-400"
                    data-testid="remove-item-btn"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              
              <div className="text-right">
                <p className="font-bold text-[#D4AF37] text-lg" data-testid="cart-item-total">
                  ${(item.price * item.quantity).toFixed(2)}
                </p>
              </div>
            </div>
          ))}
        </div>

        {/* Order Summary */}
        <div className="lg:col-span-1">
          <div className="luxury-card sticky top-24">
            <h2 className="font-['Playfair_Display'] text-2xl font-bold text-white mb-6">Order Summary</h2>
            
            <div className="space-y-3 mb-6">
              <div className="flex justify-between text-gray-400">
                <span>Subtotal ({cart.length} items)</span>
                <span data-testid="cart-subtotal">${getTotal().toFixed(2)}</span>
              </div>
              <div className="flex justify-between text-gray-400">
                <span>Payment Method</span>
                <span className="text-[#D4AF37]">USDT (TRC20)</span>
              </div>
            </div>
            
            <div className="border-t border-[rgba(212,175,55,0.2)] pt-4 mb-6">
              <div className="flex justify-between items-center">
                <span className="font-bold text-white text-lg">Total</span>
                <span className="font-bold text-[#D4AF37] text-2xl" data-testid="cart-total">
                  ${getTotal().toFixed(2)}
                </span>
              </div>
            </div>
            
            <button
              onClick={handleCheckout}
              className="btn-gold w-full mb-3"
              data-testid="checkout-btn"
            >
              Proceed to Checkout
            </button>
            
            <button
              onClick={() => {
                clearCart();
                toast.success('Cart cleared');
              }}
              className="btn-gold-outline w-full"
              data-testid="clear-cart-btn"
            >
              Clear Cart
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Cart;
