from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from models import db, Invoice, Product, Customer, StockMovement
from sqlalchemy import func, desc
from datetime import datetime, timedelta
import calendar

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
@login_required
def index():
    """Main dashboard page"""
    # Get current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Sales summary for current month
    monthly_sales = db.session.query(
        func.sum(Invoice.total_amount).label('total_sales'),
        func.count(Invoice.id).label('total_invoices'),
        func.sum(Invoice.cgst_amount + Invoice.sgst_amount + Invoice.igst_amount).label('total_gst')
    ).filter(
        Invoice.user_id == current_user.id,
        func.extract('month', Invoice.invoice_date) == current_month,
        func.extract('year', Invoice.invoice_date) == current_year,
        Invoice.status == 'paid'
    ).first()
    
    # Inventory summary
    inventory_summary = db.session.query(
        func.count(Product.id).label('total_products'),
        func.sum(Product.stock_quantity * Product.price).label('stock_value'),
        func.count(Product.id).filter(Product.is_low_stock).label('low_stock_count')
    ).filter(
        Product.user_id == current_user.id,
        Product.is_active == True
    ).first()
    
    # Customer count
    customer_count = Customer.query.filter_by(
        user_id=current_user.id, 
        is_active=True
    ).count()
    
    # Recent invoices
    recent_invoices = Invoice.query.filter_by(
        user_id=current_user.id
    ).order_by(desc(Invoice.created_at)).limit(5).all()
    
    # Low stock products
    low_stock_products = Product.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).filter(
        Product.stock_quantity <= Product.min_stock_level
    ).limit(5).all()
    
    # Top selling products (last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    top_products = db.session.query(
        Product.name,
        func.sum(InvoiceItem.quantity).label('total_sold')
    ).join(InvoiceItem).join(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.invoice_date >= thirty_days_ago,
        Invoice.status == 'paid'
    ).group_by(Product.id, Product.name).order_by(
        desc(func.sum(InvoiceItem.quantity))
    ).limit(5).all()
    
    dashboard_data = {
        'monthly_sales': monthly_sales.total_sales or 0,
        'total_invoices': monthly_sales.total_invoices or 0,
        'total_gst': monthly_sales.total_gst or 0,
        'total_products': inventory_summary.total_products or 0,
        'stock_value': inventory_summary.stock_value or 0,
        'low_stock_count': inventory_summary.low_stock_count or 0,
        'customer_count': customer_count,
        'recent_invoices': recent_invoices,
        'low_stock_products': low_stock_products,
        'top_products': top_products
    }
    
    return render_template('dashboard/index.html', data=dashboard_data)

@dashboard_bp.route('/api/sales-chart')
@login_required
def sales_chart():
    """API endpoint for sales chart data"""
    # Get sales data for last 12 months
    now = datetime.now()
    sales_data = []
    
    for i in range(12):
        month = now.month - i
        year = now.year
        if month <= 0:
            month += 12
            year -= 1
        
        sales = db.session.query(
            func.sum(Invoice.total_amount).label('total_sales')
        ).filter(
            Invoice.user_id == current_user.id,
            func.extract('month', Invoice.invoice_date) == month,
            func.extract('year', Invoice.invoice_date) == year,
            Invoice.status == 'paid'
        ).scalar() or 0
        
        sales_data.append({
            'month': calendar.month_abbr[month],
            'sales': float(sales)
        })
    
    # Reverse to show oldest to newest
    sales_data.reverse()
    
    return jsonify(sales_data)

@dashboard_bp.route('/api/inventory-chart')
@login_required
def inventory_chart():
    """API endpoint for inventory chart data"""
    # Get products with their stock values
    products = Product.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    inventory_data = []
    for product in products:
        inventory_data.append({
            'name': product.name,
            'stock_value': float(product.stock_quantity * product.price),
            'stock_quantity': product.stock_quantity
        })
    
    # Sort by stock value and take top 10
    inventory_data.sort(key=lambda x: x['stock_value'], reverse=True)
    inventory_data = inventory_data[:10]
    
    return jsonify(inventory_data)

@dashboard_bp.route('/api/recent-activity')
@login_required
def recent_activity():
    """API endpoint for recent activity"""
    # Get recent invoices
    recent_invoices = Invoice.query.filter_by(
        user_id=current_user.id
    ).order_by(desc(Invoice.created_at)).limit(10).all()
    
    # Get recent stock movements
    recent_movements = StockMovement.query.join(Product).filter(
        Product.user_id == current_user.id
    ).order_by(desc(StockMovement.created_at)).limit(10).all()
    
    activity_data = []
    
    # Add invoices to activity
    for invoice in recent_invoices:
        activity_data.append({
            'type': 'invoice',
            'message': f'Invoice {invoice.invoice_number} created for {invoice.customer.name}',
            'amount': float(invoice.total_amount),
            'date': invoice.created_at.strftime('%Y-%m-%d %H:%M'),
            'status': invoice.status
        })
    
    # Add stock movements to activity
    for movement in recent_movements:
        activity_data.append({
            'type': 'stock',
            'message': f'{movement.movement_type.title()} {movement.quantity} units of {movement.product.name}',
            'quantity': movement.quantity,
            'date': movement.created_at.strftime('%Y-%m-%d %H:%M'),
            'reference': movement.reference
        })
    
    # Sort by date and take most recent 15
    activity_data.sort(key=lambda x: x['date'], reverse=True)
    activity_data = activity_data[:15]
    
    return jsonify(activity_data)

