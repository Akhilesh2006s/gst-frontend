from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify, send_file
from flask_login import login_required, current_user
from models import db, Invoice, InvoiceItem, GSTReport
from sqlalchemy import func, extract
from datetime import datetime, date
import calendar
import json
from pdf_generator import generate_gst_report_pdf

gst_bp = Blueprint('gst', __name__)

@gst_bp.route('/gst')
@login_required
def index():
    """GST dashboard"""
    # Get current month and year
    now = datetime.now()
    current_month = now.month
    current_year = now.year
    
    # Get GST summary for current month
    gst_summary = db.session.query(
        func.sum(Invoice.subtotal).label('total_taxable_value'),
        func.sum(Invoice.cgst_amount).label('total_cgst'),
        func.sum(Invoice.sgst_amount).label('total_sgst'),
        func.sum(Invoice.igst_amount).label('total_igst'),
        func.count(Invoice.id).label('total_invoices')
    ).filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == current_month,
        extract('year', Invoice.invoice_date) == current_year,
        Invoice.status == 'paid'
    ).first()
    
    # Get GST summary by rate
    gst_by_rate = db.session.query(
        InvoiceItem.gst_rate,
        func.sum(InvoiceItem.total).label('taxable_value'),
        func.sum(InvoiceItem.gst_amount).label('gst_amount'),
        func.count(InvoiceItem.id).label('item_count')
    ).join(Invoice).filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == current_month,
        extract('year', Invoice.invoice_date) == current_year,
        Invoice.status == 'paid'
    ).group_by(InvoiceItem.gst_rate).all()
    
    # Get recent GST reports
    recent_reports = GSTReport.query.filter_by(
        user_id=current_user.id
    ).order_by(GSTReport.created_at.desc()).limit(5).all()
    
    return render_template('gst/index.html', 
                         gst_summary=gst_summary,
                         gst_by_rate=gst_by_rate,
                         recent_reports=recent_reports,
                         current_month=current_month,
                         current_year=current_year)

@gst_bp.route('/gst/gstr1')
@login_required
def gstr1():
    """Generate GSTR-1 report"""
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get invoices for the specified month
    invoices = Invoice.query.filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == month,
        extract('year', Invoice.invoice_date) == year,
        Invoice.status == 'paid'
    ).all()
    
    # Group by GST rate
    gst_data = {}
    for invoice in invoices:
        for item in invoice.items:
            rate = item.gst_rate
            if rate not in gst_data:
                gst_data[rate] = {
                    'taxable_value': 0,
                    'cgst': 0,
                    'sgst': 0,
                    'igst': 0,
                    'invoices': []
                }
            
            gst_data[rate]['taxable_value'] += item.total
            gst_data[rate]['cgst'] += item.gst_amount / 2 if invoice.cgst_amount > 0 else 0
            gst_data[rate]['sgst'] += item.gst_amount / 2 if invoice.sgst_amount > 0 else 0
            gst_data[rate]['igst'] += item.gst_amount if invoice.igst_amount > 0 else 0
            
            if invoice.id not in [inv['id'] for inv in gst_data[rate]['invoices']]:
                gst_data[rate]['invoices'].append({
                    'id': invoice.id,
                    'invoice_number': invoice.invoice_number,
                    'invoice_date': invoice.invoice_date,
                    'customer_name': invoice.customer.name,
                    'customer_gstin': invoice.customer.gstin,
                    'total_amount': invoice.total_amount
                })
    
    return render_template('gst/gstr1.html', 
                         gst_data=gst_data,
                         month=month,
                         year=year,
                         month_name=calendar.month_name[month])

@gst_bp.route('/gst/gstr3b')
@login_required
def gstr3b():
    """Generate GSTR-3B report"""
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get invoices for the specified month
    invoices = Invoice.query.filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == month,
        extract('year', Invoice.invoice_date) == year,
        Invoice.status == 'paid'
    ).all()
    
    # Calculate totals
    total_taxable_value = sum(invoice.subtotal for invoice in invoices)
    total_cgst = sum(invoice.cgst_amount for invoice in invoices)
    total_sgst = sum(invoice.sgst_amount for invoice in invoices)
    total_igst = sum(invoice.igst_amount for invoice in invoices)
    total_gst = total_cgst + total_sgst + total_igst
    
    # Group by GST rate
    gst_by_rate = {}
    for invoice in invoices:
        for item in invoice.items:
            rate = item.gst_rate
            if rate not in gst_by_rate:
                gst_by_rate[rate] = {
                    'taxable_value': 0,
                    'gst_amount': 0
                }
            
            gst_by_rate[rate]['taxable_value'] += item.total
            gst_by_rate[rate]['gst_amount'] += item.gst_amount
    
    return render_template('gst/gstr3b.html',
                         invoices=invoices,
                         total_taxable_value=total_taxable_value,
                         total_cgst=total_cgst,
                         total_sgst=total_sgst,
                         total_igst=total_igst,
                         total_gst=total_gst,
                         gst_by_rate=gst_by_rate,
                         month=month,
                         year=year,
                         month_name=calendar.month_name[month])

