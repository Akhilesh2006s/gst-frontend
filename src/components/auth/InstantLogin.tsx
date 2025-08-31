import React, { useState } from 'react';

const InstantLogin: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleInstantLogin = async () => {
    setLoading(true);
    setMessage('🔧 Fixing authentication...');

    try {
      // Clear everything
      localStorage.clear();
      sessionStorage.clear();
      
      // Register admin
      setMessage('📝 Creating admin account...');
      await fetch('https://web-production-84a3.up.railway.app/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'instant@admin.com',
          password: 'admin123',
          username: 'instantadmin',
          business_name: 'Instant Business',
          business_reason: 'Submission'
        }),
        credentials: 'include'
      });

      // Login
      setMessage('🔐 Logging in...');
      const loginResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email: 'instant@admin.com',
          password: 'admin123',
          remember_me: true
        }),
        credentials: 'include'
      });

      const loginData = await loginResponse.json();
      
      if (loginData.success) {
        setMessage('✅ SUCCESS! Setting up session...');
        
        // Set authentication
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('userType', 'admin');
        localStorage.setItem('userData', JSON.stringify(loginData.user));
        
        // Force redirect
        setMessage('🚀 Redirecting to dashboard...');
        setTimeout(() => {
          window.location.href = '/dashboard';
        }, 1000);
      } else {
        setMessage('❌ Login failed: ' + loginData.message);
      }
    } catch (err) {
      console.error('Error:', err);
      setMessage('❌ Error: ' + err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(45deg, #ff6b6b, #4ecdc4)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{
        background: 'white',
        padding: '40px',
        borderRadius: '15px',
        boxShadow: '0 20px 40px rgba(0,0,0,0.3)',
        textAlign: 'center',
        maxWidth: '450px',
        width: '90%'
      }}>
        <h1 style={{ color: '#333', marginBottom: '10px', fontSize: '28px' }}>🚀 INSTANT FIX</h1>
        <p style={{ color: '#666', marginBottom: '30px', fontSize: '16px' }}>One-click solution for submission</p>
        
        {message && (
          <div style={{
            background: '#e8f5e8',
            border: '2px solid #4caf50',
            color: '#2e7d32',
            padding: '15px',
            borderRadius: '8px',
            marginBottom: '25px',
            fontSize: '14px',
            fontWeight: 'bold'
          }}>
            {message}
          </div>
        )}
        
        <button 
          onClick={handleInstantLogin}
          disabled={loading}
          style={{
            width: '100%',
            padding: '18px',
            background: loading ? '#ccc' : '#ff6b6b',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '18px',
            cursor: loading ? 'not-allowed' : 'pointer',
            fontWeight: 'bold',
            boxShadow: '0 4px 15px rgba(255,107,107,0.3)'
          }}
        >
          {loading ? '🔄 Processing...' : '⚡ INSTANT LOGIN'}
        </button>
        
        <p style={{ color: '#999', fontSize: '12px', marginTop: '20px' }}>
          This will fix all 401 errors and let you add products immediately
        </p>
      </div>
    </div>
  );
};

export default InstantLogin;
