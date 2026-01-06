import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Mail } from 'lucide-react';

const Footer = () => {
  return (
    <footer className="glass border-t border-[rgba(212,175,55,0.2)] mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-[#D4AF37] to-[#F4E4B0] rounded-lg flex items-center justify-center">
                <span className="text-[#0a0a0a] font-bold text-xl">A</span>
              </div>
              <span className="text-gold-gradient text-2xl font-['Playfair_Display'] font-bold">
                Amazon Arab
              </span>
            </div>
            <p className="text-gray-400 max-w-md">
              Premium multi-vendor marketplace for luxury products. Secure crypto payments, verified sellers, and exceptional quality.
            </p>
            <div className="flex space-x-4 mt-6">
              <a href="#" className="p-2 hover:bg-[rgba(212,175,55,0.1)] rounded-lg transition-all">
                <Facebook className="w-5 h-5 text-gray-400 hover:text-[#D4AF37]" />
              </a>
              <a href="#" className="p-2 hover:bg-[rgba(212,175,55,0.1)] rounded-lg transition-all">
                <Twitter className="w-5 h-5 text-gray-400 hover:text-[#D4AF37]" />
              </a>
              <a href="#" className="p-2 hover:bg-[rgba(212,175,55,0.1)] rounded-lg transition-all">
                <Instagram className="w-5 h-5 text-gray-400 hover:text-[#D4AF37]" />
              </a>
              <a href="mailto:support@arabshopping.org" className="p-2 hover:bg-[rgba(212,175,55,0.1)] rounded-lg transition-all">
                <Mail className="w-5 h-5 text-gray-400 hover:text-[#D4AF37]" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-['Playfair_Display'] text-[#D4AF37] text-lg font-semibold mb-4">Quick Links</h3>
            <ul className="space-y-2">
              <li><Link to="/" className="text-gray-400 hover:text-[#D4AF37] transition-colors">Home</Link></li>
              <li><Link to="/products" className="text-gray-400 hover:text-[#D4AF37] transition-colors">Products</Link></li>
              <li><Link to="/register" className="text-gray-400 hover:text-[#D4AF37] transition-colors">Become a Seller</Link></li>
            </ul>
          </div>

          {/* Support */}
          <div>
            <h3 className="font-['Playfair_Display'] text-[#D4AF37] text-lg font-semibold mb-4">Support</h3>
            <ul className="space-y-2">
              <li><a href="mailto:support@arabshopping.org" className="text-gray-400 hover:text-[#D4AF37] transition-colors">Contact Us</a></li>
              <li><span className="text-gray-400">Payment: USDT (TRC20)</span></li>
              <li><span className="text-gray-400">Manual Verification</span></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-[rgba(212,175,55,0.1)] mt-8 pt-8 text-center">
          <p className="text-gray-500 text-sm">
            © 2025 Amazon Arab. All rights reserved. | Secure crypto payments | Verified sellers
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
