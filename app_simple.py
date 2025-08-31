from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# Enable CORS with credentials support
CORS(app, 
     origins=["*"],
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Origin", "Accept", "X-Requested-With"],
     expose_headers=["Content-Type", "Authorization"],
     max_age=86400
)

# Simple in-memory storage for demo
products = [
    {
        'id': 1,
        'name': 'Sample Product 1',
        'description': 'This is a sample product for testing',
        'price': 100.0,
        'stock_quantity': 50,
        'created_at': datetime.utcnow().isoformat()
    },
    {
        'id': 2,
        'name': 'Sample Product 2',
        'description': 'Another sample product for testing',
        'price': 200.0,
        'stock_quantity': 30,
        'created_at': datetime.utcnow().isoformat()
    }
]
customers = []
orders = [
    {
        'id': 1,
        'order_number': 'ORD-0001',
        'customer_id': 1,
        'customer_name': 'Sample Customer',
        'customer_email': 'customer@example.com',
        'products': [],
        'items': [],
        'total_amount': 0,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat()
    }
]
invoices = [
    {
        'id': 1,
        'invoice_number': 'INV-0001',
        'customer_id': 1,
        'customer_name': 'Sample Customer',
        'customer_email': 'customer@example.com',
        'order_id': 1,
        'products': [],
        'items': [],
        'total_amount': 0,
        'gst_amount': 0,
        'status': 'pending',
        'created_at': datetime.utcnow().isoformat()
    }
]

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy', 
        'message': 'GST Billing System API is running',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/')
def root():
    return jsonify({
        'status': 'healthy', 
        'message': 'GST Billing System API is running',
        'version': '1.0.0',
        'timestamp': datetime.utcnow().isoformat()
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        'status': 'running',
        'message': 'API is operational'
    })

# Product routes
@app.route('/api/products', methods=['GET'])
@app.route('/api/products/', methods=['GET'])
def get_products():
    return jsonify({
        'success': True,
        'products': products
    })

@app.route('/api/products', methods=['POST'])
def create_product():
    try:
        data = request.get_json()
        product = {
            'id': len(products) + 1,
            'name': data.get('name'),
            'description': data.get('description'),
            'price': data.get('price'),
            'stock_quantity': data.get('stock_quantity', 0),
            'created_at': datetime.utcnow().isoformat()
        }
        products.append(product)
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product': product
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = next((p for p in products if p['id'] == product_id), None)
    if product:
        return jsonify({
            'success': True,
            'product': product
        })
    else:
        return jsonify({'success': False, 'message': 'Product not found'}), 404

