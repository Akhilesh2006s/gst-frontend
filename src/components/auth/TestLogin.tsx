import React from 'react';

interface TestLoginProps {
  onLogin: (type: 'admin' | 'customer' | 'super_admin') => void;
}

const TestLogin: React.FC<TestLoginProps> = ({ onLogin }) => {
  const handleLogin = () => {
    // Simple login function
    const userData = {
      id: 1,
      name: 'Super Admin',
      email: 'admin@gstbilling.com'
    };
    
    localStorage.setItem('isAuthenticated', 'true');
    localStorage.setItem('userType', 'super_admin');
    localStorage.setItem('userData', JSON.stringify(userData));
    onLogin('super_admin'); // Update parent state
    window.location.href = '/super-admin-dashboard';
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
        <h1 style={{ color: '#333', marginBottom: '20px' }}>🔐 Login</h1>
        <p style={{ color: '#666', marginBottom: '30px' }}>Super Admin Access</p>
        
        <div style={{ marginBottom: '20px', textAlign: 'left' }}>
          <label style={{ display: 'block', marginBottom: '5px', color: '#333' }}>Email:</label>
          <input 
            type="email" 
            value="admin@gstbilling.com" 
            readOnly
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '16px'
            }}
          />
        </div>
        
        <div style={{ marginBottom: '30px', textAlign: 'left' }}>
          <label style={{ display: 'block', marginBottom: '5px', color: '#333' }}>Password:</label>
          <input 
            type="password" 
            value="admin123" 
            readOnly
            style={{
              width: '100%',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '16px'
            }}
          />
        </div>
        
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
          Login
        </button>
      </div>
    </div>
  );
};

export default TestLogin;
