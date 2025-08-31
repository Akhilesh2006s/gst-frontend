from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = None

# Enable CORS with comprehensive configuration
CORS(app, 
     origins=["*"],  # Allow all origins temporarily
     supports_credentials=True,
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     allow_headers=["Content-Type", "Authorization", "Origin", "Accept", "X-Requested-With"],
     expose_headers=["Content-Type", "Authorization"],
     max_age=86400
)



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    business_name = db.Column(db.String(200), nullable=True)
    business_reason = db.Column(db.Text, nullable=True)
    is_approved = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Customer(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    state = db.Column(db.String(50), nullable=True)
    pincode = db.Column(db.String(10), nullable=True)
    password_hash = db.Column(db.String(200), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    gst_rate = db.Column(db.Float, default=18.0)
    stock_quantity = db.Column(db.Integer, default=0)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# User loader
@login_manager.user_loader
def load_user(user_id):
    # Try to load admin user first, then customer
    user = User.query.get(int(user_id))
    if user:
        return user
    
    customer = Customer.query.get(int(user_id))
    return customer

# Routes
@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'message': 'GST Billing System API is running'})

@app.route('/')
def root():
    return jsonify({'status': 'healthy', 'message': 'GST Billing System API is running'})

@app.route('/api/test')
def test_api():
    return jsonify({'message': 'API is working!'})

# Auth routes
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        username = data.get('username')
        business_name = data.get('business_name')
        business_reason = data.get('business_reason')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create new user
        user = User(
            email=email,
            username=username,
            business_name=business_name,
            business_reason=business_reason,
            is_approved=True,  # Auto-approve all registrations
            is_active=True
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! You can now login.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def auth_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password) and user.is_approved:
            login_user(user, remember=data.get('remember_me', False))
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'business_name': user.business_name
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials or account not approved'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/auth/logout')
@login_required
def auth_logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'})

@app.route('/api/auth/check')
def auth_check():
    if current_user.is_authenticated:
        if hasattr(current_user, 'business_name'):
            return jsonify({
                'authenticated': True,
                'user_type': 'admin',
                'user': {
                    'id': current_user.id,
                    'username': current_user.username,
                    'email': current_user.email
                }
            })
        else:
            return jsonify({
                'authenticated': True,
                'user_type': 'customer',
                'user': {
                    'id': current_user.id,
                    'name': current_user.name,
                    'email': current_user.email
                }
            })
    return jsonify({'authenticated': False}), 401



