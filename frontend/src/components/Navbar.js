import React from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useCart } from '../context/CartContext';
import { ShoppingCart, User, LogOut, Package, Settings, Users } from 'lucide-react';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { cart } = useCart();
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const isActive = (path) => location.pathname === path;

  return (
    <nav className="glass sticky top-0 z-50 border-b border-[rgba(212,175,55,0.2)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center space-x-2">
            <div className="w-10 h-10 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-lg flex items-center justify-center">
              <span className="text-[#0a0a0a] font-bold text-xl">L</span>
            </div>
            <span className="text-gold-gradient text-2xl font-['Playfair_Display'] font-bold hidden sm:block">
              Amazon Arab
            </span>
          </Link>

          {/* Center Nav Links */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              to="/"
              className={`transition-colors ${isActive('/') ? 'text-[#D4AF37]' : 'text-gray-300 hover:text-[#D4AF37]'}`}
              data-testid="nav-home"
            >
              Home
            </Link>
            <Link
              to="/products"
              className={`transition-colors ${isActive('/products') ? 'text-[#D4AF37]' : 'text-gray-300 hover:text-[#D4AF37]'}`}
              data-testid="nav-products"
            >
              Products
            </Link>
            {user && (
              <Link
                to="/orders"
                className={`transition-colors ${isActive('/orders') ? 'text-[#D4AF37]' : 'text-gray-300 hover:text-[#D4AF37]'}`}
                data-testid="nav-orders"
              >
                Orders
              </Link>
            )}
          </div>

          {/* Right Side */}
          <div className="flex items-center space-x-4">
            {user ? (
              <>
                {/* Cart Icon */}
                {user.role === 'buyer' && (
                  <Link
                    to="/cart"
                    className="relative p-2 hover:bg-[rgba(212,175,55,0.1)] rounded-lg transition-all"
                    data-testid="nav-cart"
                  >
                    <ShoppingCart className="w-5 h-5 text-gray-300" />
                    {cart.length > 0 && (
                      <span className="absolute -top-1 -right-1 bg-[#D4AF37] text-[#0a0a0a] text-xs font-bold w-5 h-5 flex items-center justify-center rounded-full">
                        {cart.length}
                      </span>
                    )}
                  </Link>
                )}

                {/* Dashboard Link */}
                <Link
                  to={`/dashboard/${user.role}`}
                  className="flex items-center space-x-2 px-4 py-2 bg-[rgba(212,175,55,0.1)] hover:bg-[rgba(212,175,55,0.2)] rounded-lg transition-all"
                  data-testid="nav-dashboard"
                >
                  {user.role === 'admin' ? <Settings className="w-4 h-4" /> : 
                   user.role === 'seller' ? <Package className="w-4 h-4" /> :
                   <User className="w-4 h-4" />}
                  <span className="hidden sm:block">{user.name}</span>
                </Link>

                {/* Logout */}
                <button
                  onClick={handleLogout}
                  className="p-2 hover:bg-red-500/10 rounded-lg transition-all text-red-400 hover:text-red-300"
                  data-testid="nav-logout"
                >
                  <LogOut className="w-5 h-5" />
                </button>
              </>
            ) : (
              <>
                <Link
                  to="/login"
                  className="px-4 py-2 text-gray-300 hover:text-[#D4AF37] transition-colors"
                  data-testid="nav-login"
                >
                  Login
                </Link>
                <Link
                  to="/register"
                  className="btn-gold"
                  data-testid="nav-register"
                >
                  Sign Up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
