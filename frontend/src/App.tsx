import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Auth from './components/auth/Auth';
import Dashboard from './components/Dashboard';
import API_BASE_URL from './config/api';

// Import existing components
import Products from './components/products/Products';
import ProductForm from './components/products/ProductForm';
import ProductDetail from './components/products/ProductDetail';
import Inventory from './components/inventory/Inventory';
import Invoices from './components/invoices/Invoices';
import InvoiceForm from './components/invoices/InvoiceForm';
import InvoiceDetail from './components/invoices/InvoiceDetail';

// Import new components
import Customers from './components/customers/Customers';
import CustomerDetail from './components/customers/CustomerDetail';
import CustomerEdit from './components/customers/CustomerEdit';
import CustomerDashboard from './components/customer/CustomerDashboard';
import Orders from './components/orders/Orders';
import Reports from './components/reports/Reports';
import Sales from './components/sales/Sales';

const App: React.FC = () => {
  // Initialize userType from localStorage immediately to prevent redirect loop
  const getInitialUserType = (): 'admin' | 'customer' | null => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    const storedUserType = localStorage.getItem('userType') as 'admin' | 'customer' | null;
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    if (isAuthenticated && storedUserType) {
      if (isDevelopment) {
        // In development, trust localStorage immediately
        return storedUserType;
      }
    }
    return null;
  };
  
  const [userType, setUserType] = useState<'admin' | 'customer' | null>(getInitialUserType());

  const handleLogin = (type: 'admin' | 'customer') => {
    setUserType(type);
    // Store user type in localStorage for persistence
    localStorage.setItem('userType', type);
  };

  const handleLogout = async () => {
    // Call logout endpoint to clear server session
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        credentials: 'include'
      });
    } catch (error) {
      console.error('Logout request failed:', error);
      // Continue with logout even if request fails
    }
    
    // Clear local state
    setUserType(null);
    localStorage.removeItem('userType');
    localStorage.removeItem('isAuthenticated');
    localStorage.removeItem('userData');
  };

  // Check for stored user type on app load - set immediately to prevent redirect loop
  useEffect(() => {
    const isAuthenticated = localStorage.getItem('isAuthenticated') === 'true';
    const storedUserType = localStorage.getItem('userType') as 'admin' | 'customer' | null;
    const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
    
    // Set userType immediately from localStorage if available (prevents redirect loop)
    if (isAuthenticated && storedUserType) {
      console.log('Setting userType from localStorage:', storedUserType);
      setUserType(storedUserType);
      
      // In development, we're done - don't verify with backend
      if (isDevelopment) {
        return;
      }
      
      // In production, verify authentication with backend (but don't clear if it fails immediately)
      if (!isDevelopment) {
        // In production, verify authentication with backend
        const checkEndpoint = storedUserType === 'admin' 
          ? `${API_BASE_URL}/auth/check`
          : `${API_BASE_URL}/customer-auth/profile`;
        
        fetch(checkEndpoint, {
          credentials: 'include',
          headers: {
            'Content-Type': 'application/json'
          }
        })
        .then(async response => {
          const data = await response.json().catch(() => ({ authenticated: false }));
          if (response.ok && data.authenticated) {
            setUserType(storedUserType);
          } else {
            // Only clear if we get a clear 401 - don't clear on network errors
            if (response.status === 401) {
              console.warn('Auth check failed with 401, clearing local storage');
              localStorage.removeItem('isAuthenticated');
              localStorage.removeItem('userType');
              localStorage.removeItem('userData');
              setUserType(null);
            } else {
              console.warn('Auth check failed but not 401, keeping userType');
            }
          }
        })
        .catch((error) => {
          console.error('Auth check error:', error);
          // Don't clear on network errors - might be temporary
          // Keep the userType set from localStorage
        });
      }
    } else {
      // Only clear stale data if we're sure user isn't logged in
      // In development, NEVER clear - might be a timing issue or CORS problem
      const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
      if (!isDevelopment) {
        // In production, clear stale data
        localStorage.removeItem('isAuthenticated');
        localStorage.removeItem('userType');
        localStorage.removeItem('userData');
        setUserType(null);
      }
      // In development, leave localStorage alone - don't clear anything
      console.log('Development mode: Not clearing localStorage even if empty');
    }
  }, []);

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route 
            path="/" 
            element={
              !userType ? (
                <Auth onLogin={handleLogin} />
              ) : (
                <Navigate to={
                  userType === 'customer' ? '/customer-dashboard' :
                  '/dashboard'
                } />
              )
            } 
          />
          <Route 
            path="/login" 
            element={
              !userType ? (
                <Auth onLogin={handleLogin} />
              ) : (
                <Navigate to={
                  userType === 'customer' ? '/customer-dashboard' :
                  '/dashboard'
                } />
              )
            } 
          />

          {/* Protected Admin Routes */}
          <Route 
            path="/dashboard" 
            element={
              (() => {
                const isDevelopment = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
                // In development, also check localStorage as fallback
                if (isDevelopment && !userType) {
                  const storedUserType = localStorage.getItem('userType');
                  if (storedUserType === 'admin') {
                    console.log('Development: Using admin from localStorage for route guard');
                    return <Dashboard onLogout={handleLogout} />;
                  }
                }
                return userType === 'admin' ? (
                  <Dashboard onLogout={handleLogout} />
                ) : (
                  <Navigate to="/login" />
                );
              })()
            } 
          />
          
          {/* Products Routes */}
          <Route 
            path="/products" 
            element={
              userType === 'admin' ? (
                <Products />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/products/new" 
            element={
              userType === 'admin' ? (
                <ProductForm />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/products/:id" 
            element={
              userType === 'admin' ? (
                <ProductDetail />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/products/:id/edit" 
            element={
              userType === 'admin' ? (
                <ProductForm />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Inventory Routes */}
          <Route 
            path="/inventory" 
            element={
              userType === 'admin' ? (
                <Inventory />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Customers Routes */}
          <Route 
            path="/customers" 
            element={
              userType === 'admin' ? (
                <Customers />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/customers/:id" 
            element={
              userType === 'admin' ? (
                <CustomerDetail />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/customers/:id/edit" 
            element={
              userType === 'admin' ? (
                <CustomerEdit />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Orders Routes */}
          <Route 
            path="/orders" 
            element={
              userType === 'admin' ? (
                <Orders />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Reports Routes */}
          <Route 
            path="/reports" 
            element={
              userType === 'admin' ? (
                <Reports />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Sales Routes */}
          <Route 
            path="/sales" 
            element={
              userType === 'admin' ? (
                <Sales />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Invoices Routes */}
          <Route 
            path="/invoices" 
            element={
              userType === 'admin' ? (
                <Invoices />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/invoices/new" 
            element={
              userType === 'admin' ? (
                <InvoiceForm />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/invoices/:id" 
            element={
              userType === 'admin' ? (
                <InvoiceDetail />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />
          <Route 
            path="/invoices/:id/edit" 
            element={
              userType === 'admin' ? (
                <InvoiceForm />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />

          {/* Customer Routes */}
          <Route 
            path="/customer-dashboard" 
            element={
              userType === 'customer' ? (
                <CustomerDashboard onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" />
              )
            } 
          />


          {/* Test route to check if styling is working */}
          <Route 
            path="/test" 
            element={
              <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8">
                  <h1 className="text-4xl font-bold text-white mb-4">🎉 Success!</h1>
                  <p className="text-gray-300 text-lg mb-6">Tailwind CSS is working perfectly!</p>
                  <div className="flex space-x-4">
                    <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-2xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                      Beautiful Button
                    </button>
                    <button className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-2xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                      Another Button
                    </button>
                  </div>
                </div>
              </div>
            } 
          />

          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
};

export default App;
