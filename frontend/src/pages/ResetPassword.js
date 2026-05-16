import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';

/**
 * Reset Password page.
 *
 * Supabase generates a recovery URL of the form:
 *   https://yourapp.com/reset-password#access_token=...&refresh_token=...&type=recovery
 *
 * IMPORTANT: We intentionally DO NOT use the Supabase JS SDK on this page.
 * Calling `supabase.auth.setSession()` here triggers a SIGNED_IN event that
 * the AuthContext listener handles by calling `supabase.auth.getSession()`,
 * which deadlocks against the internal lock still held by setSession().
 *
 * Instead, we read the access_token from the URL hash and call Supabase's
 * Auth REST API directly with plain fetch — no listeners, no lock, no hang.
 */
const SUPABASE_URL = process.env.REACT_APP_SUPABASE_URL;
const SUPABASE_ANON_KEY = process.env.REACT_APP_SUPABASE_ANON_KEY;

const ResetPassword = () => {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useState('');
  const [sessionReady, setSessionReady] = useState(false);
  const [sessionError, setSessionError] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    try {
      const hash = window.location.hash || '';
      const search = window.location.search || '';

      const hashParams = new URLSearchParams(hash.replace(/^#/, ''));
      const queryParams = new URLSearchParams(search);

      // Supabase returns errors via query string or hash in some flows
      const errorCode = queryParams.get('error') || hashParams.get('error');
      const errorDesc =
        queryParams.get('error_description') || hashParams.get('error_description');
      if (errorCode) {
        setSessionError(
          errorDesc ||
            (errorCode === 'otp_expired'
              ? 'This reset link has expired. Please request a new one.'
              : 'This reset link is invalid. Please request a new one.')
        );
        return;
      }

      const token = hashParams.get('access_token');
      const type = hashParams.get('type');

      if (!token) {
        setSessionError('Missing recovery token. Please use the link from your email.');
        return;
      }
      if (type && type !== 'recovery') {
        setSessionError('This link is not a password recovery link.');
        return;
      }

      // Keep the token in memory only; remove it from the URL so it doesn't sit there.
      setAccessToken(token);
      window.history.replaceState(null, '', window.location.pathname);
      setSessionReady(true);
    } catch (e) {
      setSessionError(e?.message || 'Failed to process reset link.');
    }
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
    if (!accessToken) {
      toast.error('Missing recovery token. Please open the link from your email again.');
      return;
    }

    setSubmitting(true);
    try {
      // Direct call to Supabase Auth REST API.
      // PUT /auth/v1/user with the recovery access_token in the Authorization header
      // updates the authenticated user's password without touching the JS SDK
      // (so no lock, no SIGNED_IN event, no AuthContext deadlock).
      const res = await fetch(`${SUPABASE_URL}/auth/v1/user`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          apikey: SUPABASE_ANON_KEY,
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ password }),
      });

      let data = null;
      try {
        data = await res.json();
      } catch (_) {
        // ignore parse error
      }

      if (!res.ok) {
        const msg =
          (data && (data.msg || data.message || data.error_description || data.error)) ||
          'Failed to update password. The link may have expired.';
        toast.error(msg);
        setSubmitting(false);
        return;
      }

      // Clear any stale tokens so the user is forced to log in fresh.
      try { localStorage.removeItem('sb-access-token'); } catch (_) { /* ignore */ }
      try { localStorage.removeItem('sb-refresh-token'); } catch (_) { /* ignore */ }
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
            <div className="text-center py-4" data-testid="reset-link-error">
              <div className="mx-auto mb-4 w-14 h-14 rounded-full bg-red-500/15 flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h2 className="text-xl font-semibold text-white mb-2">Invalid or expired link</h2>
              <p className="text-gray-400 text-sm mb-6">{sessionError}</p>
              <Link to="/forgot-password" className="btn-gold inline-block w-full text-center" data-testid="request-new-link-btn">
                Request a new link
              </Link>
            </div>
          ) : !sessionReady ? (
            <div className="text-center py-10 text-gray-400" data-testid="reset-validating">Validating reset link...</div>
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6" data-testid="reset-password-form">
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
