from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, Customer, Order, OrderItem, Product, Invoice, InvoiceItem
from datetime import datetime, timedelta
import uuid

admin_bp = Blueprint('admin', __name__)

# Customer Management Routes
@admin_bp.route('/customers', methods=['GET'])
@login_required
def get_customers():
    """Get all customers for the current admin"""
    try:
        customers = Customer.query.filter_by(user_id=current_user.id).all()
        customers_data = []
        
        for customer in customers:
            customers_data.append({
                'id': customer.id,
                'name': customer.name,
                'email': customer.email,
                'phone': customer.phone,
                'billing_address': customer.billing_address,
                'state': customer.state,
                'pincode': customer.pincode,
                'created_at': customer.created_at.isoformat(),
                'is_active': customer.is_active
            })
        
        return jsonify({'success': True, 'customers': customers_data})
    
    except Exception as e:
        print(f"Error getting customers: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/customers', methods=['POST'])
@login_required
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        # Check if customer with same email already exists
        existing_customer = Customer.query.filter_by(email=data['email']).first()
        if existing_customer:
            return jsonify({'success': False, 'error': 'Customer with this email already exists'}), 400
        
        # Create new customer
        customer = Customer(
            user_id=current_user.id,
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            billing_address=data['billing_address'],
            gstin='',  # Default empty GSTIN
            state=data['state'],
            pincode=data['pincode']
        )
        customer.set_password(data['password'])
        
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
        db.session.rollback()
        print(f"Error creating customer: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/customers/<int:customer_id>', methods=['DELETE'])
@login_required
def delete_customer(customer_id):
    """Delete a customer"""
    try:
        customer = Customer.query.filter_by(id=customer_id, user_id=current_user.id).first()
        
        if not customer:
            return jsonify({'success': False, 'error': 'Customer not found'}), 404
        
        db.session.delete(customer)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Customer deleted successfully'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting customer: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Order Management Routes
@admin_bp.route('/orders', methods=['GET'])
@login_required
def get_orders():
    """Get all orders for the current admin"""
    try:
        # Get orders from customers belonging to this admin
        orders = Order.query.join(Customer).filter(Customer.user_id == current_user.id).order_by(Order.created_at.desc()).all()
        orders_data = []
        
        for order in orders:
            # Get customer details
            customer = Customer.query.get(order.customer_id)
            
            # Get order items
            items_data = []
            for item in order.items:
                items_data.append({
                    'id': item.id,
                    'product_id': item.product_id,
                    'product_name': item.product.name if item.product else 'Unknown Product',
                    'quantity': item.quantity,
                    'unit_price': float(item.unit_price),
                    'total': float(item.total)
                })
            
            orders_data.append({
                'id': order.id,
                'order_number': order.order_number,
                'customer_id': order.customer_id,
                'customer_name': customer.name if customer else 'Unknown Customer',
                'customer_email': customer.email if customer else '',
                'customer_phone': customer.phone if customer else '',
                'order_date': order.order_date.isoformat() if order.order_date else '',
                'status': order.status,
                'total_amount': float(order.total_amount),
                'notes': order.notes,
                'items': items_data,
                'created_at': order.created_at.isoformat()
            })
        
        return jsonify({'success': True, 'orders': orders_data})
    
    except Exception as e:
        print(f"Error getting orders: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
@login_required
def update_order_status(order_id):
    """Update order status"""
    try:
        data = request.get_json()
        new_status = data.get('status')
        
        if not new_status:
            return jsonify({'success': False, 'error': 'Status is required'}), 400
        
        # Get order from customers belonging to this admin
        order = Order.query.join(Customer).filter(Order.id == order_id, Customer.user_id == current_user.id).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        order.status = new_status
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Order status updated successfully'})
    
    except Exception as e:
        db.session.rollback()
        print(f"Error updating order status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/orders/<int:order_id>/generate-invoice', methods=['POST'])
@login_required
def generate_invoice_from_order(order_id):
    """Generate an invoice from an order"""
    try:
        # Get order from customers belonging to this admin
        order = Order.query.join(Customer).filter(Order.id == order_id, Customer.user_id == current_user.id).first()
        
        if not order:
            return jsonify({'success': False, 'error': 'Order not found'}), 404
        
        # Check if invoice already exists for this order
        existing_invoice = Invoice.query.filter_by(order_id=order_id).first()
        if existing_invoice:
            return jsonify({'success': False, 'error': 'Invoice already exists for this order'}), 400
        
        # Generate invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Create invoice
        invoice = Invoice(
            user_id=current_user.id,
            customer_id=order.customer_id,
            invoice_number=invoice_number,
            invoice_date=datetime.now().date(),
            due_date=(datetime.now() + timedelta(days=30)).date(),  # 30 days from now
            subtotal=order.total_amount,
            total_amount=order.total_amount,
            status='pending',
            notes=f"Invoice generated from order {order.order_number}",
            order_id=order_id  # Link to the original order
        )
        
        db.session.add(invoice)
        db.session.flush()  # Get invoice ID
        
        # Add invoice items from order items
        for order_item in order.items:
            # Calculate GST (assuming 18% for now)
            gst_rate = 18.0
            item_total = order_item.quantity * order_item.unit_price
            gst_amount = item_total * (gst_rate / 100)
            
            invoice_item = InvoiceItem(
                invoice_id=invoice.id,
                product_id=order_item.product_id,
                quantity=order_item.quantity,
                unit_price=order_item.unit_price,
                gst_rate=gst_rate,
                gst_amount=gst_amount,
                total=item_total
            )
            db.session.add(invoice_item)
        
        # Calculate invoice totals
        invoice.calculate_totals()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Invoice generated successfully',
            'invoice': {
                'id': invoice.id,
                'invoice_number': invoice.invoice_number,
                'total_amount': float(invoice.total_amount)
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Error generating invoice: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500
