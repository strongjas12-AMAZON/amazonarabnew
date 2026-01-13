import React, { createContext, useContext, useState, useEffect, useRef, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import authService from '../lib/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const initRef = useRef(false);
  const fetchingRef = useRef(false);

  const fetchUserProfile = useCallback(async () => {
    // Prevent multiple simultaneous calls
    if (fetchingRef.current) {
      return null;
    }
    
    fetchingRef.current = true;
    try {
      const currentUser = await authService.getUser();
      return currentUser;
    } catch (error) {
      console.error('Error fetching user profile:', error);
      return null;
    } finally {
      fetchingRef.current = false;
    }
  }, []);

  useEffect(() => {
    // Prevent double initialization in strict mode
    if (initRef.current) return;
    initRef.current = true;

    // Check initial session
    const initAuth = async () => {
      try {
        // Check localStorage only (we use backend API auth, not Supabase directly)
        // This avoids AbortError issues during Supabase client initialization
        const hasToken = localStorage.getItem('sb-access-token');
        
        if (hasToken) {
          // Token exists, try to fetch user profile
          const currentUser = await fetchUserProfile();
          setUser(currentUser);
        } else {
          // No token, user is not authenticated
          setUser(null);
        }
      } catch (error) {
        setUser(null);
      } finally {
        setLoading(false);
      }
      
      // Note: We don't call supabase.auth.getSession() here because:
      // 1. It causes AbortError issues during initialization
      // 2. We're using backend API auth, so tokens come from backend login response
      // 3. The onAuthStateChange listener below handles Supabase auth events if needed
    };

    initAuth();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      // Only handle specific events to prevent unnecessary refreshes
      if (event === 'SIGNED_IN' && session) {
        const currentUser = await fetchUserProfile();
        setUser(currentUser);
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
      }
      // Removed TOKEN_REFRESHED handler to prevent refresh loops
      // Token refresh doesn't require user profile update
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, [fetchUserProfile]);

  const login = async (email, password) => {
    const result = await authService.login(email, password);
    setUser(result.user);
    return result;
  };

  const register = async (data) => {
    const result = await authService.register(data);
    setUser(result.user);
    return result;
  };

  const logout = async () => {
    await authService.logout();
    setUser(null);
  };

  const getUser = async () => {
    return await authService.getUser();
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout, getUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
