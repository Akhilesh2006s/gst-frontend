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
products = []
customers = []
orders = []
invoices = []

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
            'customer_id': data.get('customer_id'),
            'products': data.get('products', []),
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
            'customer_id': data.get('customer_id'),
            'order_id': data.get('order_id'),
            'products': data.get('products', []),
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
            'customer_id': data.get('customer_id'),
            'order_id': data.get('order_id'),
            'products': data.get('products', []),
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
