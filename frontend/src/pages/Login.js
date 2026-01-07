import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await login(email, password);
      
      // Validate role exists
      if (!result.user || !result.user.role) {
        toast.error('User role not found. Please contact support.');
        setLoading(false);
        return;
      }

      toast.success('Login successful!');
      
      // Redirect based on role
      const role = result.user.role;
      if (role === 'admin') {
        navigate('/dashboard/admin');
      } else if (role === 'seller') {
        navigate('/dashboard/seller');
      } else if (role === 'buyer') {
        navigate('/dashboard/buyer');
      } else {
        // Fallback for unknown role
        navigate('/products');
      }
    } catch (error) {
      toast.error(error.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="font-['Playfair_Display'] text-4xl font-bold text-gold-gradient mb-2" data-testid="login-title">
            Welcome Back
          </h1>
          <p className="text-gray-400">Sign in to your account</p>
        </div>

        <div className="luxury-card">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
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
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="luxury-input"
                placeholder="••••••••"
                data-testid="password-input"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="btn-gold w-full"
              data-testid="login-submit-btn"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <p className="text-gray-400">
              Don't have an account?{' '}
              <Link to="/register" className="text-[#D4AF37] hover:underline" data-testid="register-link">
                Sign up
              </Link>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
