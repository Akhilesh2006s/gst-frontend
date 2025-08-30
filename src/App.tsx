import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import LoginPage from './components/auth/LoginPage';
import Dashboard from './components/Dashboard';
import SuperAdminDashboard from './components/super-admin/SuperAdminDashboard';

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
import CustomerDashboard from './components/customer/CustomerDashboard';
import Orders from './components/orders/Orders';

const App: React.FC = () => {
  const [userType, setUserType] = useState<'admin' | 'customer' | 'super_admin' | null>(null);

  const handleLogin = (type: 'admin' | 'customer' | 'super_admin') => {
    setUserType(type);
  };

  const handleLogout = () => {
    setUserType(null);
  };

  return (
    <Router>
      <div className="App">
        <Routes>
          {/* Public routes */}
          <Route 
            path="/" 
            element={
              !userType ? (
                <LoginPage onLogin={handleLogin} />
              ) : (
                <Navigate to={
                  userType === 'super_admin' ? '/super-admin-dashboard' :
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
                <LoginPage onLogin={handleLogin} />
              ) : (
                <Navigate to={
                  userType === 'super_admin' ? '/super-admin-dashboard' :
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
              userType === 'admin' ? (
                <Dashboard onLogout={handleLogout} />
              ) : (
                <Navigate to="/login" />
              )
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

          {/* Super Admin Routes */}
          <Route 
            path="/super-admin-dashboard" 
            element={
              userType === 'super_admin' ? (
                <SuperAdminDashboard />
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
