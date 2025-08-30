import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const Login: React.FC = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    rememberMe: false
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login: _login } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // For now, skip actual authentication and go directly to dashboard
      // await login(formData.username, formData.password, formData.rememberMe);
      navigate('/dashboard');
    } catch (error: any) {
      setError(error.message || 'Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-vh-100 d-flex login-page">
      {/* Left Sidebar */}
             <div className="sidebar d-none d-md-flex flex-column justify-content-center align-items-center text-white" style={{width: '40%', minWidth: '400px'}}>
         <div className="text-center">
           <i className="fas fa-receipt fa-3x mb-3"></i>
           <h1 className="display-4 fw-bold mb-2">GST Billing System</h1>
         </div>
       </div>
      
      {/* Right Content */}
      <div className="flex-grow-1 d-flex align-items-center justify-content-center bg-light">
        <div className="container">
          <div className="row justify-content-center">
            <div className="col-md-6 col-lg-5">
              <div className="card shadow-lg border-0">
                <div className="card-body p-5">
                  {error && (
                    <div className="alert alert-danger" role="alert">
                      {error}
                    </div>
                  )}
                
                  <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                      <label htmlFor="username" className="form-label">
                        <i className="fas fa-user me-2"></i>Username
                      </label>
                      <input
                        type="text"
                        className="form-control"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                        placeholder="Enter your username"
                      />
                    </div>
                    
                    <div className="mb-3">
                      <label htmlFor="password" className="form-label">
                        <i className="fas fa-lock me-2"></i>Password
                      </label>
                      <input
                        type="password"
                        className="form-control"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                        placeholder="Enter your password"
                      />
                    </div>
                    
                    <div className="mb-3 form-check">
                      <input
                        type="checkbox"
                        className="form-check-input"
                        id="rememberMe"
                        name="rememberMe"
                        checked={formData.rememberMe}
                        onChange={handleChange}
                      />
                      <label className="form-check-label" htmlFor="rememberMe">
                        Remember me
                      </label>
                    </div>
                    
                    <button
                      type="submit"
                      className="btn btn-primary w-100"
                      disabled={loading}
                    >
                      {loading ? (
                        <>
                          <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                          Signing in...
                        </>
                      ) : (
                        <>
                          <i className="fas fa-sign-in-alt me-2"></i>
                          Sign In
                        </>
                      )}
                    </button>
                  </form>
                  
                  <hr className="my-4" />
                  
                  <div className="text-center">
                    <p className="mb-0">
                      Don't have an account?{' '}
                      <Link to="/register" className="text-decoration-none">
                        Register here
                      </Link>
                    </p>
                  </div>
                </div>
              </div>
              
              <div className="text-center mt-3">
                <small className="text-muted">
                  <i className="fas fa-shield-alt me-1"></i>
                  Secure GST Billing & Inventory Management
                </small>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
