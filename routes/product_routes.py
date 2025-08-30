from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, current_app
from flask_login import login_required, current_user
from models import db, Product, StockMovement
from forms import ProductForm, StockMovementForm
from sqlalchemy import or_
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

product_bp = Blueprint('product', __name__)

# API Routes for React Frontend
@product_bp.route('/inventory/add', methods=['POST'])
@login_required
def api_add_to_inventory():
    """Add a new product to inventory"""
    try:
        data = request.get_json()
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=data['sku'], user_id=current_user.id).first():
            return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        product = Product(
            user_id=current_user.id,
            name=data['name'],
            description=data.get('description', ''),
            sku=data['sku'],
            hsn_code=data.get('hsn_code', ''),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            price=data['price'],
            gst_rate=data.get('gst_rate', 18),
            stock_quantity=data.get('stock_quantity', 0),
            min_stock_level=data.get('min_stock_level', 10),
            image_url=data.get('image_url', ''),
            weight=data.get('weight', 0),
            dimensions=data.get('dimensions', ''),
            is_active=True
        )
        
        db.session.add(product)
        db.session.commit()
        
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
            db.session.add(movement)
            db.session.commit()
        
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
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/', methods=['GET'])
@login_required
def api_get_products():
    """Get products from inventory (limited fields for products page)"""
    try:
        print(f"Products API called by user: {current_user.id}")
        search = request.args.get('search', '')
        category = request.args.get('category', '')
        
        # Only get products that are in inventory (have stock or are active)
        query = Product.query.filter_by(user_id=current_user.id, is_active=True)
        
        if search:
            query = query.filter(
                or_(
                    Product.name.contains(search),
                    Product.sku.contains(search),
                    Product.hsn_code.contains(search)
                )
            )
        
        if category and category != 'All':
            query = query.filter(Product.category == category)
        
        products = query.order_by(Product.name).all()
        print(f"Found {len(products)} products for user {current_user.id}")
        
        # Return only the fields needed for products page
        products_data = []
        for product in products:
            product_data = {
                'id': product.id,
                'name': product.name,
                'image_url': product.image_url,
                'price': float(product.price),
                'stock_quantity': product.stock_quantity
            }
            products_data.append(product_data)
            print(f"Product: ID={product.id}, Name={product.name}, SKU={product.sku}, Price={product.price}, Stock={product.stock_quantity}")
        
        print(f"Returning {len(products_data)} products")
        return jsonify({'success': True, 'products': products_data})
    
    except Exception as e:
        print(f"Error in products API: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/', methods=['POST'])
@login_required
def api_create_product():
    """Create new product"""
    try:
        data = request.get_json()
        
        # Check if SKU already exists
        if Product.query.filter_by(sku=data['sku'], user_id=current_user.id).first():
            return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        product = Product(
            user_id=current_user.id,
            name=data['name'],
            description=data.get('description', ''),
            sku=data['sku'],
            hsn_code=data.get('hsn_code', ''),
            category=data.get('category', ''),
            brand=data.get('brand', ''),
            price=data['price'],
            gst_rate=data.get('gst_rate', 18),
            stock_quantity=data.get('stock_quantity', 0),
            min_stock_level=data.get('min_stock_level', 10),
            image_url=data.get('image_url', ''),
            weight=data.get('weight', 0),
            dimensions=data.get('dimensions', ''),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(product)
        db.session.commit()
        
        # Add initial stock movement if stock quantity > 0
        if data.get('stock_quantity', 0) > 0:
            movement = StockMovement(
                product_id=product.id,
                movement_type='in',
                quantity=data['stock_quantity'],
                reference='Initial stock',
                notes='Initial stock entry'
            )
            db.session.add(movement)
            db.session.commit()
        
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
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>', methods=['GET'])
@login_required
def api_get_product(id):
    """Get single product"""
    try:
        product = Product.query.filter_by(
            id=id, user_id=current_user.id, is_active=True
        ).first()
        
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
        product = Product.query.filter_by(
            id=id, user_id=current_user.id, is_active=True
        ).first()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        data = request.get_json()
        
        # Check if SKU is changed and already exists
        if data.get('sku') != product.sku:
            if Product.query.filter_by(sku=data['sku'], user_id=current_user.id).first():
                return jsonify({'success': False, 'error': 'SKU already exists'}), 400
        
        # Update product fields
        product.name = data['name']
        product.description = data.get('description', '')
        product.sku = data['sku']
        product.hsn_code = data.get('hsn_code', '')
        product.category = data.get('category', '')
        product.brand = data.get('brand', '')
        product.price = data['price']
        product.gst_rate = data.get('gst_rate', 18)
        product.min_stock_level = data.get('min_stock_level', 10)
        product.image_url = data.get('image_url', '')
        product.weight = data.get('weight', 0)
        product.dimensions = data.get('dimensions', '')
        product.is_active = data.get('is_active', True)
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Product updated successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>', methods=['DELETE'])
@login_required
def api_delete_product(id):
    """Delete product (soft delete)"""
    try:
        product = Product.query.filter_by(
            id=id, user_id=current_user.id, is_active=True
        ).first()
        
        if not product:
            return jsonify({'success': False, 'error': 'Product not found'}), 404
        
        # Check if product has invoice items
        if product.invoice_items:
            return jsonify({
                'success': False, 
                'error': 'Cannot delete product with existing invoice items'
            }), 400
        
        product.is_active = False
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Product deleted successfully'
        })
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@product_bp.route('/<int:id>/stock', methods=['POST'])
@login_required
def api_stock_movement(id):
    """Add stock movement"""
    try:
        product = Product.query.filter_by(
            id=id, user_id=current_user.id, is_active=True
        ).first()
        
        if not product:
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
        
        db.session.add(movement)
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': 'Stock movement recorded successfully',
            'new_stock': product.stock_quantity
        })
    
    except Exception as e:
        db.session.rollback()
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

