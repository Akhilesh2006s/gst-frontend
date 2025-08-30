import React, { useState, useEffect } from 'react';

interface Product {
  id: number;
  name: string;
  description: string;
  price: number;
  stock_quantity: number;
  image_url?: string;
}

interface CartItem {
  product: Product;
  quantity: number;
}

interface CustomerOrder {
  id: number;
  order_number: string;
  order_date: string;
  status: string;
  total_amount: number;
  notes: string;
  items: any[];
  created_at: string;
}

interface CustomerInvoice {
  id: number;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  status: string;
  total_amount: number;
  notes: string;
  items: any[];
  created_at: string;
}

interface CustomerDashboardProps {
  onLogout: () => void;
}

const CustomerDashboard: React.FC<CustomerDashboardProps> = ({ onLogout }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [orders, setOrders] = useState<CustomerOrder[]>([]);
  const [invoices, setInvoices] = useState<CustomerInvoice[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [showCart, setShowCart] = useState(false);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showOrders, setShowOrders] = useState(false);
  const [showInvoices, setShowInvoices] = useState(false);
  const [orderNotes, setOrderNotes] = useState('');
  const [ordersLoading, setOrdersLoading] = useState(false);
  const [invoicesLoading, setInvoicesLoading] = useState(false);

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch('https://web-production-84a3.up.railway.app/api/products', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        setProducts(data.products || []);
      }
    } catch (error: any) {
      console.error('Failed to load products:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadOrders = async () => {
    try {
      setOrdersLoading(true);
      const response = await fetch('https://web-production-84a3.up.railway.app/api/customers/orders', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setOrders(data.orders || []);
      } else {
        console.error('Failed to load orders:', response.status, response.statusText);
        setOrders([]);
      }
    } catch (error: any) {
      console.error('Failed to load orders:', error);
      setOrders([]);
    } finally {
      setOrdersLoading(false);
    }
  };

  const loadInvoices = async () => {
    try {
      setInvoicesLoading(true);
      const response = await fetch('https://web-production-84a3.up.railway.app/api/customers/invoices', {
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setInvoices(data.invoices || []);
      } else {
        console.error('Failed to load invoices:', response.status, response.statusText);
        setInvoices([]);
      }
    } catch (error: any) {
      console.error('Failed to load invoices:', error);
      setInvoices([]);
    } finally {
      setInvoicesLoading(false);
    }
  };

  const handleLogout = () => {
    // Call the parent's logout function
    onLogout();
  };

  const addToCart = (product: Product) => {
    setCart(prevCart => {
      const existingItem = prevCart.find(item => item.product.id === product.id);
      if (existingItem) {
        return prevCart.map(item =>
          item.product.id === product.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      } else {
        return [...prevCart, { product, quantity: 1 }];
      }
    });
  };

  const removeFromCart = (productId: number) => {
    setCart(prevCart => prevCart.filter(item => item.product.id !== productId));
  };

  const updateQuantity = (productId: number, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(prevCart =>
      prevCart.map(item =>
        item.product.id === productId
          ? { ...item, quantity }
          : item
      )
    );
  };

  const getTotalAmount = () => {
    return cart.reduce((total, item) => total + (item.product.price * item.quantity), 0);
  };

  const handleSubmitOrder = async () => {
    try {
      const orderData = {
        items: cart.map(item => ({
          product_id: item.product.id,
          quantity: item.quantity,
          unit_price: item.product.price
        })),
        notes: orderNotes,
        total_amount: getTotalAmount()
      };

                           const response = await fetch('https://web-production-84a3.up.railway.app/api/customers/orders', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          credentials: 'include',
          body: JSON.stringify(orderData)
        });

      if (response.ok) {
        const data = await response.json();
                  if (data.success) {
            alert('Order submitted successfully!');
            setCart([]);
            setOrderNotes('');
            setShowOrderModal(false);
            setShowCart(false);
            loadOrders(); // Reload orders to show the new one
          } else {
          alert(data.error || 'Failed to submit order');
        }
      } else {
        alert('Failed to submit order');
      }
    } catch (error: any) {
      console.error('Failed to submit order:', error);
      alert('Failed to submit order');
    }
  };

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      minimumFractionDigits: 2
    }).format(amount);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const filteredProducts = products.filter(product =>
    product.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    product.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-500 mx-auto mb-6"></div>
          <p className="text-gray-300 text-xl">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <div className="backdrop-blur-xl bg-white/10 border-b border-white/20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="h-12 w-12 bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl flex items-center justify-center">
                <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <div>
                <h1 className="text-3xl font-bold text-white">Product Catalog</h1>
                <p className="text-gray-300">Browse and order products</p>
              </div>
            </div>
            
            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowOrders(true);
                  loadOrders();
                }}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl font-medium transition-all duration-300 flex items-center space-x-2"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>My Orders ({orders.length})</span>
              </button>
              <button
                onClick={() => {
                  setShowInvoices(true);
                  loadInvoices();
                }}
                className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-xl font-medium transition-all duration-300 flex items-center space-x-2"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <span>My Invoices ({invoices.length})</span>
              </button>
              <button
                onClick={() => setShowCart(true)}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-xl font-medium transition-all duration-300 flex items-center space-x-2"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4m0 0L7 13m0 0l-2.5 5M7 13l2.5 5m6-5v6a2 2 0 01-2 2H9a2 2 0 01-2-2v-6m6 0V9a2 2 0 00-2-2H9a2 2 0 00-2 2v4.01" />
                </svg>
                <span>Cart ({cart.length})</span>
              </button>
              <button
                onClick={handleLogout}
                className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-xl font-medium transition-all duration-300 flex items-center space-x-2"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span>Logout</span>
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Search */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <svg className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
            <div className="text-right">
              <p className="text-gray-300 text-sm">{filteredProducts.length} products found</p>
            </div>
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredProducts.map((product) => (
            <div key={product.id} className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 overflow-hidden hover:transform hover:scale-105 transition-all duration-300">
              <div className="aspect-w-16 aspect-h-9 bg-gray-800">
                {product.image_url ? (
                  <img
                    src={product.image_url}
                    alt={product.name}
                    className="w-full h-48 object-cover"
                  />
                ) : (
                  <div className="w-full h-48 bg-gradient-to-br from-gray-600 to-gray-700 flex items-center justify-center">
                    <svg className="h-16 w-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
              </div>
              <div className="p-6">
                <h3 className="text-xl font-bold text-white mb-2">{product.name}</h3>
                <p className="text-gray-300 text-sm mb-4 line-clamp-2">{product.description}</p>
                <div className="flex items-center justify-between mb-4">
                  <span className="text-2xl font-bold text-green-400">{formatCurrency(product.price)}</span>
                  <span className="text-gray-400 text-sm">Stock: {product.stock_quantity}</span>
                </div>
                <button
                  onClick={() => addToCart(product)}
                  disabled={product.stock_quantity === 0}
                  className="w-full bg-gradient-to-r from-blue-600 to-purple-600 text-white py-3 rounded-2xl font-medium hover:from-blue-700 hover:to-purple-700 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {product.stock_quantity === 0 ? 'Out of Stock' : 'Add to Cart'}
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Empty State */}
        {filteredProducts.length === 0 && (
          <div className="text-center py-12">
            <div className="h-24 w-24 bg-gradient-to-r from-gray-500 to-gray-600 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg className="h-12 w-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
              </svg>
            </div>
            <h3 className="text-2xl font-bold text-white mb-2">No products found</h3>
            <p className="text-gray-300">Try adjusting your search criteria</p>
          </div>
        )}
      </div>

      {/* Cart Modal */}
      {showCart && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Shopping Cart</h2>
              <button
                onClick={() => setShowCart(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {cart.length === 0 ? (
              <div className="text-center py-8">
                <p className="text-gray-300 mb-4">Your cart is empty</p>
                <button
                  onClick={() => setShowCart(false)}
                  className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-medium transition-all duration-300"
                >
                  Continue Shopping
                </button>
              </div>
            ) : (
              <>
                <div className="space-y-4 mb-6">
                  {cart.map((item) => (
                    <div key={item.product.id} className="flex items-center justify-between p-4 bg-white/5 rounded-2xl">
                      <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 bg-gray-800 rounded-xl flex items-center justify-center">
                          {item.product.image_url ? (
                            <img
                              src={item.product.image_url}
                              alt={item.product.name}
                              className="w-full h-full object-cover rounded-xl"
                            />
                          ) : (
                            <svg className="h-8 w-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          )}
                        </div>
                        <div>
                          <h3 className="text-white font-medium">{item.product.name}</h3>
                          <p className="text-gray-300 text-sm">{formatCurrency(item.product.price)}</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => updateQuantity(item.product.id, item.quantity - 1)}
                          className="w-8 h-8 bg-gray-600 hover:bg-gray-700 text-white rounded-lg flex items-center justify-center transition-colors"
                        >
                          -
                        </button>
                        <span className="text-white font-medium w-8 text-center">{item.quantity}</span>
                        <button
                          onClick={() => updateQuantity(item.product.id, item.quantity + 1)}
                          className="w-8 h-8 bg-gray-600 hover:bg-gray-700 text-white rounded-lg flex items-center justify-center transition-colors"
                        >
                          +
                        </button>
                        <button
                          onClick={() => removeFromCart(item.product.id)}
                          className="text-red-400 hover:text-red-300 ml-2"
                        >
                          <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                <div className="border-t border-white/20 pt-4 mb-6">
                  <div className="flex justify-between items-center text-xl font-bold text-white">
                    <span>Total:</span>
                    <span>{formatCurrency(getTotalAmount())}</span>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={() => setShowCart(false)}
                    className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-2xl font-medium transition-all duration-300"
                  >
                    Continue Shopping
                  </button>
                  <button
                    onClick={() => {
                      setShowCart(false);
                      setShowOrderModal(true);
                    }}
                    className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-2xl font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-300"
                  >
                    Place Order
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}

      {/* Order Modal */}
      {showOrderModal && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-md w-full mx-4">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-2xl font-bold text-white">Confirm Order</h2>
              <button
                onClick={() => setShowOrderModal(false)}
                className="text-gray-400 hover:text-white transition-colors"
              >
                <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <h3 className="text-white font-medium mb-2">Order Summary:</h3>
                <div className="space-y-2">
                  {cart.map((item) => (
                    <div key={item.product.id} className="flex justify-between text-gray-300">
                      <span>{item.product.name} x {item.quantity}</span>
                      <span>{formatCurrency(item.product.price * item.quantity)}</span>
                    </div>
                  ))}
                  <div className="border-t border-white/20 pt-2">
                    <div className="flex justify-between text-white font-bold">
                      <span>Total:</span>
                      <span>{formatCurrency(getTotalAmount())}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-white text-sm font-medium mb-2">Order Notes (Optional)</label>
                <textarea
                  value={orderNotes}
                  onChange={(e) => setOrderNotes(e.target.value)}
                  rows={3}
                  className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Any special instructions or notes..."
                />
              </div>

              <div className="flex space-x-4 pt-4">
                <button
                  onClick={() => setShowOrderModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 rounded-2xl font-medium transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitOrder}
                  className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600 text-white py-3 rounded-2xl font-medium hover:from-green-700 hover:to-emerald-700 transition-all duration-300"
                >
                  Confirm Order
                </button>
              </div>
            </div>
          </div>
        </div>
              )}

        {/* Orders Modal */}
        {showOrders && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Your Orders</h2>
                <button
                  onClick={() => setShowOrders(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {ordersLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-gray-300">Loading orders...</p>
                </div>
              ) : orders.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-300 mb-4">You have no orders yet.</p>
                  <button
                    onClick={() => setShowOrders(false)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-medium transition-all duration-300"
                  >
                    Back to Products
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {orders.map((order) => (
                    <div key={order.id} className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-white">Order #{order.order_number}</h3>
                        <span className="text-gray-300 text-sm">Date: {formatDate(order.order_date)}</span>
                      </div>
                      <p className="text-gray-300 text-sm mb-4">Status: <span className={`font-medium ${order.status === 'Completed' ? 'text-green-400' : order.status === 'Pending' ? 'text-yellow-400' : 'text-red-400'}`}>{order.status}</span></p>
                      <div className="flex justify-between items-center text-xl font-bold text-white mb-4">
                        <span>Total:</span>
                        <span>{formatCurrency(order.total_amount)}</span>
                      </div>
                      <p className="text-gray-300 text-sm mb-4">Notes: {order.notes || 'No notes'}</p>
                      <div className="text-gray-300 text-sm">Items:</div>
                      <ul className="space-y-2">
                        {order.items.map((item: any) => (
                          <li key={item.id} className="text-gray-300 text-sm">
                            {item.product_name} x {item.quantity} ({formatCurrency(item.unit_price)})
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Invoices Modal */}
        {showInvoices && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">Your Invoices</h2>
                <button
                  onClick={() => setShowInvoices(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>

              {invoicesLoading ? (
                <div className="text-center py-8">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
                  <p className="text-gray-300">Loading invoices...</p>
                </div>
              ) : invoices.length === 0 ? (
                <div className="text-center py-8">
                  <p className="text-gray-300 mb-4">You have no invoices yet.</p>
                  <button
                    onClick={() => setShowInvoices(false)}
                    className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl font-medium transition-all duration-300"
                  >
                    Back to Products
                  </button>
                </div>
              ) : (
                <div className="space-y-6">
                  {invoices.map((invoice) => (
                    <div key={invoice.id} className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-xl font-bold text-white">Invoice #{invoice.invoice_number}</h3>
                        <span className="text-gray-300 text-sm">Date: {formatDate(invoice.invoice_date)}</span>
                      </div>
                      <p className="text-gray-300 text-sm mb-4">Status: <span className={`font-medium ${invoice.status === 'paid' ? 'text-green-400' : invoice.status === 'pending' ? 'text-yellow-400' : 'text-red-400'}`}>{invoice.status}</span></p>
                      <div className="flex justify-between items-center text-xl font-bold text-white mb-4">
                        <span>Total:</span>
                        <span>{formatCurrency(invoice.total_amount)}</span>
                      </div>
                      <p className="text-gray-300 text-sm mb-4">Due Date: {formatDate(invoice.due_date)}</p>
                      <p className="text-gray-300 text-sm mb-4">Notes: {invoice.notes || 'No notes'}</p>
                      <div className="text-gray-300 text-sm">Items:</div>
                      <ul className="space-y-2">
                        {invoice.items.map((item: any) => (
                          <li key={item.id} className="text-gray-300 text-sm">
                            {item.product_name} x {item.quantity} ({formatCurrency(item.unit_price)})
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

export default CustomerDashboard;
