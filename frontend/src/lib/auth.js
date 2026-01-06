import { supabase } from './supabase';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

export const authService = {
  async register(data) {
    const response = await axios.post(`${API_URL}/auth/register`, data);
    if (response.data.success && response.data.session) {
      localStorage.setItem('accessToken', response.data.session.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async login(email, password) {
    const response = await axios.post(`${API_URL}/auth/login`, { email, password });
    if (response.data.success && response.data.session) {
      localStorage.setItem('accessToken', response.data.session.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  },

  async logout() {
    const token = localStorage.getItem('accessToken');
    if (token) {
      try {
        await axios.post(`${API_URL}/auth/logout`, {}, {
          headers: { Authorization: `Bearer ${token}` }
        });
      } catch (e) {
        // Continue logout even if API fails
      }
    }
    localStorage.removeItem('accessToken');
    localStorage.removeItem('user');
    await supabase.auth.signOut();
  },

  getUser() {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  },

  getToken() {
    return localStorage.getItem('accessToken');
  },

  isAuthenticated() {
    return !!this.getToken();
  }
};
