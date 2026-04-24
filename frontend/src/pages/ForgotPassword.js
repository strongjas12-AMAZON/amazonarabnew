import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import api from '../lib/api';
import { toast } from 'sonner';

const ForgotPassword = () => {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email.trim()) {
      toast.error('Please enter your email address');
      return;
    }
    setLoading(true);
    try {
      await api.post('/auth/forgot-password', {
        email: email.trim().toLowerCase(),
        redirect_url: window.location.origin,
      });
      setSubmitted(true);
    } catch (error) {
      // Backend always returns 200 for privacy. Only network errors land here.
      const detail = error?.response?.data?.detail;
      if (error?.response?.status === 429) {
        toast.error('Too many requests. Please try again later.');
      } else {
        toast.error(detail || 'Something went wrong. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="font-['Playfair_Display'] text-4xl font-bold text-gold-gradient mb-2">
            Forgot Password
          </h1>
          <p className="text-gray-400">We'll email you a secure link to reset it</p>
        </div>

        <div className="luxury-card">
          {submitted ? (
            <div className="text-center py-4">
              <div className="mx-auto mb-4 w-14 h-14 rounded-full bg-[rgba(212,175,55,0.15)] flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-[#D4AF37]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">Check your inbox</h2>
              <p className="text-gray-400 text-sm mb-6">
                If an account exists for <span className="text-[#D4AF37]">{email}</span>, we’ve sent a password reset link. The link expires in 1 hour.
              </p>
              <p className="text-gray-500 text-xs mb-6">
                Didn’t receive it? Check your spam folder, or try again in a few minutes.
              </p>
              <Link to="/login" className="btn-gold inline-block w-full text-center">
                Back to Sign In
              </Link>
            </div>
          ) : (
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
                  data-testid="forgot-email-input"
                />
              </div>
              <button
                type="submit"
                disabled={loading}
                className="btn-gold w-full"
                data-testid="forgot-submit-btn"
              >
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
              <div className="text-center">
                <Link to="/login" className="text-[#D4AF37] hover:underline text-sm">
                  ← Back to Sign In
                </Link>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;