@product_bp.route('/inventory', methods=['GET'])
@login_required
def api_get_inventory():
    """Get inventory overview"""
    try:
        products = Product.query.filter_by(
            user_id=current_user.id, is_active=True
        ).order_by(Product.name).all()
        
        # Calculate inventory summary
        total_products = len(products)
        total_value = sum(p.stock_quantity * p.price for p in products)
        low_stock_count = len([p for p in products if p.stock_quantity <= p.min_stock_level and p.stock_quantity > 0])
        out_of_stock_count = len([p for p in products if p.stock_quantity == 0])
        
        inventory_data = []
        for product in products:
            inventory_data.append({
                'id': product.id,
                'name': product.name,
                'sku': product.sku,
                'category': product.category,
                'stock_quantity': product.stock_quantity,
                'min_stock_level': product.min_stock_level,
                'price': float(product.price),
                'total_value': float(product.stock_quantity * product.price),
                'status': 'out_of_stock' if product.stock_quantity == 0 else 
                         'low_stock' if product.stock_quantity <= product.min_stock_level else 'in_stock'
            })
        
        return jsonify({
            'success': True,
            'inventory': inventory_data,
            'summary': {
                'total_products': total_products,
                'total_value': float(total_value),
                'low_stock_count': low_stock_count,
                'out_of_stock_count': out_of_stock_count
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Legacy template routes (keeping for compatibility)
@product_bp.route('/products')
@login_required
def index():
    """List all products"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    category = request.args.get('category', '')
    
    query = Product.query.filter_by(user_id=current_user.id, is_active=True)
    
    if search:
        query = query.filter(
            or_(
                Product.name.contains(search),
                Product.sku.contains(search),
                Product.hsn_code.contains(search)
            )
        )
    
    if category:
        query = query.filter(Product.category == category)
    
    products = query.order_by(Product.name).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('products/index.html', products=products, search=search, category=category)

@product_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def new():
    """Create new product"""
    form = ProductForm()
    
    if form.validate_on_submit():
        # Check if SKU already exists
        if Product.query.filter_by(sku=form.sku.data, user_id=current_user.id).first():
            flash('SKU already exists. Please choose a different SKU.', 'error')
            return render_template('products/new.html', form=form)
        
        product = Product(
            user_id=current_user.id,
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
        
        db.session.add(product)
        db.session.commit()
        
        # Add initial stock movement
        if form.stock_quantity.data > 0:
            movement = StockMovement(
                product_id=product.id,
                movement_type='in',
                quantity=form.stock_quantity.data,
                reference='Initial stock',
                notes='Initial stock entry'
            )
            db.session.add(movement)
            db.session.commit()
        
        flash('Product created successfully!', 'success')
        return redirect(url_for('product.index'))
    
    return render_template('products/new.html', form=form)

@product_bp.route('/products/<int:id>')
@login_required
def show(id):
    """Show product details"""
    product = Product.query.filter_by(
        id=id, user_id=current_user.id, is_active=True
    ).first_or_404()
    
    # Get recent stock movements
    movements = StockMovement.query.filter_by(
        product_id=product.id
    ).order_by(StockMovement.created_at.desc()).limit(10).all()
    
    return render_template('products/show.html', product=product, movements=movements)

@product_bp.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    """Edit product"""
    product = Product.query.filter_by(
        id=id, user_id=current_user.id, is_active=True
    ).first_or_404()
    
    form = ProductForm(obj=product)
    
    if form.validate_on_submit():
        # Check if SKU is changed and already exists
        if form.sku.data != product.sku:
            if Product.query.filter_by(sku=form.sku.data, user_id=current_user.id).first():
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
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('product.show', id=product.id))
    
    return render_template('products/edit.html', form=form, product=product)

@product_bp.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    """Delete product (soft delete)"""
    product = Product.query.filter_by(
        id=id, user_id=current_user.id, is_active=True
    ).first_or_404()
    
    # Check if product has invoice items
    if product.invoice_items:
        flash('Cannot delete product with existing invoice items. Please delete invoices first.', 'error')
        return redirect(url_for('product.show', id=product.id))
    
    product.is_active = False
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('product.index'))

@product_bp.route('/products/<int:id>/stock', methods=['GET', 'POST'])
@login_required
def stock_movement(id):
    """Add stock movement"""
    product = Product.query.filter_by(
        id=id, user_id=current_user.id, is_active=True
    ).first_or_404()
    
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
        
        db.session.add(movement)
        db.session.commit()
        
        flash('Stock movement recorded successfully!', 'success')
        return redirect(url_for('product.show', id=product.id))
    
    return render_template('products/stock_movement.html', form=form, product=product)

@product_bp.route('/inventory')
@login_required
def inventory():
    """Inventory overview"""
    products = Product.query.filter_by(
        user_id=current_user.id, is_active=True
    ).order_by(Product.name).all()
    
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
    
    products = Product.query.filter(
        Product.user_id == current_user.id,
        Product.is_active == True,
        or_(
            Product.name.contains(search_term),
            Product.sku.contains(search_term),
            Product.hsn_code.contains(search_term)
        )
    ).limit(10).all()
    
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
    product = Product.query.filter_by(
        id=id, user_id=current_user.id, is_active=True
    ).first_or_404()
    
    return jsonify({
        'id': product.id,
        'name': product.name,
        'sku': product.sku,
        'hsn_code': product.hsn_code,
        'price': float(product.price),
        'gst_rate': float(product.gst_rate),
        'stock_quantity': product.stock_quantity,
        'unit': product.unit,
        'description': product.description
    })
