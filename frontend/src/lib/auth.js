import { supabase } from './supabase';
import api from './api';

const authService = {
  async register(data) {
    try {
      // Use backend API endpoint for registration (includes rate limiting, email auto-confirmation)
      const response = await api.post('/auth/register', {
        name: data.name,
        email: data.email,
        password: data.password,
        role: data.role
      });

      if (!response.data.success) {
        throw new Error(response.data.detail || 'Registration failed');
      }

      // Set the session in Supabase client so it's available for future requests
      if (response.data.session) {
        const { error: sessionError } = await supabase.auth.setSession({
          access_token: response.data.session.access_token,
          refresh_token: response.data.session.refresh_token
        });

        if (sessionError) {
          console.warn('Failed to set session:', sessionError);
        }
      }

      return {
        success: true,
        user: response.data.user,
        session: response.data.session
      };
    } catch (error) {
      // Handle API errors
      const errorMessage = error.response?.data?.detail || error.message || 'Registration failed';
      
      // Transform error messages to user-friendly ones
      const lowerMessage = errorMessage.toLowerCase();
      if (lowerMessage.includes('already registered') || lowerMessage.includes('already exists')) {
        throw new Error('This email is already registered');
      } else if (lowerMessage.includes('password')) {
        throw new Error('Password does not meet requirements');
      } else if (lowerMessage.includes('email')) {
        throw new Error('Invalid email address');
      } else if (lowerMessage.includes('rate') || lowerMessage.includes('limit')) {
        throw new Error('Too many registration attempts. Please try again later');
      }
      
      throw new Error(errorMessage);
    }
  },

  async login(email, password) {
    try {
      // Use backend API endpoint for login (includes rate limiting: 5/minute)
      const response = await api.post('/auth/login', {
        email,
        password
      });

      if (!response.data.success) {
        throw new Error(response.data.detail || 'Login failed');
      }

      // Set the session in Supabase client so it's available for future requests
      if (response.data.session) {
        const { error: sessionError } = await supabase.auth.setSession({
          access_token: response.data.session.access_token,
          refresh_token: response.data.session.refresh_token
        });

        if (sessionError) {
          console.warn('Failed to set session:', sessionError);
        }
      }

      return {
        success: true,
        user: response.data.user,
        session: response.data.session
      };
    } catch (error) {
      // Handle API errors
      const errorMessage = error.response?.data?.detail || error.message || 'Login failed';
      
      // Transform error messages to user-friendly ones
      const lowerMessage = errorMessage.toLowerCase();
      if (lowerMessage.includes('invalid') || lowerMessage.includes('credentials') || lowerMessage.includes('password')) {
        throw new Error('Invalid email or password');
      } else if (lowerMessage.includes('email') && lowerMessage.includes('confirmed')) {
        throw new Error('Please verify your email address before logging in');
      } else if (lowerMessage.includes('rate') || lowerMessage.includes('limit')) {
        throw new Error('Too many login attempts. Please try again later');
      } else if (lowerMessage.includes('not found')) {
        throw new Error('User account not found. Please register first.');
      }
      
      throw new Error(errorMessage);
    }
  },

  async logout() {
    try {
      // Call backend logout endpoint
      try {
        await api.post('/auth/logout');
      } catch (error) {
        // Ignore logout API errors, still sign out locally
        console.warn('Backend logout failed:', error);
      }
    } finally {
      // Always sign out from Supabase client
      await supabase.auth.signOut();
    }
  },

  async getUser() {
    try {
      // Get current session from Supabase first
      const { data: { session } } = await supabase.auth.getSession();
      
      if (!session || !session.access_token) {
        return null;
      }

      // Fetch user info from backend API (which validates token and returns user data)
      try {
        const response = await api.get('/me');
        if (response.data.success && response.data.user) {
          return response.data.user;
        }
      } catch (error) {
        // If /me fails, token might be invalid, try fetching from Supabase directly as fallback
        const { data: { user } } = await supabase.auth.getUser();
        
        if (!user) {
          return null;
        }

        // Fallback: try to get profile from Supabase directly
        const { data: profile, error: profileError } = await supabase
          .from('users')
          .select('*')
          .eq('id', user.id)
          .single();

        if (profileError || !profile) {
          return null;
        }

        // Convert to expected format
        return {
          id: profile.id,
          email: profile.email,
          name: profile.name,
          role: profile.role,
          verificationStatus: profile.verificationStatus || profile.verification_status || 'unverified'
        };
      }

      return null;
    } catch (error) {
      console.error('Error fetching user:', error);
      return null;
    }
  },

  async getSession() {
    const { data: { session } } = await supabase.auth.getSession();
    return session;
  },

  isAuthenticated() {
    return supabase.auth.getSession().then(({ data: { session } }) => !!session);
  }
};

export default authService;
