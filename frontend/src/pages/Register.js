import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const Register = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'buyer'
  });
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (formData.password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      await register({
        name: formData.name,
        email: formData.email,
        password: formData.password,
        role: formData.role
      });

      toast.success('Registration successful! Please verify your account.');
      
      if (formData.role === 'seller') {
        navigate('/dashboard/seller');
      } else {
        navigate('/products');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="font-['Playfair_Display'] text-4xl font-bold text-gold-gradient mb-2" data-testid="register-title">
            Join LuxMarket
          </h1>
          <p className="text-gray-400">Create your account today</p>
        </div>

        <div className="luxury-card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                Full Name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                required
                value={formData.name}
                onChange={handleChange}
                className="luxury-input"
                placeholder="John Doe"
                data-testid="name-input"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                id="email"
                name="email"
                type="email"
                required
                value={formData.email}
                onChange={handleChange}
                className="luxury-input"
                placeholder="you@example.com"
                data-testid="email-input"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                required
                value={formData.password}
                onChange={handleChange}
                className="luxury-input"
                placeholder="••••••••"
                data-testid="password-input"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-300 mb-2">
                Confirm Password
              </label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                value={formData.confirmPassword}
                onChange={handleChange}
                className="luxury-input"
                placeholder="••••••••"
                data-testid="confirm-password-input"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Account Type
              </label>
              <div className="grid grid-cols-2 gap-4">
                <label
                  className={`flex items-center justify-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    formData.role === 'buyer'
                      ? 'border-[#D4AF37] bg-[rgba(212,175,55,0.1)]'
                      : 'border-[rgba(212,175,55,0.2)] hover:border-[rgba(212,175,55,0.4)]'
                  }`}
                  data-testid="buyer-role-option"
                >
                  <input
                    type="radio"
                    name="role"
                    value="buyer"
                    checked={formData.role === 'buyer'}
                    onChange={handleChange}
                    className="hidden"
                  />
                  <span className="font-semibold">Buyer</span>
                </label>

                <label
                  className={`flex items-center justify-center p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    formData.role === 'seller'
                      ? 'border-[#D4AF37] bg-[rgba(212,175,55,0.1)]'
                      : 'border-[rgba(212,175,55,0.2)] hover:border-[rgba(212,175,55,0.4)]'
                  }`}
                  data-testid="seller-role-option"
                >
                  <input
                    type="radio"
                    name="role"
                    value="seller"
                    checked={formData.role === 'seller'}
                    onChange={handleChange}
                    className="hidden"
                  />
                  <span className="font-semibold">Seller</span>
                </label>
              </div>
              {formData.role === 'seller' && (
                <p className="text-xs text-yellow-500 mt-2">
                  Note: Sellers require verification with invite code and documents
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-gold w-full"
              data-testid="register-submit-btn"
            >
              {loading ? 'Creating Account...' : 'Create Account'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Already have an account?{' '}
              <Link to="/login" className="text-[#D4AF37] hover:underline" data-testid="login-link">
                Sign in
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Register;
