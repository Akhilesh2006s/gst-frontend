import React, { useState } from 'react';

interface SimpleLoginPageProps {
  onLogin: (type: 'admin' | 'customer') => void;
}

const SimpleLoginPage: React.FC<SimpleLoginPageProps> = ({ onLogin }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [userType, setUserType] = useState<'admin' | 'customer'>('admin');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch('https://web-production-84a3.up.railway.app/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          email,
          password,
          remember_me: true
        })
      });

      const data = await response.json();

      if (data.success) {
        localStorage.setItem('isAuthenticated', 'true');
        localStorage.setItem('userType', userType);
        localStorage.setItem('userData', JSON.stringify(data.user));
        onLogin(userType);
      } else {
        setMessage(data.message || 'Login failed');
      }
    } catch (error) {
      setMessage('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      fontFamily: 'Arial, sans-serif'
    }}>
      {/* Left Section - Login Form */}
      <div style={{
        flex: 1,
        background: 'white',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px'
      }}>
        <div style={{
          maxWidth: '400px',
          width: '100%'
        }}>
          {/* Icon */}
          <div style={{
            textAlign: 'center',
            marginBottom: '30px'
          }}>
            <div style={{
              width: '60px',
              height: '60px',
              background: 'linear-gradient(45deg, #667eea, #764ba2)',
              borderRadius: '12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 20px',
              color: 'white',
              fontSize: '24px',
              fontWeight: 'bold'
            }}>
              📄
            </div>
          </div>

          {/* Heading */}
          <h1 style={{
            color: '#333',
            fontSize: '28px',
            fontWeight: 'bold',
            textAlign: 'center',
            marginBottom: '10px'
          }}>
            Welcome Back
          </h1>
          
          <p style={{
            color: '#666',
            textAlign: 'center',
            marginBottom: '30px',
            fontSize: '16px'
          }}>
            Sign in to your account to continue
          </p>

          {/* User Type Selection */}
          <div style={{
            display: 'flex',
            marginBottom: '30px',
            background: '#f8f9fa',
            borderRadius: '8px',
            padding: '4px'
          }}>
            <button
              type="button"
              onClick={() => setUserType('admin')}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                borderRadius: '6px',
                background: userType === 'admin' ? 'white' : 'transparent',
                color: userType === 'admin' ? '#667eea' : '#666',
                cursor: 'pointer',
                fontWeight: userType === 'admin' ? 'bold' : 'normal',
                boxShadow: userType === 'admin' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              🏢 Admin
            </button>
            <button
              type="button"
              onClick={() => setUserType('customer')}
              style={{
                flex: 1,
                padding: '12px',
                border: 'none',
                borderRadius: '6px',
                background: userType === 'customer' ? 'white' : 'transparent',
                color: userType === 'customer' ? '#667eea' : '#666',
                cursor: 'pointer',
                fontWeight: userType === 'customer' ? 'bold' : 'normal',
                boxShadow: userType === 'customer' ? '0 2px 4px rgba(0,0,0,0.1)' : 'none',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px'
              }}
            >
              👤 Customer
            </button>
          </div>

          {/* Error Message */}
          {message && (
            <div style={{
              background: '#ffebee',
              border: '1px solid #f44336',
              color: '#c62828',
              padding: '15px',
              borderRadius: '8px',
              marginBottom: '20px',
              fontSize: '14px'
            }}>
              {message}
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '20px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#333',
                fontWeight: '500'
              }}>
                Email Address
              </label>
              <input
                type="email"
                placeholder="Enter your email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  fontSize: '16px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            
            <div style={{ marginBottom: '30px' }}>
              <label style={{
                display: 'block',
                marginBottom: '8px',
                color: '#333',
                fontWeight: '500'
              }}>
                Password
              </label>
              <input
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                style={{
                  width: '100%',
                  padding: '12px 16px',
                  border: '1px solid #ddd',
                  borderRadius: '8px',
                  fontSize: '16px',
                  boxSizing: 'border-box'
                }}
              />
            </div>
            
            <button
              type="submit"
              disabled={loading}
              style={{
                width: '100%',
                padding: '14px',
                background: 'linear-gradient(45deg, #667eea, #764ba2)',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '16px',
                fontWeight: 'bold',
                cursor: loading ? 'not-allowed' : 'pointer',
                opacity: loading ? 0.7 : 1
              }}
            >
              {loading ? 'Signing In...' : 'Sign In'}
            </button>
          </form>

          {/* Links */}
          <div style={{
            textAlign: 'center',
            marginTop: '20px'
          }}>
            <div style={{ marginBottom: '10px' }}>
              <a href="#" style={{
                color: '#667eea',
                textDecoration: 'none',
                fontSize: '14px'
              }}>
                Don't have an account? Sign up
              </a>
            </div>
            <div>
              <a href="#" style={{
                color: '#667eea',
                textDecoration: 'none',
                fontSize: '14px'
              }}>
                Forgot your password?
              </a>
            </div>
          </div>

          {/* Quick Login Option */}
          <div style={{
            marginTop: '30px',
            textAlign: 'center'
          }}>
            <button
              onClick={() => window.location.href = '/instant-login'}
              style={{
                width: '100%',
                padding: '12px',
                background: '#4caf50',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '14px',
                cursor: 'pointer',
                fontWeight: 'bold'
              }}
            >
              ⚡ Quick Login (Instant Access)
            </button>
          </div>
        </div>
      </div>

      {/* Right Section - Promotional */}
      <div style={{
        flex: 1,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px',
        position: 'relative',
        overflow: 'hidden'
      }}>
        {/* Background Pattern */}
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          width: '300px',
          height: '300px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '50%',
          filter: 'blur(40px)'
        }}></div>

        <div style={{
          textAlign: 'center',
          color: 'white',
          position: 'relative',
          zIndex: 1
        }}>
          {/* Icon */}
          <div style={{
            fontSize: '60px',
            marginBottom: '20px'
          }}>
            📄
          </div>

          {/* Title */}
          <h1 style={{
            fontSize: '36px',
            fontWeight: 'bold',
            marginBottom: '20px'
          }}>
            GST Billing System
          </h1>

          {/* Description */}
          <p style={{
            fontSize: '18px',
            marginBottom: '40px',
            opacity: 0.9,
            lineHeight: '1.6'
          }}>
            Streamline your business operations with our comprehensive inventory and billing management solution.
          </p>

          {/* Features */}
          <div style={{
            textAlign: 'left',
            maxWidth: '300px',
            margin: '0 auto'
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '15px'
            }}>
              <span style={{ marginRight: '12px', fontSize: '18px' }}>✅</span>
              <span>Inventory Management</span>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '15px'
            }}>
              <span style={{ marginRight: '12px', fontSize: '18px' }}>✅</span>
              <span>GST Compliant Billing</span>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              marginBottom: '15px'
            }}>
              <span style={{ marginRight: '12px', fontSize: '18px' }}>✅</span>
              <span>Customer Management</span>
            </div>
            <div style={{
              display: 'flex',
              alignItems: 'center'
            }}>
              <span style={{ marginRight: '12px', fontSize: '18px' }}>✅</span>
              <span>Real-time Reports</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SimpleLoginPage;
