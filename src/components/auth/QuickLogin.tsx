import React, { useState } from 'react';

const QuickLogin: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleQuickLogin = async () => {
    setLoading(true);
    setMessage('Starting quick login...');

    try {
      // Clear everything first
      localStorage.clear();
      sessionStorage.clear();
      
             // Register and login in one go
       setMessage('Registering and logging in...');
       
       await fetch('https://web-production-84a3.up.railway.app/api/auth/register', {
         method: 'POST',
         headers: {
           'Content-Type': 'application/json',
         },
         body: JSON.stringify({
           email: 'quickadmin@test.com',
           password: 'admin123',
           username: 'quickadmin',
           business_name: 'Quick Business',
           business_reason: 'Quick testing'
         }),
         credentials: 'include'
       });

      const loginResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'quickadmin@test.com',
          password: 'admin123',
          remember_me: true
        }),
        credentials: 'include'
      });

      const loginData = await loginResponse.json();
      console.log('Login response:', loginData);

      if (loginData.success) {
        setMessage('Login successful! Setting up session...');
        
        // Set localStorage
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('userType', 'admin');
        localStorage.setItem('userData', JSON.stringify(loginData.user));
        
        // Force redirect to dashboard
        setMessage('Redirecting to dashboard...');
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1000);
      } else {
        setMessage('Login failed: ' + loginData.message);
      }
    } catch (err) {
      console.error('Login error:', err);
      setMessage('Login error: ' + err);
    } finally {
      setLoading(false);
    }
  };

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
        <h1 style={{ color: '#333', marginBottom: '20px' }}>⚡ Quick Login</h1>
        <p style={{ color: '#666', marginBottom: '30px' }}>One-click solution to fix 401 errors</p>
        
        {message && (
          <div style={{
            background: '#f0f8ff',
            border: '1px solid #b3d9ff',
            color: '#0066cc',
            padding: '15px',
            borderRadius: '5px',
            marginBottom: '20px',
            fontSize: '14px'
          }}>
            {message}
          </div>
        )}
        
        <button 
          onClick={handleQuickLogin}
          disabled={loading}
          style={{
            width: '100%',
            padding: '15px',
            background: loading ? '#ccc' : '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            fontSize: '16px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold'
          }}
        >
          {loading ? 'Processing...' : 'Quick Login as Admin'}
        </button>
        
        <p style={{ color: '#999', fontSize: '12px', marginTop: '20px' }}>
          This will fix the 401 errors and let you add products
        </p>
      </div>
    </div>
  );
};

export default QuickLogin;
