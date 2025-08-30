import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface Product {
  id: number;
  name: string;
  description: string;
  cost: number;
  image_url: string;
  stock_quantity: number;
}

interface Invoice {
  id: number;
  invoice_number: string;
  customer_name: string;
  total_amount: number;
  created_at: string;
}

interface DashboardProps {
  onLogout: () => void;
}

const Dashboard: React.FC<DashboardProps> = ({ onLogout }) => {
  const navigate = useNavigate();
  const [products, setProducts] = useState<Product[]>([]);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'overview' | 'products' | 'invoices' | 'inventory'>('overview');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch products
      const productsResponse = await fetch('/api/products/', {
        credentials: 'include'
      });
      if (productsResponse.ok) {
        const productsData = await productsResponse.json();
        setProducts(productsData.products || []);
      }

      // Fetch invoices
      const invoicesResponse = await fetch('/api/invoices', {
        credentials: 'include'
      });
      if (invoicesResponse.ok) {
        const invoicesData = await invoicesResponse.json();
        setInvoices(invoicesData.invoices || []);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = () => {
    // Call the parent's logout function
    onLogout();
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-500 mx-auto mb-6"></div>
          <p className="text-gray-300 text-xl">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="backdrop-blur-xl bg-white/10 border-b border-white/20 shadow-2xl">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <div className="h-16 w-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div className="ml-6">
                <h1 className="text-4xl font-bold text-white">Admin Dashboard</h1>
                <p className="text-gray-300 text-lg">Manage your business operations</p>
              </div>
            </div>
            <button
              onClick={handleLogout}
              className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-2xl text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500 transition-all duration-300 transform hover:scale-105 shadow-lg"
            >
              <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              Logout
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Navigation Tabs */}
        <div className="mb-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {[
              { key: 'overview', label: 'Overview', icon: '📊', path: '/dashboard' },
              { key: 'products', label: 'Products', icon: '📦', path: '/products' },
              { key: 'customers', label: 'Customers', icon: '👥', path: '/customers' },
              { key: 'orders', label: 'Orders', icon: '📋', path: '/orders' },
              { key: 'invoices', label: 'Invoices', icon: '🧾', path: '/invoices' },
              { key: 'inventory', label: 'Inventory', icon: '📋', path: '/inventory' }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => {
                  if (tab.key === 'overview') {
                    setActiveTab(tab.key as any);
                  } else {
                    navigate(tab.path);
                  }
                }}
                className={`py-4 px-6 border-b-2 font-semibold text-lg rounded-t-2xl transition-all duration-300 flex items-center space-x-2 ${
                  activeTab === tab.key
                    ? 'border-blue-500 text-blue-400 bg-blue-500/10'
                    : 'border-transparent text-gray-400 hover:text-white hover:border-gray-300'
                }`}
              >
                <span className="text-xl">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="mt-8">
          {activeTab === 'overview' && (
            <div className="space-y-8">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-16 w-16 bg-gradient-to-r from-blue-400 to-cyan-500 rounded-2xl flex items-center justify-center shadow-lg">
                        <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4 flex-1">
                      <p className="text-sm font-medium text-gray-300">Total Products</p>
                      <p className="text-3xl font-bold text-white">{products.length}</p>
                    </div>
                  </div>
                </div>

                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-16 w-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center shadow-lg">
                        <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4 flex-1">
                      <p className="text-sm font-medium text-gray-300">Total Invoices</p>
                      <p className="text-3xl font-bold text-white">{invoices.length}</p>
                    </div>
                  </div>
                </div>

                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-16 w-16 bg-gradient-to-r from-purple-400 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
                        <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4 flex-1">
                      <p className="text-sm font-medium text-gray-300">Total Revenue</p>
                      <p className="text-3xl font-bold text-white">
                        ₹{invoices.reduce((sum, invoice) => sum + invoice.total_amount, 0).toLocaleString()}
                      </p>
                    </div>
                  </div>
                </div>

                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
                  <div className="flex items-center">
                    <div className="flex-shrink-0">
                      <div className="h-16 w-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg">
                        <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4 flex-1">
                      <p className="text-sm font-medium text-gray-300">Low Stock Items</p>
                      <p className="text-3xl font-bold text-white">
                        {products.filter(p => p.stock_quantity < 10).length}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8">
                  <h3 className="text-2xl font-bold text-white mb-6">Recent Products</h3>
                  <div className="space-y-4">
                    {products.slice(0, 5).map((product) => (
                      <div key={product.id} className="flex items-center space-x-4 p-4 bg-white/5 rounded-2xl">
                        <div className="h-12 w-12 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center">
                          <span className="text-white font-bold text-lg">
                            {product.name.charAt(0).toUpperCase()}
                          </span>
                        </div>
                        <div className="flex-1">
                          <h4 className="text-white font-semibold">{product.name}</h4>
                          <p className="text-gray-300 text-sm">₹{product.cost}</p>
                        </div>
                        <div className="text-right">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            product.stock_quantity > 20 ? 'bg-green-500/20 text-green-400' :
                            product.stock_quantity > 10 ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-red-500/20 text-red-400'
                          }`}>
                            {product.stock_quantity} in stock
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8">
                  <h3 className="text-2xl font-bold text-white mb-6">Recent Invoices</h3>
                  <div className="space-y-4">
                    {invoices.slice(0, 5).map((invoice) => (
                      <div key={invoice.id} className="flex items-center space-x-4 p-4 bg-white/5 rounded-2xl">
                        <div className="h-12 w-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                          <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div className="flex-1">
                          <h4 className="text-white font-semibold">#{invoice.invoice_number}</h4>
                          <p className="text-gray-300 text-sm">{invoice.customer_name}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-white font-semibold">₹{invoice.total_amount}</p>
                          <p className="text-gray-400 text-xs">
                            {new Date(invoice.created_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'products' && (
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-3xl font-bold text-white">Products</h3>
                <button 
                  onClick={() => navigate('/products/new')}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-2xl font-semibold hover:from-blue-700 hover:to-purple-700 transition-all duration-300 transform hover:scale-105 shadow-lg"
                >
                  Add Product
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <div key={product.id} className="backdrop-blur-xl bg-white/5 rounded-3xl p-6 border border-white/10 hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-2">
                    <div className="h-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl mb-4 flex items-center justify-center">
                      <span className="text-white text-4xl font-bold">
                        {product.name.charAt(0).toUpperCase()}
                      </span>
                    </div>
                    <h4 className="text-xl font-bold text-white mb-2">{product.name}</h4>
                    <p className="text-gray-300 mb-4 line-clamp-2">{product.description}</p>
                    <div className="flex justify-between items-center">
                      <span className="text-2xl font-bold text-green-400">₹{product.cost}</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                        product.stock_quantity > 20 ? 'bg-green-500/20 text-green-400' :
                        product.stock_quantity > 10 ? 'bg-yellow-500/20 text-yellow-400' :
                        'bg-red-500/20 text-red-400'
                      }`}>
                        {product.stock_quantity} in stock
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'invoices' && (
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-3xl font-bold text-white">Invoices</h3>
                <button className="bg-gradient-to-r from-green-600 to-emerald-600 text-white px-6 py-3 rounded-2xl font-semibold hover:from-green-700 hover:to-emerald-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                  Create Invoice
                </button>
              </div>
              <div className="space-y-4">
                {invoices.map((invoice) => (
                  <div key={invoice.id} className="backdrop-blur-xl bg-white/5 rounded-3xl p-6 border border-white/10 hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-4">
                        <div className="h-12 w-12 bg-gradient-to-r from-green-500 to-emerald-600 rounded-xl flex items-center justify-center">
                          <svg className="h-6 w-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                        </div>
                        <div>
                          <h4 className="text-xl font-bold text-white">#{invoice.invoice_number}</h4>
                          <p className="text-gray-300">{invoice.customer_name}</p>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-2xl font-bold text-green-400">₹{invoice.total_amount}</p>
                        <p className="text-gray-400">
                          {new Date(invoice.created_at).toLocaleDateString()}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'inventory' && (
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8">
              <div className="flex justify-between items-center mb-8">
                <h3 className="text-3xl font-bold text-white">Inventory Management</h3>
                <button className="bg-gradient-to-r from-purple-600 to-pink-600 text-white px-6 py-3 rounded-2xl font-semibold hover:from-purple-700 hover:to-pink-700 transition-all duration-300 transform hover:scale-105 shadow-lg">
                  Update Stock
                </button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {products.map((product) => (
                  <div key={product.id} className="backdrop-blur-xl bg-white/5 rounded-3xl p-6 border border-white/10 hover:shadow-2xl transition-all duration-300">
                    <div className="flex items-center space-x-4 mb-4">
                      <div className="h-12 w-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                        <span className="text-white font-bold text-lg">
                          {product.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h4 className="text-lg font-bold text-white">{product.name}</h4>
                        <p className="text-gray-300 text-sm">Current Stock</p>
                      </div>
                    </div>
                    <div className="mb-4">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-gray-300">Stock Level</span>
                        <span className={`font-semibold ${
                          product.stock_quantity > 20 ? 'text-green-400' :
                          product.stock_quantity > 10 ? 'text-yellow-400' :
                          'text-red-400'
                        }`}>
                          {product.stock_quantity} units
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div 
                          className={`h-2 rounded-full transition-all duration-300 ${
                            product.stock_quantity > 20 ? 'bg-green-500' :
                            product.stock_quantity > 10 ? 'bg-yellow-500' :
                            'bg-red-500'
                          }`}
                          style={{ width: `${Math.min((product.stock_quantity / 50) * 100, 100)}%` }}
                        ></div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <button className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-xl font-medium transition-all duration-300">
                        Add Stock
                      </button>
                      <button className="flex-1 bg-red-600 hover:bg-red-700 text-white py-2 px-4 rounded-xl font-medium transition-all duration-300">
                        Remove Stock
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