@app.route('/api/admin/dashboard')
@login_required
def admin_dashboard():
    try:
        # Get basic stats
        total_customers = Customer.query.filter_by(is_active=True).count()
        total_products = Product.query.filter_by(is_active=True).count()
        
        return jsonify({
            'success': True,
            'stats': {
                'total_customers': total_customers,
                'total_products': total_products
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500



# Customer routes
@app.route('/api/customer-auth/register', methods=['POST'])
def customer_register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone')
        address = data.get('address')
        
        # Check if customer already exists
        if Customer.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create new customer
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address
        )
        customer.set_password(password)
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful!'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customer-auth/login', methods=['POST'])
def customer_login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        customer = Customer.query.filter_by(email=email).first()
        if customer and customer.check_password(password):
            login_user(customer, remember=data.get('remember_me', False))
            return jsonify({
                'success': True,
                'message': 'Login successful!',
                'customer': {
                    'id': customer.id,
                    'name': customer.name,
                    'email': customer.email
                }
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customer-auth/logout')
@login_required
def customer_logout():
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'})

# Admin routes
@app.route('/api/admin/customers', methods=['GET'])
@login_required
def get_customers():
    try:
        customers = Customer.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'customers': [{
                'id': c.id,
                'name': c.name,
                'email': c.email,
                'phone': c.phone,
                'billing_address': c.address,  # Map 'address' to 'billing_address' for frontend
                'state': c.state or '',  # Return actual state value
                'pincode': c.pincode or '',  # Return actual pincode value
                'created_at': c.created_at.isoformat(),
                'is_active': c.is_active
            } for c in customers]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/customers', methods=['POST'])
@login_required
def create_customer():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone')
        # Handle both 'address' and 'billing_address' field names
        address = data.get('address') or data.get('billing_address')
        password = data.get('password', 'default123')
        
        if Customer.query.filter_by(email=email).first():
            return jsonify({'success': False, 'message': 'Email already exists'}), 400
        
        customer = Customer(
            name=name,
            email=email,
            phone=phone,
            address=address,
            state=data.get('state', ''),
            pincode=data.get('pincode', '')
        )
        customer.set_password(password)
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer created successfully',
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/customers/<int:customer_id>', methods=['PUT'])
@login_required
def update_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        data = request.get_json()
        
        customer.name = data.get('name', customer.name)
        customer.email = data.get('email', customer.email)
        customer.phone = data.get('phone', customer.phone)
        customer.address = data.get('address', customer.address)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    try:
        customer = Customer.query.get_or_404(customer_id)
        customer.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Customer deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Order and Invoice models
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='orders', lazy=True)
    admin = db.relationship('User', backref='orders', lazy=True)
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='order_items', lazy=True)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(50), unique=True, nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    gst_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    customer = db.relationship('Customer', backref='invoices', lazy=True)
    admin = db.relationship('User', backref='invoices', lazy=True)
    order = db.relationship('Order', backref='invoices', lazy=True)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True, cascade='all, delete-orphan')

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    gst_rate = db.Column(db.Float, nullable=False)
    
    product = db.relationship('Product', backref='invoice_items', lazy=True)

