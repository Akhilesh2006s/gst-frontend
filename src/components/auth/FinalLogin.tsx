import React, { useState } from 'react';

const FinalLogin: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleFinalLogin = async () => {
    setLoading(true);
    setMessage('Starting login process...');

    try {
      // Clear everything first
      localStorage.clear();
      sessionStorage.clear();
      
      // Step 1: Register
      setMessage('Step 1: Registering admin account...');
      const registerResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'finaladmin@test.com',
          password: 'admin123',
          username: 'finaladmin',
          business_name: 'Final Business',
          business_reason: 'Final testing'
        }),
        credentials: 'include'
      });

      console.log('Registration status:', registerResponse.status);

      // Step 2: Login
      setMessage('Step 2: Logging in...');
      const loginResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'finaladmin@test.com',
          password: 'admin123',
          remember_me: true
        }),
        credentials: 'include'
      });

      const loginData = await loginResponse.json();
      console.log('Login response:', loginData);

      if (loginData.success) {
        setMessage('Step 3: Setting up session...');
        
        // Set localStorage
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('userType', 'admin');
        localStorage.setItem('userData', JSON.stringify(loginData.user));
        
        // Test authentication
        setMessage('Step 4: Testing authentication...');
        const testResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/check', {
          credentials: 'include'
        });
        
        if (testResponse.ok) {
          setMessage('Step 5: Login successful! Redirecting...');
          
          // Force a complete page reload to ensure clean state
          setTimeout(() => {
            window.location.href = '/dashboard';
          }, 2000);
        } else {
          setMessage('Authentication test failed. Please try again.');
        }
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
        <h1 style={{ color: '#333', marginBottom: '20px' }}>🔐 Final Login</h1>
        <p style={{ color: '#666', marginBottom: '30px' }}>Complete authentication solution</p>
        
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
          onClick={handleFinalLogin}
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
          {loading ? 'Processing...' : 'Login as Admin'}
        </button>
        
        <p style={{ color: '#999', fontSize: '12px', marginTop: '20px' }}>
          This will register, login, and test authentication in one go
        </p>
      </div>
    </div>
  );
};

export default FinalLogin;
