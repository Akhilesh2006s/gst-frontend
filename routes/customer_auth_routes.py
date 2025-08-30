from flask import Blueprint, request, jsonify, session
from flask_login import login_user, logout_user, login_required, current_user
from models import db, Customer, User
from forms import CustomerRegistrationForm, CustomerLoginForm, ForgotPasswordForm, ResetPasswordForm
import re
import secrets
import string

customer_auth_bp = Blueprint('customer_auth', __name__)

@customer_auth_bp.route('/register', methods=['POST'])
def register():
    """Customer registration"""
    try:
        data = request.get_json()
        
        # Check if email already exists
        if Customer.query.filter_by(email=data['email']).first():
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
        # Create new customer (assuming admin user_id = 1 for now)
        customer = Customer(
            user_id=1,  # Default admin user
            name=data['name'],
            email=data['email'],
            phone=data['phone'],
            gstin=data.get('gstin'),
            billing_address=data['billing_address'],
            shipping_address=data.get('shipping_address'),
            state=data['state'],
            pincode=data['pincode']
        )
        customer.set_password(data['password'])
        
        db.session.add(customer)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please login.',
            'customer': {
                'id': customer.id,
                'name': customer.name,
                'email': customer.email
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@customer_auth_bp.route('/login', methods=['POST'])
def login():
    """Customer login"""
    try:
        data = request.get_json()
        
        customer = Customer.query.filter_by(email=data['email']).first()
        if customer and customer.check_password(data['password']):
            login_user(customer, remember=data.get('remember_me', False))
            session.permanent = True
            
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

@customer_auth_bp.route('/logout')
@login_required
def logout():
    """Customer logout"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'})

@customer_auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    """Forgot password - send reset email"""
    try:
        data = request.get_json()
        email = data['email']
        
        customer = Customer.query.filter_by(email=email).first()
        if not customer:
            return jsonify({'success': False, 'message': 'Email not found'}), 404
        
        # Generate reset token (in production, send email with reset link)
        reset_token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        session['reset_token'] = reset_token
        session['reset_email'] = email
        
        # For now, just return success (in production, send email)
        return jsonify({
            'success': True,
            'message': 'Password reset instructions sent to your email',
            'reset_token': reset_token  # Remove this in production
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@customer_auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    try:
        data = request.get_json()
        reset_token = data.get('reset_token')
        new_password = data['password']
        
        # Verify reset token
        if reset_token != session.get('reset_token'):
            return jsonify({'success': False, 'message': 'Invalid reset token'}), 400
        
        email = session.get('reset_email')
        customer = Customer.query.filter_by(email=email).first()
        
        if not customer:
            return jsonify({'success': False, 'message': 'Customer not found'}), 404
        
        # Update password
        customer.set_password(new_password)
        db.session.commit()
        
        # Clear session
        session.pop('reset_token', None)
        session.pop('reset_email', None)
        
        return jsonify({'success': True, 'message': 'Password reset successful'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@customer_auth_bp.route('/profile')
@login_required
def profile():
    """Get customer profile"""
    return jsonify({
        'success': True,
        'customer': {
            'id': current_user.id,
            'name': current_user.name,
            'email': current_user.email,
            'phone': current_user.phone,
            'gstin': current_user.gstin,
            'billing_address': current_user.billing_address,
            'shipping_address': current_user.shipping_address,
            'state': current_user.state,
            'pincode': current_user.pincode
        }
    })

