from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from models import db, Invoice, InvoiceItem, Product, Customer, StockMovement
from sqlalchemy import func, extract, desc
from datetime import datetime, date, timedelta
import calendar
import json
from pdf_generator import generate_sales_report_pdf

report_bp = Blueprint('report', __name__)

@report_bp.route('/reports')
@login_required
def index():
    """Reports dashboard"""
    return render_template('reports/index.html')

@report_bp.route('/reports/sales')
@login_required
def sales():
    """Sales report"""
    report_type = request.args.get('type', 'monthly')
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    date_from = request.args.get('date_from', '')
    date_to = request.args.get('date_to', '')
    
    if report_type == 'monthly':
        # Monthly report
        invoices = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            extract('month', Invoice.invoice_date) == month,
            extract('year', Invoice.invoice_date) == year,
            Invoice.status == 'paid'
        ).all()
    else:
        # Date range report
        if not date_from or not date_to:
            flash('Please select date range', 'error')
            return render_template('reports/sales.html', invoices=[], report_type=report_type)
        
        start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        
        invoices = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            Invoice.invoice_date >= start_date,
            Invoice.invoice_date <= end_date,
            Invoice.status == 'paid'
        ).all()
    
    # Calculate totals
    total_sales = sum(invoice.total_amount for invoice in invoices)
    total_invoices = len(invoices)
    total_gst = sum(invoice.cgst_amount + invoice.sgst_amount + invoice.igst_amount for invoice in invoices)
    
    # Top customers
    customer_sales = {}
    for invoice in invoices:
        customer_name = invoice.customer.name
        if customer_name not in customer_sales:
            customer_sales[customer_name] = 0
        customer_sales[customer_name] += invoice.total_amount
    
    top_customers = sorted(customer_sales.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Top products
    product_sales = {}
    for invoice in invoices:
        for item in invoice.items:
            product_name = item.product.name
            if product_name not in product_sales:
                product_sales[product_name] = {'quantity': 0, 'amount': 0}
            product_sales[product_name]['quantity'] += item.quantity
            product_sales[product_name]['amount'] += item.total
    
    top_products = sorted(product_sales.items(), key=lambda x: x[1]['amount'], reverse=True)[:10]
    
    return render_template('reports/sales.html',
                         invoices=invoices,
                         total_sales=total_sales,
                         total_invoices=total_invoices,
                         total_gst=total_gst,
                         top_customers=top_customers,
                         top_products=top_products,
                         report_type=report_type,
                         month=month,
                         year=year,
                         date_from=date_from,
                         date_to=date_to)

@report_bp.route('/reports/inventory')
@login_required
def inventory():
    """Inventory report"""
    products = Product.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).order_by(Product.name).all()
    
    # Calculate inventory summary
    total_products = len(products)
    total_value = sum(p.stock_quantity * p.price for p in products)
    low_stock_count = len([p for p in products if p.is_low_stock])
    out_of_stock_count = len([p for p in products if p.stock_quantity == 0])
    
    # Get recent stock movements
    recent_movements = StockMovement.query.join(Product).filter(
        Product.user_id == current_user.id
    ).order_by(desc(StockMovement.created_at)).limit(20).all()
    
    # Stock movement summary
    movement_summary = db.session.query(
        StockMovement.movement_type,
        func.sum(StockMovement.quantity).label('total_quantity')
    ).join(Product).filter(
        Product.user_id == current_user.id,
        StockMovement.created_at >= datetime.now() - timedelta(days=30)
    ).group_by(StockMovement.movement_type).all()
    
    return render_template('reports/inventory.html',
                         products=products,
                         total_products=total_products,
                         total_value=total_value,
                         low_stock_count=low_stock_count,
                         out_of_stock_count=out_of_stock_count,
                         recent_movements=recent_movements,
                         movement_summary=movement_summary)

@report_bp.route('/reports/customers')
@login_required
def customers():
    """Customer report"""
    customers = Customer.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    # Calculate customer statistics
    customer_stats = []
    for customer in customers:
        invoices = customer.invoices
        total_purchases = sum(invoice.total_amount for invoice in invoices if invoice.status == 'paid')
        total_invoices = len([invoice for invoice in invoices if invoice.status == 'paid'])
        last_purchase = max([invoice.invoice_date for invoice in invoices if invoice.status == 'paid']) if invoices else None
        
        customer_stats.append({
            'customer': customer,
            'total_purchases': total_purchases,
            'total_invoices': total_invoices,
            'last_purchase': last_purchase,
            'average_order': total_purchases / total_invoices if total_invoices > 0 else 0
        })
    
    # Sort by total purchases
    customer_stats.sort(key=lambda x: x['total_purchases'], reverse=True)
    
    return render_template('reports/customers.html', customer_stats=customer_stats)

