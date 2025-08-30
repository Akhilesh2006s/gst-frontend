import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface InventoryItem {
  id: number;
  name: string;
  sku: string;
  category: string;
  stock_quantity: number;
  min_stock_level: number;
  price: number;
  total_value: number;
  status: 'in_stock' | 'low_stock' | 'out_of_stock';
}

interface InventorySummary {
  total_products: number;
  total_value: number;
  low_stock_count: number;
  out_of_stock_count: number;
}

const Inventory: React.FC = () => {
  const navigate = useNavigate();
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [summary, setSummary] = useState<InventorySummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedStatus, setSelectedStatus] = useState('');
  const [showStockModal, setShowStockModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState<InventoryItem | null>(null);
  const [stockAction, setStockAction] = useState<'add' | 'remove'>('add');
  const [stockQuantity, setStockQuantity] = useState(1);
  const [stockReference, setStockReference] = useState('');
  const [stockNotes, setStockNotes] = useState('');
  
  // Add to Inventory form state
  const [showAddToInventoryModal, setShowAddToInventoryModal] = useState(false);
  const [newProduct, setNewProduct] = useState({
    name: '',
    sku: '',
    description: '',
    category: '',
    price: '',
    stock_quantity: '',
    min_stock_level: '10',
    image_url: ''
  });

  useEffect(() => {
    loadInventory();
  }, []);

  const loadInventory = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/products/inventory', {
        credentials: 'include'
      });
      if (response.ok) {
        const data = await response.json();
        const products = data.inventory || [];
        
        // Transform products to inventory items
        const inventoryItems: InventoryItem[] = products.map((product: any) => ({
          id: product.id,
          name: product.name,
          sku: product.sku || `SKU-${product.id}`,
          category: product.category || 'General',
          stock_quantity: product.stock_quantity || 0,
          min_stock_level: product.min_stock_level || 10,
          price: product.price || 0,
          total_value: (product.stock_quantity || 0) * (product.price || 0),
          status: (product.stock_quantity || 0) === 0 ? 'out_of_stock' : 
                  (product.stock_quantity || 0) <= (product.min_stock_level || 10) ? 'low_stock' : 'in_stock'
        }));
        
        setInventory(inventoryItems);
        
        // Calculate summary
        const summary: InventorySummary = {
          total_products: inventoryItems.length,
          total_value: inventoryItems.reduce((sum, item) => sum + item.total_value, 0),
          low_stock_count: inventoryItems.filter(item => item.status === 'low_stock').length,
          out_of_stock_count: inventoryItems.filter(item => item.status === 'out_of_stock').length
        };
        setSummary(summary);
      }
    } catch (error: any) {
      console.error('Failed to load inventory:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAddToInventory = async () => {
    try {
      const response = await fetch('/api/products/inventory/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          name: newProduct.name,
          sku: newProduct.sku,
          description: newProduct.description,
          category: newProduct.category,
          price: parseFloat(newProduct.price),
          stock_quantity: parseInt(newProduct.stock_quantity),
          min_stock_level: parseInt(newProduct.min_stock_level),
          image_url: newProduct.image_url
        })
      });

      if (response.ok) {
        const data = await response.json();
        alert(data.message);
        setShowAddToInventoryModal(false);
        setNewProduct({
          name: '',
          sku: '',
          description: '',
          category: '',
          price: '',
          stock_quantity: '',
          min_stock_level: '10',
          image_url: ''
        });
        await loadInventory();
      } else {
        const error = await response.json();
        alert(`Failed to add product: ${error.error}`);
      }
    } catch (error: any) {
      alert(`Failed to add product: ${error.message}`);
    }
  };

  const filteredInventory = inventory.filter(item => {
    const matchesSearch = item.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         item.sku.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = selectedStatus === '' || item.status === selectedStatus;
    return matchesSearch && matchesStatus;
  });

  const handleStockAction = (product: InventoryItem, action: 'add' | 'remove') => {
    setSelectedProduct(product);
    setStockAction(action);
    setStockQuantity(1);
    setStockReference('');
    setStockNotes('');
    setShowStockModal(true);
  };

  const handleStockSubmit = async () => {
    if (!selectedProduct) return;

    try {
      const response = await fetch(`/api/products/${selectedProduct.id}/stock`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          movement_type: stockAction === 'add' ? 'in' : 'out',
          quantity: stockQuantity,
          reference: stockReference || `${stockAction === 'add' ? 'Stock Added' : 'Stock Removed'}`,
          notes: stockNotes || `Manual ${stockAction} of ${stockQuantity} units`
        })
      });

      if (response.ok) {
        await loadInventory();
        setShowStockModal(false);
        setSelectedProduct(null);
      }
    } catch (error: any) {
      alert(`Failed to update stock: ${error.message}`);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'in_stock':
        return <span className="px-3 py-1 rounded-full text-sm font-medium bg-green-500/20 text-green-400">In Stock</span>;
      case 'low_stock':
        return <span className="px-3 py-1 rounded-full text-sm font-medium bg-yellow-500/20 text-yellow-400">Low Stock</span>;
      case 'out_of_stock':
        return <span className="px-3 py-1 rounded-full text-sm font-medium bg-red-500/20 text-red-400">Out of Stock</span>;
      default:
        return <span className="px-3 py-1 rounded-full text-sm font-medium bg-gray-500/20 text-gray-400">Unknown</span>;
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-blue-500 mx-auto mb-6"></div>
          <p className="text-gray-300 text-xl">Loading inventory...</p>
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
                <div className="h-16 w-16 bg-gradient-to-r from-purple-500 to-pink-600 rounded-2xl flex items-center justify-center shadow-lg">
                  <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 8h14M5 8a2 2 0 110-4h14a2 2 0 110 4M5 8v10a2 2 0 002 2h10a2 2 0 002-2V8m-9 4h4" />
                  </svg>
                </div>
              </div>
              <div className="ml-6">
                <h1 className="text-4xl font-bold text-white">Inventory Management</h1>
                <p className="text-gray-300 text-lg">Add products to inventory first, then they appear in products</p>
              </div>
            </div>
            <div className="flex space-x-4">
              <button
                onClick={() => navigate('/dashboard')}
                className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-2xl text-white bg-gray-600 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
                </svg>
                Back to Dashboard
              </button>
              <button
                onClick={() => setShowAddToInventoryModal(true)}
                className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-2xl text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all duration-300 transform hover:scale-105 shadow-lg"
              >
                <svg className="h-5 w-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
                Add to Inventory
              </button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
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
                  <p className="text-3xl font-bold text-white">{summary.total_products}</p>
                </div>
              </div>
            </div>

            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-16 w-16 bg-gradient-to-r from-green-400 to-emerald-500 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-300">Total Value</p>
                  <p className="text-3xl font-bold text-white">₹{summary.total_value.toLocaleString()}</p>
                </div>
              </div>
            </div>

            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-16 w-16 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-300">Low Stock</p>
                  <p className="text-3xl font-bold text-white">{summary.low_stock_count}</p>
                </div>
              </div>
            </div>

            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="flex items-center">
                <div className="flex-shrink-0">
                  <div className="h-16 w-16 bg-gradient-to-r from-red-400 to-pink-500 rounded-2xl flex items-center justify-center shadow-lg">
                    <svg className="h-8 w-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                </div>
                <div className="ml-4 flex-1">
                  <p className="text-sm font-medium text-gray-300">Out of Stock</p>
                  <p className="text-3xl font-bold text-white">{summary.out_of_stock_count}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Search and Filters */}
        <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-4 items-center justify-between">
            <div className="flex-1 max-w-md">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search inventory..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-xl"
                />
                <svg className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
            </div>
            
            <div className="flex space-x-4">
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                className="px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent backdrop-blur-xl"
              >
                <option value="">All Status</option>
                <option value="in_stock">In Stock</option>
                <option value="low_stock">Low Stock</option>
                <option value="out_of_stock">Out of Stock</option>
              </select>
            </div>
          </div>
        </div>

        {/* Inventory Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredInventory.map((item) => (
            <div key={item.id} className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-6 hover:shadow-3xl transition-all duration-300 transform hover:-translate-y-2">
              <div className="flex items-center space-x-4 mb-4">
                <div className="h-12 w-12 bg-gradient-to-r from-purple-500 to-pink-600 rounded-xl flex items-center justify-center">
                  <span className="text-white font-bold text-lg">
                    {item.name.charAt(0).toUpperCase()}
                  </span>
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">{item.name}</h3>
                  <p className="text-gray-300 text-sm">{item.sku}</p>
                </div>
              </div>
              
              <div className="mb-4">
                <div className="flex justify-between items-center mb-2">
                  <span className="text-gray-300">Stock Level</span>
                  <span className={`font-semibold ${
                    item.stock_quantity > item.min_stock_level ? 'text-green-400' :
                    item.stock_quantity > 0 ? 'text-yellow-400' : 'text-red-400'
                  }`}>
                    {item.stock_quantity} units
                  </span>
                </div>
                <div className="w-full bg-gray-700 rounded-full h-2">
                  <div 
                    className={`h-2 rounded-full transition-all duration-300 ${
                      item.stock_quantity > item.min_stock_level ? 'bg-green-500' :
                      item.stock_quantity > 0 ? 'bg-yellow-500' : 'bg-red-500'
                    }`}
                    style={{ width: `${Math.min((item.stock_quantity / (item.min_stock_level * 2)) * 100, 100)}%` }}
                  ></div>
                </div>
              </div>
              
              <div className="flex justify-between items-center mb-4">
                <span className="text-lg font-bold text-green-400">₹{item.price}</span>
                {getStatusBadge(item.status)}
              </div>
              
              <div className="flex space-x-2">
                <button
                  onClick={() => handleStockAction(item, 'add')}
                  className="flex-1 bg-green-600 hover:bg-green-700 text-white py-2 px-4 rounded-xl font-medium transition-all duration-300"
                >
                  Add Stock
                </button>
                <button
                  onClick={() => handleStockAction(item, 'remove')}
                  disabled={item.stock_quantity === 0}
                  className="flex-1 bg-red-600 hover:bg-red-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-2 px-4 rounded-xl font-medium transition-all duration-300"
                >
                  Remove Stock
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Add to Inventory Modal - Side by Side Layout */}
        {showAddToInventoryModal && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-4xl w-full mx-4">
              <h3 className="text-2xl font-bold text-white mb-6">Add Product to Inventory</h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Left Side - Form */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Product Name *
                    </label>
                    <input
                      type="text"
                      value={newProduct.name}
                      onChange={(e) => setNewProduct({...newProduct, name: e.target.value})}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter product name"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      SKU *
                    </label>
                    <input
                      type="text"
                      value={newProduct.sku}
                      onChange={(e) => setNewProduct({...newProduct, sku: e.target.value})}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter SKU"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Description
                    </label>
                    <textarea
                      value={newProduct.description}
                      onChange={(e) => setNewProduct({...newProduct, description: e.target.value})}
                      rows={3}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                      placeholder="Enter product description"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Category
                    </label>
                    <input
                      type="text"
                      value={newProduct.category}
                      onChange={(e) => setNewProduct({...newProduct, category: e.target.value})}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter category"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Price (₹) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={newProduct.price}
                      onChange={(e) => setNewProduct({...newProduct, price: e.target.value})}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter price"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Initial Stock Quantity *
                    </label>
                    <input
                      type="number"
                      value={newProduct.stock_quantity}
                      onChange={(e) => setNewProduct({...newProduct, stock_quantity: e.target.value})}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter initial stock"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Minimum Stock Level
                    </label>
                    <input
                      type="number"
                      value={newProduct.min_stock_level}
                      onChange={(e) => setNewProduct({...newProduct, min_stock_level: e.target.value})}
                      className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Enter minimum stock level"
                    />
                  </div>
                </div>

                {/* Right Side - Image Upload */}
                <div className="space-y-4">
                  <div>
                    <label className="block text-gray-300 text-sm font-medium mb-2">
                      Product Image
                    </label>
                    <div className="border-2 border-dashed border-white/20 rounded-2xl p-8 text-center hover:border-white/40 transition-colors duration-300">
                      <div className="space-y-4">
                        <div className="h-32 w-32 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl flex items-center justify-center mx-auto">
                          {newProduct.image_url ? (
                            <img 
                              src={newProduct.image_url} 
                              alt="Product preview"
                              className="w-full h-full object-cover rounded-2xl"
                            />
                          ) : (
                            <svg className="h-12 w-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          )}
                        </div>
                        <div>
                          <p className="text-gray-300 text-sm mb-2">
                            {newProduct.image_url ? 'Image uploaded successfully!' : 'Click to upload product image'}
                          </p>
                          <input
                            type="file"
                            accept="image/*"
                            onChange={(e) => {
                              const file = e.target.files?.[0];
                              if (file) {
                                const reader = new FileReader();
                                reader.onload = (e) => {
                                  setNewProduct({...newProduct, image_url: e.target?.result as string});
                                };
                                reader.readAsDataURL(file);
                              }
                            }}
                            className="hidden"
                            id="image-upload"
                          />
                          <label
                            htmlFor="image-upload"
                            className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-all duration-300 cursor-pointer"
                          >
                            <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                            </svg>
                            {newProduct.image_url ? 'Change Image' : 'Upload Image'}
                          </label>
                        </div>
                        {newProduct.image_url && (
                          <button
                            onClick={() => setNewProduct({...newProduct, image_url: ''})}
                            className="text-red-400 hover:text-red-300 text-sm transition-colors duration-300"
                          >
                            Remove Image
                          </button>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Product Preview */}
                  <div className="mt-6">
                    <h4 className="text-gray-300 text-sm font-medium mb-3">Product Preview</h4>
                    <div className="backdrop-blur-xl bg-white/5 rounded-2xl p-4 border border-white/10">
                      <div className="h-24 w-24 bg-gradient-to-r from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mx-auto mb-3">
                        {newProduct.image_url ? (
                          <img 
                            src={newProduct.image_url} 
                            alt="Preview"
                            className="w-full h-full object-cover rounded-xl"
                          />
                        ) : (
                          <span className="text-white text-2xl font-bold">
                            {newProduct.name ? newProduct.name.charAt(0).toUpperCase() : '?'}
                          </span>
                        )}
                      </div>
                      <div className="text-center">
                        <h5 className="text-white font-semibold text-sm mb-1">
                          {newProduct.name || 'Product Name'}
                        </h5>
                        <p className="text-green-400 font-bold">
                          {newProduct.price ? `₹${newProduct.price}` : '₹0.00'}
                        </p>
                        <p className="text-gray-400 text-xs mt-1">
                          {newProduct.stock_quantity ? `${newProduct.stock_quantity} in stock` : '0 in stock'}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <div className="flex space-x-4 mt-8">
                <button
                  onClick={() => setShowAddToInventoryModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-2xl font-medium transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleAddToInventory}
                  disabled={!newProduct.name || !newProduct.sku || !newProduct.price || !newProduct.stock_quantity}
                  className="flex-1 bg-purple-600 hover:bg-purple-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white py-3 px-4 rounded-2xl font-medium transition-all duration-300"
                >
                  Add to Inventory
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Stock Modal */}
        {showStockModal && selectedProduct && (
          <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
            <div className="backdrop-blur-xl bg-white/10 rounded-3xl shadow-2xl border border-white/20 p-8 max-w-md w-full mx-4">
              <h3 className="text-2xl font-bold text-white mb-6">
                {stockAction === 'add' ? 'Add Stock' : 'Remove Stock'}
              </h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Product: {selectedProduct.name}
                  </label>
                </div>
                
                <div>
                  <label className="block text-gray-300 text-sm font-medium mb-2">
                    Quantity
                  </label>
                  <input
                    type="number"
                    min="1"
                    value={stockQuantity}
                    onChange={(e) => setStockQuantity(parseInt(e.target.value) || 1)}
                    className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>
              </div>
              
              <div className="flex space-x-4 mt-8">
                <button
                  onClick={() => setShowStockModal(false)}
                  className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-3 px-4 rounded-2xl font-medium transition-all duration-300"
                >
                  Cancel
                </button>
                <button
                  onClick={handleStockSubmit}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-2xl font-medium transition-all duration-300"
                >
                  {stockAction === 'add' ? 'Add Stock' : 'Remove Stock'}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Inventory;