# Product routes
@app.route('/api/products', methods=['GET'])
@app.route('/api/products/', methods=['GET'])
def get_products():
    try:
        products = Product.query.filter_by(is_active=True).all()
        return jsonify({
            'success': True,
            'products': [{
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': p.price,
                'gst_rate': p.gst_rate,
                'stock_quantity': p.stock_quantity,
                'created_at': p.created_at.isoformat()
            } for p in products]
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products', methods=['POST'])
@login_required
def create_product():
    try:
        data = request.get_json()
        name = data.get('name')
        description = data.get('description')
        price = data.get('price')
        gst_rate = data.get('gst_rate', 18.0)
        stock_quantity = data.get('stock_quantity', 0)
        
        product = Product(
            name=name,
            description=description,
            price=price,
            gst_rate=gst_rate,
            stock_quantity=stock_quantity,
            admin_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product created successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'price': product.price
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.price = data.get('price', product.price)
        product.gst_rate = data.get('gst_rate', product.gst_rate)
        product.stock_quantity = data.get('stock_quantity', product.stock_quantity)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product updated successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        product.is_active = False
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Product deleted successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Order routes
@app.route('/api/admin/orders', methods=['GET'])
@app.route('/api/admin/orders/', methods=['GET'])
@login_required
def get_orders():
    try:
        # Get orders for the current admin
        orders = Order.query.filter_by(admin_id=current_user.id).all()
        
        orders_data = []
        for order in orders:
            try:
                customer_name = order.customer.name if order.customer else 'Unknown'
            except:
                customer_name = 'Unknown'
            
            orders_data.append({
                'id': order.id,
                'customer_name': customer_name,
                'total_amount': order.total_amount,
                'status': order.status,
                'created_at': order.created_at.isoformat(),
                'items_count': len(order.items)
            })
        
        return jsonify({
            'success': True,
            'orders': orders_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        new_status = data.get('status')
        
        if new_status in ['pending', 'processing', 'completed', 'cancelled']:
            order.status = new_status
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': f'Order status updated to {new_status}'
            })
        else:
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/admin/orders/<int:order_id>/generate-invoice', methods=['POST'])
@login_required
def generate_invoice(order_id):
    try:
        order = Order.query.get_or_404(order_id)
        
        # Check if invoice already exists for this order
        existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
        if existing_invoice:
            return jsonify({'success': False, 'message': 'Invoice already exists for this order'}), 400
        
        # Generate invoice number
        invoice_count = Invoice.query.count()
        invoice_number = f'INV-{invoice_count + 1:03d}-{order_id}'
        
        # Calculate GST
        gst_rate = 18.0  # Default GST rate
        gst_amount = order.total_amount * (gst_rate / 100)
        
        # Create invoice
        invoice = Invoice(
            invoice_number=invoice_number,
            order_id=order_id,
            customer_id=order.customer_id,
            admin_id=order.admin_id,
            total_amount=order.total_amount,
            gst_amount=gst_amount
        )
        
        db.session.add(invoice)
        
        # Create invoice items from order items
        for item in order.items:
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.price,
                gst_rate=gst_rate
            )
            db.session.add(invoice_item)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice generated successfully',
            'invoice': {
                'id': invoice.id,
                'number': invoice.invoice_number,
                'total_amount': invoice.total_amount
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Invoice routes
@app.route('/api/invoices', methods=['GET'])
@app.route('/api/invoices/', methods=['GET'])
@login_required
def get_invoices():
    try:
        # Get invoices for the current admin
        invoices = Invoice.query.filter_by(admin_id=current_user.id).all()
        
        invoices_data = []
        for invoice in invoices:
            try:
                customer_name = invoice.customer.name if invoice.customer else 'Unknown'
            except:
                customer_name = 'Unknown'
            
            invoices_data.append({
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'customer_name': customer_name,
                'total_amount': invoice.total_amount,
                'gst_amount': invoice.gst_amount,
                'created_at': invoice.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'invoices': invoices_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/customers/invoices', methods=['GET'])
@app.route('/api/customers/invoices/', methods=['GET'])
@login_required
def get_customer_invoices():
    try:
        # Get invoices for the current customer
        invoices = Invoice.query.filter_by(customer_id=current_user.id).all()
        
        invoices_data = []
        for invoice in invoices:
            invoices_data.append({
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'total_amount': invoice.total_amount,
                'gst_amount': invoice.gst_amount,
                'created_at': invoice.created_at.isoformat()
            })
        
        return jsonify({
            'success': True,
            'invoices': invoices_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/invoices/<int:invoice_id>', methods=['GET'])
@login_required
def get_invoice(invoice_id):
    try:
        invoice = Invoice.query.get_or_404(invoice_id)
        
        # Check if user has access to this invoice
        if not (current_user.id == invoice.admin_id or current_user.id == invoice.customer_id):
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        invoice_data = {
            'id': invoice.id,
            'invoice_number': invoice.invoice_number,
            'total_amount': invoice.total_amount,
            'gst_amount': invoice.gst_amount,
            'created_at': invoice.created_at.isoformat(),
            'items': []
        }
        
        for item in invoice.items:
            try:
                product_name = item.product.name if item.product else 'Unknown Product'
            except:
                product_name = 'Unknown Product'
            
            invoice_data['items'].append({
                'id': item.id,
                'product_name': product_name,
                'quantity': item.quantity,
                'price': item.price,
                'gst_rate': item.gst_rate
            })
        
        return jsonify({
            'success': True,
            'invoice': invoice_data
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/invoices/<int:invoice_id>/pdf', methods=['GET'])
@login_required
def get_invoice_pdf(invoice_id):
    try:
        # Placeholder - return success for now
        return jsonify({
            'success': True,
            'message': 'PDF generated successfully',
            'pdf_url': f'/api/invoices/{invoice_id}/pdf'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# Initialize database
def init_db():
    with app.app_context():
        # Drop and recreate all tables to handle schema changes
        db.drop_all()
        db.create_all()
        print("Database initialized successfully!")

# Initialize database when app starts
init_db()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
