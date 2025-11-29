from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from models import Product, StockMovement, CustomerProductPrice, Customer
from database import db

def get_db():
    """Get database instance"""
    from database import db as database
    return database
from bson import ObjectId
from forms import ProductForm, StockMovementForm
from datetime import datetime
import os
import uuid
import re
from werkzeug.utils import secure_filename

product_bp = Blueprint('product', __name__)

# API Routes for React Frontend
@product_bp.route('/inventory/add', methods=['POST'])
@login_required
def api_add_to_inventory():
    """Add a new product to inventory"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Product name is required'}), 400
        if not data.get('price'):
            return jsonify({'success': False, 'error': 'Product price is required'}), 400
        
        # Auto-generate SKU if not provided
        sku = data.get('sku')
        if not sku:
            # Generate SKU from product name and timestamp
            name_part = re.sub(r'[^A-Z0-9]', '', data['name'].upper())[:10] or 'PROD'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')[-8:]  # Last 8 digits
            sku = f"{name_part}-{timestamp}"
            
            # Ensure SKU is unique
            counter = 1
            original_sku = sku
            user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
            while db['products'].find_one({'sku': sku, 'user_id': user_id_obj}):
                sku = f"{original_sku}-{counter}"
                counter += 1
        
        # Check if SKU already exists (if provided)
        user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        if data.get('sku') and db['products'].find_one({'sku': sku, 'user_id': user_id_obj}):
            return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        product = Product(
            user_id=current_user.id,
            admin_id=current_user.id,  # Set admin_id to same as user_id for backward compatibility
            name=data['name'],
            description=data.get('description', ''),
            sku=sku,
            hsn_code=data.get('hsn_code', ''),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            price=float(data['price']),
            gst_rate=float(data.get('gst_rate', 18)),
            stock_quantity=int(data.get('stock_quantity', 0)),
            min_stock_level=int(data.get('min_stock_level', 10)),
            unit=data.get('unit', 'PCS'),
            image_url=data.get('image_url', ''),
            weight=float(data.get('weight', 0)) if data.get('weight') else None,
            dimensions=data.get('dimensions', ''),
            vegetable_name=data.get('vegetable_name', ''),
            vegetable_name_hindi=data.get('vegetable_name_hindi', ''),
            quantity_gm=float(data.get('quantity_gm')) if data.get('quantity_gm') is not None else None,
            quantity_kg=float(data.get('quantity_kg')) if data.get('quantity_kg') is not None else None,
            rate_per_gm=float(data.get('rate_per_gm')) if data.get('rate_per_gm') is not None else None,
            rate_per_kg=float(data.get('rate_per_kg')) if data.get('rate_per_kg') is not None else None,
            is_active=True
        )
        
        product.save()
        
        # Add initial stock movement if stock quantity > 0
        if data.get('stock_quantity', 0) > 0:
            movement = StockMovement(
                product_id=product.id,
                movement_type='in',
                quantity=data['stock_quantity'],
                reference='Initial stock',
                notes='Product added to inventory',
                created_at=datetime.utcnow()
            )
            movement.save()
        
        return jsonify({
            'success': True, 
            'message': 'Product added to inventory successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'price': float(product.price),
                'stock_quantity': product.stock_quantity
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/', methods=['GET'])
@login_required
def api_get_products():
    """Get products from inventory (limited fields for products page) with customer-specific pricing"""
    try:
        # Check if user is authenticated
        if not current_user or not hasattr(current_user, 'id'):
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        # Determine if current_user is a Customer or Admin/User
        # Check by trying to find customer record - more reliable than isinstance
        from models import Customer
        database = get_db()
        # Try to find customer in database directly
        customer_doc = database['customers'].find_one({'_id': ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id})
        is_customer = customer_doc is not None
        
        if is_customer:
            customer = Customer.from_dict(customer_doc) if customer_doc else None
            print(f"Customer found: {customer_doc.get('name') if customer_doc else 'None'}, user_id={customer_doc.get('user_id') if customer_doc else 'None'}")
        else:
            customer = None
            print(f"No customer found for ID: {current_user.id}, checking if admin/user")
        
        print(f"Customer detection: is_customer={is_customer}, user_id={current_user.id}")
        
        if is_customer:
            # For customers, get their admin's user_id
            if not customer.user_id:
                return jsonify({'success': False, 'error': 'Customer not associated with an admin'}), 404
            user_id = customer.user_id
            # Customers should only see active products
            query = {
                'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
                'is_active': True
            }
            customer_id = current_user.id  # Use the logged-in customer's ID for pricing
        else:
            # For admins, use their own user_id
            user_id = current_user.id
            query = {'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id}
            customer_id = request.args.get('customer_id', type=int)  # Optional customer ID for customer-specific pricing
        
        print(f"Products API called by user: {user_id} (customer: {is_customer})")
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'sku': {'$regex': search, '$options': 'i'}},
                {'hsn_code': {'$regex': search, '$options': 'i'}}
            ]
        
        if category and category != 'All':
            query['category'] = category
        
        # Get database instance
        database = get_db() if 'get_db' in globals() else db
        if database is None:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500
        
        products = [Product.from_dict(doc) for doc in database['products'].find(query).sort('name', 1)]
        print(f"Found {len(products)} products for user {user_id}")
        
        # Return only the fields needed for products page
        products_data = []
        for product in products:
            try:
                # Get customer-specific price if customer_id is provided
                if customer_id:
                    # Check if customer exists (can be from any admin since products are visible to all)
                    customer = Customer.find_by_id(customer_id)
                    if customer:
                        # Get customer-specific price if set for this product
                        try:
                            price = product.get_customer_price(customer_id)
                        except Exception as price_error:
                            print(f"Error getting customer price for product {product.id}: {str(price_error)}")
                            price = product.price  # Fallback to default price
                    else:
                        price = product.price  # Fallback to default price
                else:
                    price = product.price  # Default price
                
                # Get purchase_price from product model
                try:
                    purchase_price = float(product.purchase_price) if hasattr(product, 'purchase_price') and product.purchase_price is not None else 0.0
                except (ValueError, TypeError, AttributeError):
                    purchase_price = 0.0
                
                # Safely get all product fields with try-except for each
                try:
                    product_data = {
                        'id': product.id if hasattr(product, 'id') else 0,
                        'name': getattr(product, 'name', '') or '',
                        'description': getattr(product, 'description', '') or '',
                        'image_url': getattr(product, 'image_url', '') or '',
                        'price': float(price) if price is not None else 0.0,
                        'default_price': float(getattr(product, 'price', 0)) if getattr(product, 'price', None) is not None else 0.0,
                        'stock_quantity': getattr(product, 'stock_quantity', 0) if getattr(product, 'stock_quantity', None) is not None else 0,
                        'has_custom_price': customer_id and price != getattr(product, 'price', 0) if customer_id else False,
                        'is_active': getattr(product, 'is_active', True) if getattr(product, 'is_active', None) is not None else True,
                        'sku': getattr(product, 'sku', '') or '',
                        'category': getattr(product, 'category', '') or '',
                        'purchase_price': purchase_price,
                        'hsn_code': getattr(product, 'hsn_code', '') or '',
                        'brand': getattr(product, 'brand', '') or '',
                        'gst_rate': float(getattr(product, 'gst_rate', 18)) if getattr(product, 'gst_rate', None) is not None else 18.0,
                        'min_stock_level': getattr(product, 'min_stock_level', 10) if getattr(product, 'min_stock_level', None) is not None else 10
                    }
                except Exception as field_error:
                    print(f"Error creating product_data dict for product {getattr(product, 'id', 'unknown')}: {str(field_error)}")
                    # Create minimal product data
                    product_data = {
                        'id': getattr(product, 'id', 0),
                        'name': str(getattr(product, 'name', 'Unknown')),
                        'description': '',
                        'image_url': '',
                        'price': 0.0,
                        'default_price': 0.0,
                        'stock_quantity': 0,
                        'has_custom_price': False,
                        'is_active': True,
                        'sku': '',
                        'category': '',
                        'purchase_price': 0.0,
                        'hsn_code': '',
                        'brand': '',
                        'gst_rate': 18.0,
                        'min_stock_level': 10
                    }
                products_data.append(product_data)
                print(f"Product: ID={product.id}, Name={product.name}, SKU={product.sku}, Price={price}, Default Price={product.price}, Stock={product.stock_quantity}")
            except Exception as product_error:
                print(f"Error processing product {product.id}: {str(product_error)}")
                import traceback
                traceback.print_exc()
                # Skip this product but continue with others
                continue
        
        print(f"Returning {len(products_data)} products")
        return jsonify({'success': True, 'products': products_data})
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in products API: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return jsonify({
            'success': False, 
            'error': str(e),
            'message': f'Failed to load products: {str(e)}'
        }), 500

@product_bp.route('/', methods=['OPTIONS'])
def api_create_product_options():
    """Handle CORS preflight for product creation"""
    return '', 200

@product_bp.route('/', methods=['POST'])
@login_required
def api_create_product():
    """Create new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Product name is required'}), 400
        if not data.get('price'):
            return jsonify({'success': False, 'error': 'Product price is required'}), 400
        
        # Auto-generate SKU if not provided
        sku = data.get('sku')
        if not sku:
            # Generate SKU from product name and timestamp
            name_part = re.sub(r'[^A-Z0-9]', '', data['name'].upper())[:10] or 'PROD'
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')[-8:]  # Last 8 digits
            sku = f"{name_part}-{timestamp}"
            
            # Ensure SKU is unique
            counter = 1
            original_sku = sku
            user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
            while db['products'].find_one({'sku': sku, 'user_id': user_id_obj}):
                sku = f"{original_sku}-{counter}"
                counter += 1
        
        # Check if SKU already exists (if provided)
        user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        if data.get('sku') and db['products'].find_one({'sku': sku, 'user_id': user_id_obj}):
            return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        product = Product(
            user_id=current_user.id,
            admin_id=current_user.id,  # Set admin_id to same as user_id for backward compatibility
            name=data['name'],
            description=data.get('description', ''),
            sku=sku,
            hsn_code=data.get('hsn_code', ''),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            price=float(data['price']),
            purchase_price=float(data.get('purchase_price', 0)) if data.get('purchase_price') is not None else 0.0,
            gst_rate=float(data.get('gst_rate', 18)),
            stock_quantity=int(data.get('stock_quantity', 0)),
            min_stock_level=int(data.get('min_stock_level', 10)),
            unit=data.get('unit', 'PCS'),
            image_url=data.get('image_url', ''),
            weight=float(data.get('weight', 0)) if data.get('weight') else None,
            dimensions=data.get('dimensions', ''),
            vegetable_name=data.get('vegetable_name', ''),
            vegetable_name_hindi=data.get('vegetable_name_hindi', ''),
            quantity_gm=float(data.get('quantity_gm')) if data.get('quantity_gm') is not None else None,
            quantity_kg=float(data.get('quantity_kg')) if data.get('quantity_kg') is not None else None,
            rate_per_gm=float(data.get('rate_per_gm')) if data.get('rate_per_gm') is not None else None,
            rate_per_kg=float(data.get('rate_per_kg')) if data.get('rate_per_kg') is not None else None,
            is_active=data.get('is_active', True)
        )
        
        product.save()
        
        # Add initial stock movement if stock quantity > 0
        if data.get('stock_quantity', 0) > 0:
            movement = StockMovement(
                product_id=product.id,
                movement_type='in',
                quantity=data['stock_quantity'],
                reference='Initial stock',
                notes='Initial stock entry'
            )
            movement.save()
        
        return jsonify({
            'success': True, 
            'message': 'Product created successfully',
            'product': {
                'id': product.id,
                'name': product.name,
                'sku': product.sku
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Customer Product Pricing Routes - Must be defined before /<int:id> routes
@product_bp.route('/customer-prices', methods=['GET'])
@login_required
def api_get_customer_prices():
    """Get all customer-specific prices for products"""
    try:
        customer_id = request.args.get('customer_id', type=int)
        product_id = request.args.get('product_id', type=int)
        
        # Get customers for this user first
        customer_ids = [str(doc['_id']) for doc in db['customers'].find(
            {'user_id': ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id}
        )]
        
        query = {'customer_id': {'$in': [ObjectId(cid) if isinstance(cid, str) else cid for cid in customer_ids]}}
        
        if customer_id:
            query['customer_id'] = ObjectId(customer_id) if isinstance(customer_id, str) else customer_id
        if product_id:
            query['product_id'] = ObjectId(product_id) if isinstance(product_id, str) else product_id
        
        prices = [CustomerProductPrice.from_dict(doc) for doc in db['customer_product_prices'].find(query)]
        
        prices_data = []
        for price in prices:
            prices_data.append({
                'id': price.id,
                'customer_id': price.customer_id,
                'customer_name': price.customer.name if price.customer else 'Unknown',
                'product_id': price.product_id,
                'product_name': price.product.name if price.product else 'Unknown',
                'price': float(price.price),
                'created_at': price.created_at.isoformat() if price.created_at else None,
                'updated_at': price.updated_at.isoformat() if price.updated_at else None
            })
        
        return jsonify({'success': True, 'prices': prices_data})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/customer-prices', methods=['POST', 'OPTIONS'])
@login_required
def api_set_customer_price():
    """Set or update customer-specific price for a product"""
    # Handle OPTIONS for CORS preflight
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
            
        customer_id = data.get('customer_id')
        product_id = data.get('product_id')
        price = data.get('price')
        
        # Convert to integers to ensure proper type
        try:
            customer_id = int(customer_id) if customer_id is not None else None
            product_id = int(product_id) if product_id is not None else None
            price = float(price) if price is not None else None
        except (ValueError, TypeError) as e:
            return jsonify({'success': False, 'error': f'Invalid data types: {str(e)}'}), 400
        
        if not all([customer_id, product_id, price is not None]):
            return jsonify({'success': False, 'error': 'customer_id, product_id, and price are required'}), 400
        
        # First, verify customer exists (check if it belongs to this admin or any admin)
        customer = Customer.find_by_id(customer_id)
        if not customer:
            # Get all customers for debugging
            all_customers = [Customer.from_dict(doc) for doc in db['customers'].find()]
            customer_ids = [c.id for c in all_customers]
            return jsonify({
                'success': False, 
                'error': f'Customer not found. Customer ID: {customer_id}. Available customer IDs: {customer_ids}'
            }), 404
        
        # Verify product belongs to this admin
        user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        product = Product.find_by_id(product_id)
        if not product or str(product.user_id) != str(current_user.id):
            # Get all products for debugging
            all_products = [Product.from_dict(doc) for doc in db['products'].find({'user_id': user_id_obj})]
            product_ids = [p.id for p in all_products]
            return jsonify({
                'success': False, 
                'error': f'Product not found or does not belong to you. Product ID: {product_id}. Your product IDs: {product_ids}'
            }), 404
        
        # If customer belongs to a different admin, that's okay - we can still set prices
        # The important thing is that the product belongs to the current admin
        
        # Check if price already exists
        customer_price = CustomerProductPrice.find_by_customer_and_product(customer_id, product_id)
        
        if customer_price:
            # Update existing price
            customer_price.price = float(price)
            customer_price.updated_at = datetime.utcnow()
            customer_price.save()
        else:
            # Create new price
            customer_price = CustomerProductPrice(
                customer_id=customer_id,
                product_id=product_id,
                price=float(price)
            )
            customer_price.save()
        
        return jsonify({
            'success': True,
            'message': 'Customer price set successfully',
            'price': {
                'id': customer_price.id,
                'customer_id': customer_price.customer_id,
                'product_id': customer_price.product_id,
                'price': float(customer_price.price)
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>', methods=['GET'])
@login_required
def api_get_product(id):
    """Get single product"""
    try:
        product = Product.find_by_id(id)
        if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
            product = None
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        product_data = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'sku': product.sku,
            'hsn_code': product.hsn_code,
            'category': product.category,
            'brand': product.brand,
            'price': float(product.price),
            'gst_rate': float(product.gst_rate),
            'stock_quantity': product.stock_quantity,
            'min_stock_level': product.min_stock_level,
            'image_url': product.image_url,
            'weight': float(product.weight) if product.weight else 0,
            'dimensions': product.dimensions,
            'vegetable_name': product.vegetable_name,
            'vegetable_name_hindi': product.vegetable_name_hindi,
            'quantity_gm': float(product.quantity_gm) if product.quantity_gm else None,
            'quantity_kg': float(product.quantity_kg) if product.quantity_kg else None,
            'rate_per_gm': float(product.rate_per_gm) if product.rate_per_gm else None,
            'rate_per_kg': float(product.rate_per_kg) if product.rate_per_kg else None,
            'is_active': product.is_active,
            'created_at': product.created_at.isoformat() if product.created_at else None,
            'updated_at': product.updated_at.isoformat() if product.updated_at else None
        }
        
        return jsonify({'success': True, 'product': product_data})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>', methods=['PUT'])
@login_required
def api_update_product(id):
    """Update product"""
    try:
        # Don't filter by is_active so we can update inactive products too
        product = Product.find_by_id(id)
        if not product or str(product.user_id) != str(current_user.id):
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Check if SKU is changed and already exists
        if data.get('sku') != product.sku:
            user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
            if db['products'].find_one({'sku': data['sku'], 'user_id': user_id_obj}):
                return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        # Update product fields
        product.name = data.get('name', product.name)
        product.description = data.get('description', product.description)
        product.sku = data.get('sku', product.sku)
        product.hsn_code = data.get('hsn_code', product.hsn_code)
        product.category = data.get('category', product.category)
        product.brand = data.get('brand', product.brand)
        if 'price' in data:
            product.price = data['price']
        if 'purchase_price' in data:
            product.purchase_price = float(data['purchase_price']) if data['purchase_price'] is not None else 0.0
        product.gst_rate = data.get('gst_rate', product.gst_rate)
        product.min_stock_level = data.get('min_stock_level', product.min_stock_level)
        product.image_url = data.get('image_url', product.image_url)
        product.weight = data.get('weight', product.weight)
        product.dimensions = data.get('dimensions', product.dimensions)
        product.vegetable_name = data.get('vegetable_name', product.vegetable_name)
        product.vegetable_name_hindi = data.get('vegetable_name_hindi', product.vegetable_name_hindi)
        product.quantity_gm = float(data.get('quantity_gm')) if data.get('quantity_gm') is not None else product.quantity_gm
        product.quantity_kg = float(data.get('quantity_kg')) if data.get('quantity_kg') is not None else product.quantity_kg
        product.rate_per_gm = float(data.get('rate_per_gm')) if data.get('rate_per_gm') is not None else product.rate_per_gm
        product.rate_per_kg = float(data.get('rate_per_kg')) if data.get('rate_per_kg') is not None else product.rate_per_kg
        product.is_active = data.get('is_active', product.is_active)
        product.updated_at = datetime.utcnow()
        product.save()
        
        return jsonify({
            'success': True, 
            'message': 'Product updated successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>/toggle-visibility', methods=['POST'])
@login_required
def api_toggle_product_visibility(id):
    """Toggle product visibility (is_active)"""
    try:
        product = Product.find_by_id(id)
        if not product or str(product.user_id) != str(current_user.id):
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Toggle is_active
        product.is_active = not product.is_active
        product.updated_at = datetime.utcnow()
        product.save()
        
        return jsonify({
            'success': True,
            'message': f'Product {"activated" if product.is_active else "deactivated"} successfully',
            'is_active': product.is_active
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def api_delete_product(id):
    """Delete product (hard delete)"""
    try:
        product = Product.find_by_id(id)
        if not product or str(product.user_id) != str(current_user.id):
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        product_id_obj = ObjectId(id) if isinstance(id, str) else id
        
        # Check if product has invoice items
        invoice_item_count = db['invoice_items'].count_documents({'product_id': product_id_obj})
        if invoice_item_count > 0:
            return jsonify({
                'success': False, 
                'error': 'Cannot delete product with existing invoice items. Please delete related invoices first.'
            }), 400
        
            # Delete stock movements first
        db['stock_movements'].delete_many({'product_id': product_id_obj})
        
            # Delete customer prices first
        db['customer_product_prices'].delete_many({'product_id': product_id_obj})
        
        # Hard delete the product
        db['products'].delete_one({'_id': product_id_obj})
        
        return jsonify({
            'success': True, 
            'message': 'Product deleted successfully'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>/stock', methods=['POST'])
@login_required
def api_stock_movement(id):
    """Add stock movement"""
    try:
        product = Product.find_by_id(id)
        if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        movement = StockMovement(
            product_id=product.id,
            movement_type=data['movement_type'],
            quantity=data['quantity'],
            reference=data.get('reference', ''),
            notes=data.get('notes', '')
        )
        
        # Update product stock
        if data['movement_type'] == 'in':
            product.stock_quantity += data['quantity']
        elif data['movement_type'] == 'out':
            if product.stock_quantity < data['quantity']:
                return jsonify({'success': False, 'error': 'Insufficient stock'}), 400
            product.stock_quantity -= data['quantity']
        else:  # adjustment
            product.stock_quantity = data['quantity']
        
        product.updated_at = datetime.utcnow()
        
        movement.save()
        
        return jsonify({
            'success': True, 
            'message': 'Stock movement recorded successfully',
            'new_stock': product.stock_quantity
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/bulk-stock', methods=['POST'])
@login_required
def api_bulk_stock_movement():
    """Bulk stock in/out for multiple products"""
    try:
        if not current_user or not hasattr(current_user, 'id'):
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        data = request.get_json()
        movement_type = data.get('movement_type')  # 'in' or 'out'
        items = data.get('items', [])  # List of {product_id, quantity}
        
        if movement_type not in ['in', 'out']:
            return jsonify({'success': False, 'error': 'Invalid movement type'}), 400
        
        if not items or len(items) == 0:
            return jsonify({'success': False, 'error': 'No items provided'}), 400
        
        results = []
        errors = []
        
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 0)
            
            if not product_id or quantity <= 0:
                errors.append(f"Invalid item: product_id={product_id}, quantity={quantity}")
                continue
            
            try:
                product = Product.find_by_id(product_id)
                if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
                    product = None
                
                if not product:
                    errors.append(f"Product {product_id} not found")
                    continue
                
                # Check stock for stock out
                if movement_type == 'out' and product.stock_quantity < quantity:
                    errors.append(f"Insufficient stock for {product.name}. Available: {product.stock_quantity}, Requested: {quantity}")
                    continue
                
                # Create stock movement
                movement = StockMovement(
                    product_id=product.id,
                    movement_type=movement_type,
                    quantity=quantity,
                    reference=data.get('reference', 'Bulk operation'),
                    notes=data.get('notes', f'Bulk stock {movement_type}')
                )
                
                # Update product stock
                if movement_type == 'in':
                    product.stock_quantity += quantity
                else:  # out
                    product.stock_quantity -= quantity
                
                product.updated_at = datetime.utcnow()
                product.save()
                movement.save()
                
                results.append({
                    'product_id': product_id,
                    'product_name': product.name,
                    'new_stock': product.stock_quantity
                })
                
            except Exception as e:
                errors.append(f"Error processing product {product_id}: {str(e)}")
                continue
        
        return jsonify({
            'success': True,
            'message': f'Bulk stock {movement_type} completed',
            'processed': len(results),
            'results': results,
            'errors': errors
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in bulk stock API: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/upload-image', methods=['POST'])
@login_required
def api_upload_image():
    """Upload product image"""
    try:
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file:
            # Generate unique filename
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4().hex}_{filename}"
            
            # Create upload directory if it doesn't exist
            upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_dir, unique_filename)
            file.save(file_path)
            
            # Return the URL
            image_url = f"/static/uploads/products/{unique_filename}"
            
            return jsonify({
                'success': True, 
                'image_url': image_url,
                'filename': unique_filename
            })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/stock-movements', methods=['GET'])
@login_required
def api_get_stock_movements():
    """Get stock movements for purchases report"""
    try:
        if not current_user or not hasattr(current_user, 'id'):
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        user_id = current_user.id
        movement_type = request.args.get('movement_type', '')  # 'in' or 'out' or empty for all
        
        # Get all products for this user
        user_id_obj = ObjectId(user_id) if isinstance(user_id, str) else user_id
        products = [Product.from_dict(doc) for doc in db['products'].find({'user_id': user_id_obj, 'is_active': True})]
        product_ids = [ObjectId(p.id) if isinstance(p.id, str) else p.id for p in products]
        
        if not product_ids:
            return jsonify({'success': True, 'movements': []})
        
        # Query stock movements
        query = {'product_id': {'$in': product_ids}}
        
        if movement_type:
            query['movement_type'] = movement_type
        
        movements = [StockMovement.from_dict(doc) for doc in db['stock_movements'].find(query).sort('created_at', -1)]
        
        movements_data = []
        for movement in movements:
            movements_data.append({
                'id': movement.id,
                'product_id': movement.product_id,
                'movement_type': movement.movement_type,
                'quantity': movement.quantity,
                'reference': movement.reference or '',
                'notes': movement.notes or '',
                'created_at': movement.created_at.isoformat() if movement.created_at else None
            })
        
        return jsonify({
            'success': True,
            'movements': movements_data
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in stock movements API: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/inventory', methods=['GET'])
@login_required
def api_get_inventory():
    """Get optimized inventory overview with summary calculations"""
    try:
        # Check if user is authenticated
        if not current_user or not hasattr(current_user, 'id'):
            return jsonify({'success': False, 'error': 'User not authenticated'}), 401
        
        user_id = current_user.id
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        # Build optimized query - only get necessary fields
        query = {
            'user_id': ObjectId(user_id) if isinstance(user_id, str) else user_id,
            'is_active': True
        }
        
        if search:
            query['$or'] = [
                {'name': {'$regex': search, '$options': 'i'}},
                {'sku': {'$regex': search, '$options': 'i'}},
                {'hsn_code': {'$regex': search, '$options': 'i'}}
            ]
        
        if category and category != 'All' and category != '':
            query['category'] = category
        
        # Get products with optimized query
        products = [Product.from_dict(doc) for doc in db['products'].find(query).sort('name', 1)]
        
        # Calculate summary statistics efficiently
        low_stock_items = []
        positive_stock_items = []
        total_stock_value_sales = 0.0
        total_stock_value_purchase = 0.0
        low_stock_qty = 0
        positive_stock_qty = 0
        
        inventory_data = []
        
        # Get last updated dates in a single query for all products
        product_ids = [ObjectId(p.id) if isinstance(p.id, str) else p.id for p in products]
        last_movements = {}
        if product_ids:
            # Get the most recent movement for each product using aggregation
            pipeline = [
                {'$match': {'product_id': {'$in': product_ids}}},
                {'$group': {
                    '_id': '$product_id',
                    'last_updated': {'$max': '$created_at'}
                }}
            ]
            recent_movements = db['stock_movements'].aggregate(pipeline)
            
            for movement in recent_movements:
                product_id_str = str(movement['_id'])
                last_movements[product_id_str] = movement['last_updated']
        
        for product in products:
            stock_qty = product.stock_quantity if product.stock_quantity is not None else 0
            price = float(product.price) if product.price is not None else 0.0
            purchase_price = float(product.purchase_price) if product.purchase_price is not None else 0.0
            
            # Calculate stock values
            stock_value_sales = stock_qty * price
            stock_value_purchase = stock_qty * purchase_price
            
            # Track low stock (negative or below min level)
            if stock_qty < 0 or (stock_qty > 0 and stock_qty <= product.min_stock_level):
                low_stock_items.append(product.id)
                low_stock_qty += stock_qty
            
            # Track positive stock
            if stock_qty > 0:
                positive_stock_items.append(product.id)
                positive_stock_qty += stock_qty
            
            total_stock_value_sales += stock_value_sales
            total_stock_value_purchase += stock_value_purchase
            
            # Get last updated date
            last_updated = last_movements.get(product.id)
            if not last_updated and product.updated_at:
                last_updated = product.updated_at
            
            inventory_data.append({
                'id': product.id,
                'name': product.name or '',
                'vegetable_name_hindi': getattr(product, 'vegetable_name_hindi', '') or '',
                'sku': product.sku or '',
                'category': product.category or '',
                'stock_quantity': stock_qty,
                'min_stock_level': product.min_stock_level if product.min_stock_level is not None else 10,
                'price': price,
                'purchase_price': purchase_price,
                'unit': product.unit or 'PCS',
                'last_updated': last_updated.isoformat() if last_updated else None,
                'status': 'out_of_stock' if stock_qty == 0 else 
                         'low_stock' if stock_qty < 0 or (stock_qty > 0 and stock_qty <= product.min_stock_level) else 'in_stock'
            })
        
        return jsonify({
            'success': True,
            'inventory': inventory_data,
            'summary': {
                'low_stock': {
                    'items': len(low_stock_items),
                    'quantity': low_stock_qty
                },
                'positive_stock': {
                    'items': len(positive_stock_items),
                    'quantity': positive_stock_qty
                },
                'stock_value_sales_price': float(total_stock_value_sales),
                'stock_value_purchase_price': float(total_stock_value_purchase),
                'total_products': len(products)
            }
        })
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in inventory API: {str(e)}")
        print(f"Full traceback:\n{error_trace}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Legacy template routes (keeping for compatibility)
@product_bp.route('/products')
@login_required
def index():
    """List all products"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = {
        'user_id': ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id,
        'is_active': True
    }
    
    if search:
        query['$or'] = [
            {'name': {'$regex': search, '$options': 'i'}},
            {'sku': {'$regex': search, '$options': 'i'}},
            {'hsn_code': {'$regex': search, '$options': 'i'}}
        ]
    
    if category:
        query['category'] = category
    
    # Manual pagination for MongoDB
    skip = (page - 1) * 20
    all_products = [Product.from_dict(doc) for doc in db['products'].find(query).sort('name', 1).skip(skip).limit(20)]
    total_count = db['products'].count_documents(query)
    
    # Create pagination-like object
    class Pagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
    
    products = Pagination(all_products, page, 20, total_count)
    
    return render_template('products/index.html', products=products, search=search, category=category)

@product_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new product"""
    form = ProductForm()
    
    if form.validate_on_submit():
        # Check if SKU already exists
        user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        if db['products'].find_one({'sku': form.sku.data, 'user_id': user_id_obj}):
            flash('SKU already exists. Please choose a different SKU.', 'error')
            return render_template('products/new.html', form=form)
        
        product = Product(
            user_id=current_user.id,
            admin_id=current_user.id,  # Set admin_id to same as user_id for backward compatibility
            name=form.name.data,
            sku=form.sku.data,
            hsn_code=form.hsn_code.data,
            description=form.description.data,
            price=form.price.data,
            gst_rate=form.gst_rate.data,
            stock_quantity=form.stock_quantity.data,
            min_stock_level=form.min_stock_level.data,
            unit=form.unit.data
        )
        
        product.save()
        
        # Add initial stock movement
        if form.stock_quantity.data > 0:
            movement = StockMovement(
                product_id=product.id,
                movement_type='in',
                quantity=form.stock_quantity.data,
                reference='Initial stock',
                notes='Initial stock entry'
            )
            movement.save()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('product.index'))
    
    return render_template('products/new.html', form=form)

@product_bp.route('/products/<int:id>')
@login_required
def show(id):
    """Show product details"""
    product = Product.find_by_id(id)
    if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
        from flask import abort
        abort(404)
    
    # Get recent stock movements
    product_id_obj = ObjectId(product.id) if isinstance(product.id, str) else product.id
    movements = [StockMovement.from_dict(doc) for doc in db['stock_movements'].find(
        {'product_id': product_id_obj}
    ).sort('created_at', -1).limit(10)]
    
    return render_template('products/show.html', product=product, movements=movements)

@product_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit product"""
    product = Product.find_by_id(id)
    if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
        from flask import abort
        abort(404)
    
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        # Check if SKU is changed and already exists
        if form.sku.data != product.sku:
            user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
            if db['products'].find_one({'sku': form.sku.data, 'user_id': user_id_obj}):
                flash('SKU already exists. Please choose a different SKU.', 'error')
                return render_template('products/edit.html', form=form, product=product)
        
        product.name = form.name.data
        product.sku = form.sku.data
        product.hsn_code = form.hsn_code.data
        product.description = form.description.data
        product.price = form.price.data
        product.gst_rate = form.gst_rate.data
        product.min_stock_level = form.min_stock_level.data
        product.unit = form.unit.data
        product.save()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product.show', id=product.id))
    
    return render_template('products/edit.html', form=form, product=product)

@product_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete product (hard delete)"""
    product = Product.find_by_id(id)
    if not product or str(product.user_id) != str(current_user.id):
        from flask import abort
        abort(404)
    
    product_id_obj = ObjectId(id) if isinstance(id, str) else id
    
    # Check if product has invoice items
    invoice_item_count = db['invoice_items'].count_documents({'product_id': product_id_obj})
    if invoice_item_count > 0:
        flash('Cannot delete product with existing invoice items. Please delete invoices first.', 'error')
        return redirect(url_for('product.show', id=product.id))
    
    # Delete stock movements first
    db['stock_movements'].delete_many({'product_id': product_id_obj})
    
    # Delete customer prices first
    db['customer_product_prices'].delete_many({'product_id': product_id_obj})
    
    # Hard delete the product
    db['products'].delete_one({'_id': product_id_obj})
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product.index'))

@product_bp.route('/products/<int:id>/stock', methods=['GET', 'POST'])
@login_required
def stock_movement(id):
    """Add stock movement"""
    product = Product.find_by_id(id)
    if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
        from flask import abort
        abort(404)
    
    form = StockMovementForm()
    
    if form.validate_on_submit():
        movement = StockMovement(
            product_id=product.id,
            movement_type=form.movement_type.data,
            quantity=form.quantity.data,
            reference=form.reference.data,
            notes=form.notes.data
        )
        
        # Update product stock
        if form.movement_type.data == 'in':
            product.stock_quantity += form.quantity.data
        elif form.movement_type.data == 'out':
            if product.stock_quantity < form.quantity.data:
                flash('Insufficient stock!', 'error')
                return render_template('products/stock_movement.html', form=form, product=product)
            product.stock_quantity -= form.quantity.data
        else:  # adjustment
            product.stock_quantity = form.quantity.data
        
        movement.save()
        
        flash('Stock movement recorded successfully!', 'success')
        return redirect(url_for('product.show', id=product.id))
    
    return render_template('products/stock_movement.html', form=form, product=product)

@product_bp.route('/inventory')
@login_required
def inventory():
    """Inventory overview"""
    user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
    products = [Product.from_dict(doc) for doc in db['products'].find(
        {'user_id': user_id_obj, 'is_active': True}
    ).sort('name', 1)]
    
    # Calculate inventory summary
    total_products = len(products)
    total_value = sum(p.stock_quantity * p.price for p in products)
    low_stock_count = len([p for p in products if p.is_low_stock])
    out_of_stock_count = len([p for p in products if p.stock_quantity == 0])
    
    return render_template('products/inventory.html', 
                         products=products,
                         total_products=total_products,
                         total_value=total_value,
                         low_stock_count=low_stock_count,
                         out_of_stock_count=out_of_stock_count)

@product_bp.route('/search')
@login_required
def search():
    """API endpoint for product search (for invoice creation)"""
    search_term = request.args.get('q', '')
    
    if len(search_term) < 2:
        return jsonify([])
    
    user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
    query = {
        'user_id': user_id_obj,
        'is_active': True,
        '$or': [
            {'name': {'$regex': search_term, '$options': 'i'}},
            {'sku': {'$regex': search_term, '$options': 'i'}},
            {'hsn_code': {'$regex': search_term, '$options': 'i'}}
        ]
    }
    products = [Product.from_dict(doc) for doc in db['products'].find(query).limit(10)]
    
    results = []
    for product in products:
        results.append({
            'id': product.id,
            'name': product.name,
            'sku': product.sku,
            'price': float(product.price),
            'gst_rate': float(product.gst_rate),
            'stock_quantity': product.stock_quantity,
            'unit': product.unit
        })
    
    return jsonify(results)

@product_bp.route('/<int:id>')
@login_required
def get_product(id):
    """API endpoint to get product details"""
    product = Product.find_by_id(id)
    if not product or str(product.user_id) != str(current_user.id) or not product.is_active:
        from flask import abort
        abort(404)
    
    customer_id = request.args.get('customer_id', type=int)
    price = product.get_customer_price(customer_id) if customer_id else product.price
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'hsn_code': product.hsn_code,
        'price': float(price),
        'default_price': float(product.price),
        'gst_rate': float(product.gst_rate),
        'stock_quantity': product.stock_quantity,
        'unit': product.unit,
        'description': product.description
    })

# Customer Product Pricing Routes moved to before /<int:id> routes (see above)

@product_bp.route('/customer-prices/<int:price_id>', methods=['DELETE'])
@login_required
def api_delete_customer_price(price_id):
    """Delete customer-specific price"""
    try:
        # Get customer IDs for this user
        user_id_obj = ObjectId(current_user.id) if isinstance(current_user.id, str) else current_user.id
        customer_ids = [str(doc['_id']) for doc in db['customers'].find({'user_id': user_id_obj})]
        
        # Find price that belongs to one of these customers
        price_id_obj = ObjectId(price_id) if isinstance(price_id, str) else price_id
        customer_price_doc = db['customer_product_prices'].find_one({
            '_id': price_id_obj,
            'customer_id': {'$in': [ObjectId(cid) if isinstance(cid, str) else cid for cid in customer_ids]}
        })
        
        if not customer_price_doc:
            return jsonify({'success': False, 'error': 'Price not found'}), 404
        
        db['customer_product_prices'].delete_one({'_id': price_id_obj})
        
        return jsonify({'success': True, 'message': 'Customer price deleted successfully'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