@report_bp.route('/reports/products')
@login_required
def products():
    """Product performance report"""
    products = Product.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    # Calculate product performance
    product_stats = []
    for product in products:
        # Get sales data for last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        sales_data = db.session.query(
            func.sum(InvoiceItem.quantity).label('total_sold'),
            func.sum(InvoiceItem.total).label('total_revenue'),
            func.count(InvoiceItem.id).label('times_sold')
        ).join(Invoice).filter(
            InvoiceItem.product_id == product.id,
            Invoice.user_id == current_user.id,
            Invoice.invoice_date >= thirty_days_ago,
            Invoice.status == 'paid'
        ).first()
        
        # Get stock movements
        movements = StockMovement.query.filter_by(product_id=product.id).all()
        stock_in = sum(m.quantity for m in movements if m.movement_type == 'in')
        stock_out = sum(m.quantity for m in movements if m.movement_type == 'out')
        
        product_stats.append({
            'product': product,
            'total_sold': sales_data.total_sold or 0,
            'total_revenue': sales_data.total_revenue or 0,
            'times_sold': sales_data.times_sold or 0,
            'stock_in': stock_in,
            'stock_out': stock_out,
            'current_stock': product.stock_quantity,
            'stock_value': product.stock_quantity * product.price
        })
    
    # Sort by revenue
    product_stats.sort(key=lambda x: x['total_revenue'], reverse=True)
    
    return render_template('reports/products.html', product_stats=product_stats)

@report_bp.route('/reports/analytics')
@login_required
def analytics():
    """Business analytics"""
    # Sales trend for last 12 months
    sales_trend = []
    for i in range(12):
        month = datetime.now().month - i
        year = datetime.now().year
        if month <= 0:
            month += 12
            year -= 1
        
        sales = db.session.query(
            func.sum(Invoice.total_amount).label('total_sales')
        ).filter(
            Invoice.user_id == current_user.id,
            extract('month', Invoice.invoice_date) == month,
            extract('year', Invoice.invoice_date) == year,
            Invoice.status == 'paid'
        ).scalar() or 0
        
        sales_trend.append({
            'month': calendar.month_abbr[month],
            'sales': float(sales)
        })
    
    sales_trend.reverse()
    
    # Top performing metrics
    # Best selling product
    best_product = db.session.query(
        Product.name,
        func.sum(InvoiceItem.quantity).label('total_sold')
    ).join(InvoiceItem).join(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status == 'paid'
    ).group_by(Product.id, Product.name).order_by(
        desc(func.sum(InvoiceItem.quantity))
    ).first()
    
    # Best customer
    best_customer = db.session.query(
        Customer.name,
        func.sum(Invoice.total_amount).label('total_spent')
    ).join(Invoice).filter(
        Invoice.user_id == current_user.id,
        Invoice.status == 'paid'
    ).group_by(Customer.id, Customer.name).order_by(
        desc(func.sum(Invoice.total_amount))
    ).first()
    
    # Monthly growth
    current_month_sales = db.session.query(
        func.sum(Invoice.total_amount).label('total_sales')
    ).filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == datetime.now().month,
        extract('year', Invoice.invoice_date) == datetime.now().year,
        Invoice.status == 'paid'
    ).scalar() or 0
    
    last_month_sales = db.session.query(
        func.sum(Invoice.total_amount).label('total_sales')
    ).filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == datetime.now().month - 1,
        extract('year', Invoice.invoice_date) == datetime.now().year,
        Invoice.status == 'paid'
    ).scalar() or 0
    
    growth_percentage = ((current_month_sales - last_month_sales) / last_month_sales * 100) if last_month_sales > 0 else 0
    
    return render_template('reports/analytics.html',
                         sales_trend=sales_trend,
                         best_product=best_product,
                         best_customer=best_customer,
                         current_month_sales=current_month_sales,
                         last_month_sales=last_month_sales,
                         growth_percentage=growth_percentage)

@report_bp.route('/reports/export/<report_type>')
@login_required
def export_report(report_type):
    """Export report as PDF"""
    if report_type == 'sales':
        month = request.args.get('month', datetime.now().month, type=int)
        year = request.args.get('year', datetime.now().year, type=int)
        
        invoices = Invoice.query.filter(
            Invoice.user_id == current_user.id,
            extract('month', Invoice.invoice_date) == month,
            extract('year', Invoice.invoice_date) == year,
            Invoice.status == 'paid'
        ).all()
        
        pdf_path = generate_sales_report_pdf(invoices, month, year)
        
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f'sales_report_{month:02d}_{year}.pdf',
            mimetype='application/pdf'
        )
    
    flash('Invalid report type', 'error')
    return redirect(url_for('report.index'))

@report_bp.route('/api/reports/sales-data')
@login_required
def sales_data():
    """API endpoint for sales chart data"""
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now() - timedelta(days=days)
    
    # Get daily sales data
    daily_sales = db.session.query(
        func.date(Invoice.invoice_date).label('date'),
        func.sum(Invoice.total_amount).label('sales')
    ).filter(
        Invoice.user_id == current_user.id,
        Invoice.invoice_date >= start_date,
        Invoice.status == 'paid'
    ).group_by(func.date(Invoice.invoice_date)).all()
    
    # Format data for chart
    chart_data = []
    for sale in daily_sales:
        chart_data.append({
            'date': sale.date.strftime('%Y-%m-%d'),
            'sales': float(sale.sales)
        })
    
    return jsonify(chart_data)

@report_bp.route('/api/reports/inventory-data')
@login_required
def inventory_data():
    """API endpoint for inventory chart data"""
    products = Product.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    chart_data = []
    for product in products:
        chart_data.append({
            'name': product.name,
            'stock_quantity': product.stock_quantity,
            'stock_value': float(product.stock_quantity * product.price)
        })
    
    return jsonify(chart_data)

