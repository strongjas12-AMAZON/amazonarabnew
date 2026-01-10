import axios from 'axios';
import { supabase } from './supabase';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

if (!BACKEND_URL) {
  throw new Error('Missing REACT_APP_BACKEND_URL environment variable. Please check your .env file.');
}

const API_URL = `${BACKEND_URL}/api`;

const api = axios.create({
  baseURL: API_URL,
});

// Add auth token to requests
api.interceptors.request.use(async (config) => {
  const { data: { session } } = await supabase.auth.getSession();
  if (session?.access_token) {
    config.headers.Authorization = `Bearer ${session.access_token}`;
  }
  return config;
});

// Handle 401 errors (but not for auth endpoints where 401 is expected)
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      const url = error.config?.url || '';
      // Don't redirect for auth-related endpoints that can legitimately return 401
      // /me is used during auth initialization, so don't redirect on it
      if (!url.includes('/auth/login') && 
          !url.includes('/auth/register') && 
          !url.includes('/me')) {
        // Only redirect if we're not already on the login page
        if (window.location.pathname !== '/login') {
          await supabase.auth.signOut();
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default api;
