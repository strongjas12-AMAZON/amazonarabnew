import axios from 'axios';
import { supabase } from './supabase';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error('Missing REACT_APP_BACKEND_URL environment variable. Please check your .env file and rebuild the frontend.');
}

const API_URL = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_URL,
  timeout: 30000, // 30 seconds timeout
  // Note: withCredentials NOT set — we use JWT bearer tokens in the
  // Authorization header, not cookies. Setting withCredentials=true would
  // conflict with the backend's wildcard CORS origin ('*') and make the
  // browser reject every preflight response.
});

// ---- Token refresh state (prevents multiple parallel refreshes) ----
let refreshPromise = null;

async function refreshAccessToken() {
  // If a refresh is already in-flight, return the same promise so concurrent
  // 401s don't trigger multiple refresh requests.
  if (refreshPromise) return refreshPromise;

  const refreshToken = localStorage.getItem('sb-refresh-token');
  if (!refreshToken) {
    return Promise.reject(new Error('No refresh token available'));
  }

  refreshPromise = axios
    .post(`${API_URL}/auth/refresh`, { refresh_token: refreshToken }, { timeout: 15000 })
    .then((resp) => {
      const session = resp?.data?.session;
      if (!session?.access_token) {
        throw new Error('Refresh response missing access_token');
      }
      localStorage.setItem('sb-access-token', session.access_token);
      if (session.refresh_token) {
        localStorage.setItem('sb-refresh-token', session.refresh_token);
      }
      return session.access_token;
    })
    .finally(() => {
      // Clear the in-flight promise so the next 401 can refresh again later.
      refreshPromise = null;
    });

  return refreshPromise;
}

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  // Don't override Content-Type for FormData - let axios handle it automatically
  // Only set Content-Type for non-FormData requests
  if (!(config.data instanceof FormData)) {
    config.headers['Content-Type'] = config.headers['Content-Type'] || 'application/json';
  }

  // Get token from localStorage (we use backend API auth, not Supabase directly)
  try {
    const accessToken = localStorage.getItem('sb-access-token');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
  } catch (storageErr) {
    // Silently fail - token will be null and request will be unauthenticated
  }

  return config;
}, (error) => {
  console.error('[API] Request interceptor error:', error);
  return Promise.reject(error);
});

// Handle 401 errors with automatic token refresh + one retry.
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config || {};
    const status = error.response?.status;
    const url = originalRequest.url || '';

    // Auth-related endpoints where 401 is expected / shouldn't trigger refresh-retry
    const isAuthEndpoint =
      url.includes('/auth/login') ||
      url.includes('/auth/register') ||
      url.includes('/auth/refresh') ||
      url.includes('/auth/logout') ||
      url.includes('/me');

    if (status === 401 && !isAuthEndpoint && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const newToken = await refreshAccessToken();
        // Retry the original request with the new token.
        originalRequest.headers = originalRequest.headers || {};
        originalRequest.headers.Authorization = `Bearer ${newToken}`;
        return api(originalRequest);
      } catch (refreshErr) {
        // Refresh failed — clear session and send user to login.
        try {
          localStorage.removeItem('sb-access-token');
          localStorage.removeItem('sb-refresh-token');
        } catch (_) { /* ignore */ }
        try { await supabase.auth.signOut(); } catch (_) { /* ignore */ }
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
        return Promise.reject(refreshErr);
      }
    }

    // Fallback: legacy behavior for any 401 we couldn't refresh through.
    if (status === 401 && !isAuthEndpoint) {
      if (window.location.pathname !== '/login') {
        try { await supabase.auth.signOut(); } catch (_) { /* ignore */ }
        window.location.href = '/login';
      }
    }

    return Promise.reject(error);
  }
);

export default api;
