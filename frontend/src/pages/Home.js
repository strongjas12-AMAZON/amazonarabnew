import React from 'react';
import { Link } from 'react-router-dom';
import { Shield, Zap, Lock, TrendingUp } from 'lucide-react';

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden py-20 px-4 sm:px-6 lg:px-8">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_30%_50%,rgba(212,175,55,0.1),transparent_50%)]" />
        <div className="relative max-w-7xl mx-auto text-center">
          <h1 className="font-['Playfair_Display'] text-5xl sm:text-6xl lg:text-7xl font-bold mb-6 animate-fade-in" data-testid="hero-title">
            Welcome to{' '}
            <span className="text-gold-gradient">Amazon Arab</span>
          </h1>
          <p className="text-xl sm:text-2xl text-gray-400 mb-12 max-w-3xl mx-auto animate-fade-in">
            Premium Multi-Vendor Marketplace with Secure Crypto Payments
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in">
            <Link to="/products" className="btn-gold inline-block" data-testid="explore-products-btn">
              Explore Products
            </Link>
            <Link to="/register" className="btn-gold-outline inline-block" data-testid="become-seller-btn">
              Become a Seller
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <h2 className="font-['Playfair_Display'] text-4xl font-bold text-center mb-16 text-gold-gradient">
            Why Choose LuxMarket?
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            <div className="luxury-card text-center" data-testid="feature-crypto">
              <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
                <Lock className="w-8 h-8 text-[#0a0a0a]" />
              </div>
              <h3 className="font-['Playfair_Display'] text-xl font-semibold mb-3 text-[#D4AF37]">Crypto Payments</h3>
              <p className="text-gray-400">Secure USDT (TRC20) payments with manual admin verification for safety</p>
            </div>

            <div className="luxury-card text-center" data-testid="feature-verified">
              <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
                <Shield className="w-8 h-8 text-[#0a0a0a]" />
              </div>
              <h3 className="font-['Playfair_Display'] text-xl font-semibold mb-3 text-[#D4AF37]">Verified Sellers</h3>
              <p className="text-gray-400">All sellers undergo strict verification with invite codes and document checks</p>
            </div>

            <div className="luxury-card text-center" data-testid="feature-quality">
              <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
                <TrendingUp className="w-8 h-8 text-[#0a0a0a]" />
              </div>
              <h3 className="font-['Playfair_Display'] text-xl font-semibold mb-3 text-[#D4AF37]">Quality Products</h3>
              <p className="text-gray-400">Curated selection of premium products from trusted sellers</p>
            </div>

            <div className="luxury-card text-center" data-testid="feature-fast">
              <div className="w-16 h-16 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-full mx-auto mb-4 flex items-center justify-center">
                <Zap className="w-8 h-8 text-[#0a0a0a]" />
              </div>
              <h3 className="font-['Playfair_Display'] text-xl font-semibold mb-3 text-[#D4AF37]">Fast & Secure</h3>
              <p className="text-gray-400">Quick order processing with transparent transaction tracking</p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-[rgba(20,20,20,0.5)]">
        <div className="max-w-7xl mx-auto">
          <h2 className="font-['Playfair_Display'] text-4xl font-bold text-center mb-16 text-gold-gradient">
            How It Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
            <div className="text-center">
              <div className="w-20 h-20 bg-[#D4AF37] rounded-full mx-auto mb-6 flex items-center justify-center text-3xl font-bold text-[#0a0a0a]">
                1
              </div>
              <h3 className="font-['Playfair_Display'] text-2xl font-semibold mb-4 text-white">Browse Products</h3>
              <p className="text-gray-400">Explore our curated collection of premium products from verified sellers</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-[#D4AF37] rounded-full mx-auto mb-6 flex items-center justify-center text-3xl font-bold text-[#0a0a0a]">
                2
              </div>
              <h3 className="font-['Playfair_Display'] text-2xl font-semibold mb-4 text-white">Pay with Crypto</h3>
              <p className="text-gray-400">Checkout securely using USDT on TRC20 network to our verified wallet</p>
            </div>

            <div className="text-center">
              <div className="w-20 h-20 bg-[#D4AF37] rounded-full mx-auto mb-6 flex items-center justify-center text-3xl font-bold text-[#0a0a0a]">
                3
              </div>
              <h3 className="font-['Playfair_Display'] text-2xl font-semibold mb-4 text-white">Order Confirmed</h3>
              <p className="text-gray-400">Admin verifies payment and your order is processed for delivery</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="font-['Playfair_Display'] text-4xl sm:text-5xl font-bold mb-6 text-white">
            Ready to Start Shopping?
          </h2>
          <p className="text-xl text-gray-400 mb-8">
            Join thousands of satisfied customers enjoying luxury products with secure crypto payments
          </p>
          <Link to="/register" className="btn-gold inline-block" data-testid="get-started-btn">
            Get Started Now
          </Link>
        </div>
      </section>
    </div>
  );
};

export default Home;
