import React from 'react';

const SimpleLogin: React.FC = () => {
  const handleLogin = async () => {
    try {
      // Register a new admin first
      const registerResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'admin@test.com',
          password: 'admin123',
          username: 'testadmin',
          business_name: 'Test Business',
          business_reason: 'Testing the system'
        }),
        credentials: 'include'
      });

      console.log('Registration response:', registerResponse.status);

      // Then login
      const loginResponse = await fetch('https://web-production-84a3.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: 'admin@test.com',
          password: 'admin123',
          remember_me: true
        }),
        credentials: 'include'
      });

      const data = await loginResponse.json();
      console.log('Login response:', data);

      if (data.success) {
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('userType', 'admin');
        localStorage.setItem('userData', JSON.stringify(data.user));
        
        // Redirect to dashboard
        window.location.href = '/dashboard';
      } else {
        alert('Login failed: ' + data.message);
      }
    } catch (err) {
      alert('Login error: ' + err);
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
        <h1 style={{ color: '#333', marginBottom: '20px' }}>🔐 Quick Login</h1>
        <p style={{ color: '#666', marginBottom: '30px' }}>Auto-register and login as admin</p>
        
        <button 
          onClick={handleLogin}
          style={{
            width: '100%',
            padding: '12px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '5px',
            fontSize: '16px',
            cursor: 'pointer',
            fontWeight: 'bold'
          }}
        >
          Login as Admin
        </button>
        
        <p style={{ color: '#999', fontSize: '12px', marginTop: '20px' }}>
          This will register and login automatically
        </p>
      </div>
    </div>
  );
};

export default SimpleLogin;