@app.route('/api/products/<int:product_id>/stock', methods=['POST'])
def update_product_stock(product_id):
    try:
        product = next((p for p in products if p['id'] == product_id), None)
        if not product:
            return jsonify({'success': False, 'message': 'Product not found'}), 404
        
        data = request.get_json()
        movement_type = data.get('movement_type')
        quantity = data.get('quantity', 0)
        
        if movement_type == 'in':
            product['stock_quantity'] += quantity
        elif movement_type == 'out':
            if product['stock_quantity'] >= quantity:
                product['stock_quantity'] -= quantity
            else:
                return jsonify({'success': False, 'message': 'Insufficient stock'}), 400
        
        return jsonify({
            'success': True,
            'message': f'Stock updated successfully. New quantity: {product["stock_quantity"]}',
            'new_quantity': product['stock_quantity']
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Customer routes
@app.route('/api/admin/customers', methods=['GET'])
def get_customers():
    return jsonify({
        'success': True,
        'customers': customers
    })

@app.route('/api/admin/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        customer = {
            'id': len(customers) + 1,
            'name': data.get('name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'billing_address': data.get('billing_address'),
            'state': data.get('state', ''),
            'pincode': data.get('pincode', ''),
            'created_at': datetime.utcnow().isoformat(),
            'is_active': True
        }
        customers.append(customer)
        
        return jsonify({
            'success': True,
            'message': 'Customer created successfully',
            'customer': customer
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Customer order routes
@app.route('/api/customers/orders', methods=['GET'])
def get_customer_orders():
    # Return empty orders list for now
    return jsonify({
        'success': True,
        'orders': []
    })

@app.route('/api/customers/orders', methods=['POST'])
def create_customer_order():
    try:
        data = request.get_json()
        order = {
            'id': len(orders) + 1,
            'order_number': f'ORD-{len(orders) + 1:04d}',
            'customer_id': data.get('customer_id'),
            'customer_name': data.get('customer_name', 'Unknown Customer'),
            'customer_email': data.get('customer_email', 'unknown@example.com'),
            'products': data.get('products', []),
            'items': data.get('products', []),  # Add items field for compatibility
            'total_amount': data.get('total_amount', 0),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        orders.append(order)
        
        return jsonify({
            'success': True,
            'message': 'Order created successfully',
            'order': order
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Customer invoice routes
@app.route('/api/customers/invoices', methods=['GET'])
def get_customer_invoices():
    # Return empty invoices list for now
    return jsonify({
        'success': True,
        'invoices': []
    })

@app.route('/api/customers/invoices', methods=['POST'])
def create_customer_invoice():
    try:
        data = request.get_json()
        invoice = {
            'id': len(invoices) + 1,
            'invoice_number': f'INV-{len(invoices) + 1:04d}',
            'customer_id': data.get('customer_id'),
            'customer_name': data.get('customer_name', 'Unknown Customer'),
            'customer_email': data.get('customer_email', 'unknown@example.com'),
            'order_id': data.get('order_id'),
            'products': data.get('products', []),
            'items': data.get('products', []),  # Add items field for compatibility
            'total_amount': data.get('total_amount', 0),
            'gst_amount': data.get('gst_amount', 0),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        invoices.append(invoice)
        
        return jsonify({
            'success': True,
            'message': 'Invoice created successfully',
            'invoice': invoice
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Auth routes (simplified)
@app.route('/api/auth/register', methods=['POST'])
def register():
    return jsonify({
        'success': True,
        'message': 'Registration successful!'
    })

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    return jsonify({
        'success': True,
        'message': 'Login successful!',
        'user': {
            'id': 1,
            'username': 'admin',
            'email': 'admin@test.com',
            'business_name': 'Test Business'
        }
    })

@app.route('/api/auth/logout', methods=['POST'])
def auth_logout():
    return jsonify({
        'success': True,
        'message': 'Logout successful!'
    })

@app.route('/api/auth/check')
def auth_check():
    return jsonify({
        'authenticated': True,
        'user_type': 'admin',
        'user': {
            'id': 1,
            'username': 'admin',
            'email': 'admin@test.com'
        }
    })

# Admin order routes
@app.route('/api/admin/orders', methods=['GET'])
def get_admin_orders():
    return jsonify({
        'success': True,
        'orders': orders
    })

@app.route('/api/admin/orders/<int:order_id>/generate-invoice', methods=['POST'])
def generate_invoice_from_order(order_id):
    try:
        # Find the order
        order = next((o for o in orders if o['id'] == order_id), None)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Create invoice from order
        invoice = {
            'id': len(invoices) + 1,
            'invoice_number': f'INV-{len(invoices) + 1:04d}',
            'customer_id': order.get('customer_id'),
            'customer_name': order.get('customer_name', 'Unknown Customer'),
            'customer_email': order.get('customer_email', 'unknown@example.com'),
            'order_id': order_id,
            'products': order.get('products', []),
            'items': order.get('items', []),
            'total_amount': order.get('total_amount', 0),
            'gst_amount': order.get('total_amount', 0) * 0.18,  # 18% GST
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        invoices.append(invoice)
        
        # Update order status
        order['status'] = 'invoiced'
        
        return jsonify({
            'success': True,
            'message': 'Invoice generated successfully',
            'invoice': invoice
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        # Find the order
        order = next((o for o in orders if o['id'] == order_id), None)
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Update order status
        order['status'] = new_status
        
        return jsonify({
            'success': True,
            'message': f'Order status updated to {new_status}',
            'order': order
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Invoice routes
@app.route('/api/invoices', methods=['GET'])
def get_invoices():
    return jsonify({
        'success': True,
        'invoices': invoices
    })

@app.route('/api/invoices', methods=['POST'])
def create_invoice():
    try:
        data = request.get_json()
        invoice = {
            'id': len(invoices) + 1,
            'invoice_number': f'INV-{len(invoices) + 1:04d}',
            'customer_id': data.get('customer_id'),
            'customer_name': data.get('customer_name', 'Unknown Customer'),
            'customer_email': data.get('customer_email', 'unknown@example.com'),
            'order_id': data.get('order_id'),
            'products': data.get('products', []),
            'items': data.get('products', []),  # Add items field for compatibility
            'total_amount': data.get('total_amount', 0),
            'gst_amount': data.get('gst_amount', 0),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat()
        }
        invoices.append(invoice)
        
        return jsonify({
            'success': True,
            'message': 'Invoice created successfully',
            'invoice': invoice
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
