import React, { useEffect } from 'react';

const ResetLogin: React.FC = () => {
  useEffect(() => {
    // Clear all authentication data immediately
    localStorage.clear();
    sessionStorage.clear();
    
    // Clear any cookies by calling logout endpoint
    fetch('https://web-production-84a3.up.railway.app/api/auth/logout', {
      method: 'POST',
      credentials: 'include'
    }).catch(() => {}); // Ignore errors
    
    // Force a complete page reload to clear everything
    window.location.href = '/direct-login';
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(45deg, #667eea 0%, #764ba2 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '10px',
        boxShadow: '0 10px 30px rgba(0,0,0,0.3)',
        textAlign: 'center',
        maxWidth: '400px',
        width: '90%'
      }}>
        <h1 style={{ color: '#333', marginBottom: '20px' }}>🔄 Resetting Session...</h1>
        <p style={{ color: '#666', marginBottom: '30px' }}>Clearing all data and redirecting to login</p>
        <div style={{
          width: '40px',
          height: '40px',
          border: '4px solid #f3f3f3',
          borderTop: '4px solid #667eea',
          borderRadius: '50%',
          animation: 'spin 1s linear infinite',
          margin: '0 auto'
        }}></div>
        <style>{`
          @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
          }
        `}</style>
      </div>
    </div>
  );
};

export default ResetLogin;
