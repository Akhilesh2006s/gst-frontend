import React, { useEffect, useState } from 'react';

interface AuthCheckProps {
  children: React.ReactNode;
  onAuthFail: () => void;
}

const AuthCheck: React.FC<AuthCheckProps> = ({ children, onAuthFail }) => {
  const [isChecking, setIsChecking] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const userType = localStorage.getItem('userType');
        if (!userType) {
          onAuthFail();
          return;
        }

        // Check with backend if session is still valid
        const response = await fetch('https://web-production-84a3.up.railway.app/api/auth/check', {
          credentials: 'include'
        });

        if (response.ok) {
          const data = await response.json();
          if (data.authenticated) {
            setIsAuthenticated(true);
          } else {
            // Clear invalid auth data
            localStorage.removeItem('isAuthenticated');
            localStorage.removeItem('userType');
            localStorage.removeItem('userData');
            onAuthFail();
          }
        } else {
          // Session expired or invalid
          localStorage.removeItem('isAuthenticated');
          localStorage.removeItem('userType');
          localStorage.removeItem('userData');
          onAuthFail();
        }
      } catch (error) {
        console.error('Auth check failed:', error);
        onAuthFail();
      } finally {
        setIsChecking(false);
      }
    };

    checkAuth();
  }, [onAuthFail]);

  if (isChecking) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-500 mx-auto mb-6"></div>
          <p className="text-gray-300 text-xl">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null; // Will redirect via onAuthFail
  }

  return <>{children}</>;
};

export default AuthCheck;