@gst_bp.route('/gst/reports')
@login_required
def reports():
    """List all GST reports"""
    reports = GSTReport.query.filter_by(
        user_id=current_user.id
    ).order_by(GSTReport.created_at.desc()).all()
    
    return render_template('gst/reports.html', reports=reports)

@gst_bp.route('/gst/reports/generate', methods=['POST'])
@login_required
def generate_report():
    """Generate and save GST report"""
    report_type = request.form.get('report_type')
    month = int(request.form.get('month'))
    year = int(request.form.get('year'))
    
    if report_type not in ['GSTR1', 'GSTR3B']:
        flash('Invalid report type', 'error')
        return redirect(url_for('gst.reports'))
    
    # Check if report already exists
    existing_report = GSTReport.query.filter_by(
        user_id=current_user.id,
        report_type=report_type,
        period_month=month,
        period_year=year
    ).first()
    
    if existing_report:
        flash('Report for this period already exists', 'error')
        return redirect(url_for('gst.reports'))
    
    # Get invoices for the period
    invoices = Invoice.query.filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == month,
        extract('year', Invoice.invoice_date) == year,
        Invoice.status == 'paid'
    ).all()
    
    # Calculate totals
    total_taxable_value = sum(invoice.subtotal for invoice in invoices)
    total_cgst = sum(invoice.cgst_amount for invoice in invoices)
    total_sgst = sum(invoice.sgst_amount for invoice in invoices)
    total_igst = sum(invoice.igst_amount for invoice in invoices)
    
    # Prepare report data
    report_data = {
        'invoices': [
            {
                'invoice_number': invoice.invoice_number,
                'invoice_date': invoice.invoice_date.strftime('%Y-%m-%d'),
                'customer_name': invoice.customer.name,
                'customer_gstin': invoice.customer.gstin,
                'subtotal': float(invoice.subtotal),
                'cgst': float(invoice.cgst_amount),
                'sgst': float(invoice.sgst_amount),
                'igst': float(invoice.igst_amount),
                'total': float(invoice.total_amount)
            }
            for invoice in invoices
        ]
    }
    
    # Create report record
    report = GSTReport(
        user_id=current_user.id,
        report_type=report_type,
        period_month=month,
        period_year=year,
        total_taxable_value=total_taxable_value,
        total_cgst=total_cgst,
        total_sgst=total_sgst,
        total_igst=total_igst,
        report_data=report_data
    )
    
    db.session.add(report)
    db.session.commit()
    
    flash(f'{report_type} report generated successfully!', 'success')
    return redirect(url_for('gst.reports'))

@gst_bp.route('/gst/reports/<int:id>')
@login_required
def show_report(id):
    """Show GST report details"""
    report = GSTReport.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()
    
    return render_template('gst/show_report.html', report=report)

@gst_bp.route('/gst/reports/<int:id>/pdf')
@login_required
def download_report_pdf(id):
    """Download GST report as PDF"""
    report = GSTReport.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()
    
    # Generate PDF
    pdf_path = generate_gst_report_pdf(report)
    
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f'{report.report_type}_{report.period_month:02d}_{report.period_year}.pdf',
        mimetype='application/pdf'
    )

@gst_bp.route('/gst/reports/<int:id>/delete', methods=['POST'])
@login_required
def delete_report(id):
    """Delete GST report"""
    report = GSTReport.query.filter_by(
        id=id, user_id=current_user.id
    ).first_or_404()
    
    db.session.delete(report)
    db.session.commit()
    
    flash('Report deleted successfully!', 'success')
    return redirect(url_for('gst.reports'))

@gst_bp.route('/api/gst/summary')
@login_required
def gst_summary():
    """API endpoint for GST summary data"""
    month = request.args.get('month', datetime.now().month, type=int)
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Get GST summary for the specified month
    summary = db.session.query(
        func.sum(Invoice.subtotal).label('total_taxable_value'),
        func.sum(Invoice.cgst_amount).label('total_cgst'),
        func.sum(Invoice.sgst_amount).label('total_sgst'),
        func.sum(Invoice.igst_amount).label('total_igst'),
        func.count(Invoice.id).label('total_invoices')
    ).filter(
        Invoice.user_id == current_user.id,
        extract('month', Invoice.invoice_date) == month,
        extract('year', Invoice.invoice_date) == year,
        Invoice.status == 'paid'
    ).first()
    
    return jsonify({
        'total_taxable_value': float(summary.total_taxable_value or 0),
        'total_cgst': float(summary.total_cgst or 0),
        'total_sgst': float(summary.total_sgst or 0),
        'total_igst': float(summary.total_igst or 0),
        'total_invoices': summary.total_invoices or 0
    })

