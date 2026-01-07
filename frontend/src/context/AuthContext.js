import React, { createContext, useContext, useState, useEffect, useRef } from 'react';
import { supabase } from '../lib/supabase';
import authService from '../lib/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const initRef = useRef(false);

  useEffect(() => {
    // Prevent double initialization in strict mode
    if (initRef.current) return;
    initRef.current = true;

    // Check initial session
    const initAuth = async () => {
      try {
        // First check if there's an existing session
        const { data: { session } } = await supabase.auth.getSession();
        
        if (session?.user) {
          // Session exists, fetch full user profile
          const currentUser = await authService.getUser();
          setUser(currentUser);
        } else {
          setUser(null);
        }
      } catch (error) {
        console.error('Auth init error:', error);
        setUser(null);
      } finally {
        setLoading(false);
      }
    };

    initAuth();

    // Listen for auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (event === 'SIGNED_IN' && session) {
        try {
          const currentUser = await authService.getUser();
          setUser(currentUser);
        } catch (error) {
          console.error('Error fetching user on sign in:', error);
        }
      } else if (event === 'SIGNED_OUT') {
        setUser(null);
      } else if (event === 'TOKEN_REFRESHED' && session) {
        // Keep user state on token refresh
        if (!user) {
          try {
            const currentUser = await authService.getUser();
            setUser(currentUser);
          } catch (error) {
            console.error('Error fetching user on token refresh:', error);
          }
        }
      }
    });

    return () => {
      subscription?.unsubscribe();
    };
  }, []);

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
