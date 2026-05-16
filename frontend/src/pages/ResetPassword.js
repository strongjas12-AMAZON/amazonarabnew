import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { toast } from 'sonner';

/**
 * Reset Password page.
 *
 * Supabase generates a recovery URL of the form:
 *   https://yourapp.com/reset-password#access_token=...&refresh_token=...&type=recovery
 *
 * Since our supabase client is configured with detectSessionInUrl:false,
 * we manually parse the hash, establish a session with setSession(), and then
 * call updateUser({ password }) to change the password.
 */
const ResetPassword = () => {
  const navigate = useNavigate();
  const [sessionReady, setSessionReady] = useState(false);
  const [sessionError, setSessionError] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    const establishRecoverySession = async () => {
      try {
        const hash = window.location.hash || '';
        const search = window.location.search || '';

        // Parse both hash (#access_token=...) and query (?error=...) formats
        const hashParams = new URLSearchParams(hash.replace(/^#/, ''));
        const queryParams = new URLSearchParams(search);

        // Supabase returns errors via query string in some flows
        const errorCode = queryParams.get('error') || hashParams.get('error');
        const errorDesc = queryParams.get('error_description') || hashParams.get('error_description');
        if (errorCode) {
          setSessionError(
            errorDesc ||
              (errorCode === 'otp_expired'
                ? 'This reset link has expired. Please request a new one.'
                : 'This reset link is invalid. Please request a new one.')
          );
          return;
        }

        const accessToken = hashParams.get('access_token');
        const refreshToken = hashParams.get('refresh_token');
        const type = hashParams.get('type');

        if (!accessToken || !refreshToken) {
          setSessionError('Missing recovery tokens. Please use the link from your email.');
          return;
        }
        if (type && type !== 'recovery') {
          setSessionError('This link is not a password recovery link.');
          return;
        }

        const { error } = await supabase.auth.setSession({
          access_token: accessToken,
          refresh_token: refreshToken,
        });
        if (error) {
          setSessionError(error.message || 'Could not validate the reset link.');
          return;
        }

        // Clear the hash so tokens aren’t sitting in the URL
        window.history.replaceState(null, '', window.location.pathname);
        setSessionReady(true);
      } catch (e) {
        setSessionError(e?.message || 'Failed to process reset link.');
      }
    };
    establishRecoverySession();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (password.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    if (password !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    setSubmitting(true);
    try {
      const { error } = await supabase.auth.updateUser({ password });
      if (error) {
        toast.error(error.message || 'Failed to update password');
        setSubmitting(false);
        return;
      }
      // Sign out the recovery session so user must log in fresh
      try { await supabase.auth.signOut(); } catch (_) { /* ignore */ }
      // Clear any stale token we may have stored
      try { localStorage.removeItem('token'); } catch (_) { /* ignore */ }

      toast.success('Password updated successfully. Please sign in.');
      navigate('/login', { replace: true });
    } catch (err) {
      toast.error(err?.message || 'Something went wrong');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="font-['Playfair_Display'] text-4xl font-bold text-gold-gradient mb-2">
            Reset Password
          </h1>
          <p className="text-gray-400">Choose a new password for your account</p>
        </div>

        <div className="luxury-card">
          {sessionError ? (
            <div className="text-center py-4">
              <div className="mx-auto mb-4 w-14 h-14 rounded-full bg-red-500/15 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">Invalid or expired link</h2>
              <p className="text-gray-400 text-sm mb-6">{sessionError}</p>
              <Link to="/forgot-password" className="btn-gold inline-block w-full text-center">
                Request a new link
              </Link>
            </div>
          ) : !sessionReady ? (
            <div className="text-center py-10 text-gray-400">Validating reset link...</div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                  New Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  minLength={8}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="luxury-input"
                  placeholder="At least 8 characters"
                  data-testid="new-password-input"
                />
              </div>
              <div>
                <label htmlFor="confirm-password" className="block text-sm font-medium text-gray-300 mb-2">
                  Confirm New Password
                </label>
                <input
                  id="confirm-password"
                  type="password"
                  required
                  minLength={8}
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  className="luxury-input"
                  placeholder="Re-enter password"
                  data-testid="confirm-password-input"
                />
              </div>
              <button
                type="submit"
                disabled={submitting}
                className="btn-gold w-full"
                data-testid="reset-submit-btn"
              >
                {submitting ? 'Updating...' : 'Update Password'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;
