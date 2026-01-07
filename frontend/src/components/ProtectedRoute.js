import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ProtectedRoute = ({ children, allowedRoles }) => {
  const { user, loading } = useAuth();
  const [isReady, setIsReady] = useState(false);

  useEffect(() => {
    // Wait for auth loading to complete before making decisions
    if (!loading) {
      // Small delay to ensure auth state is fully propagated
      const timer = setTimeout(() => {
        setIsReady(true);
      }, 50);
      return () => clearTimeout(timer);
    }
  }, [loading]);

  // Show loading while auth is initializing
  if (loading || !isReady) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="spinner"></div>
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // Check if user has required role
  if (allowedRoles && allowedRoles.length > 0) {
    if (!user.role || !allowedRoles.includes(user.role)) {
      // User doesn't have required role - redirect to appropriate dashboard based on their actual role
      const roleRedirects = {
        admin: '/dashboard/admin',
        seller: '/dashboard/seller',
        buyer: '/dashboard/buyer'
      };
      const redirectPath = roleRedirects[user.role] || '/';
      return <Navigate to={redirectPath} replace />;
    }
  }

  return children;
};

export default ProtectedRoute;
