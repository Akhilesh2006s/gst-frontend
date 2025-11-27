from flask import Blueprint, render_template, request, flash, redirect, url_for, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from models import User
from forms import LoginForm, RegistrationForm, ProfileForm
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/')
def index():
    """Landing page - bypassed for now"""
    return jsonify({
        'success': True,
        'message': 'Landing page bypassed for development'
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    """Admin login"""
    try:
        data = request.get_json()
        
        user = User.find_by_email(data['email'])
        if user and user.check_password(data['password']):
            # Auto-approve legacy users if needed
            if not user.is_approved:
                user.is_approved = True
                user.save()
            
            login_user(user, remember=data.get('remember_me', False))
            session.permanent = True
            
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
            return jsonify({'success': False, 'message': 'Invalid email or password'}), 401
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Admin registration"""
    try:
        data = request.get_json()
        
        # Check if username or email already exists
        if User.find_by_username(data.get('name', '')):
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        if User.find_by_email(data['email']):
            return jsonify({'success': False, 'message': 'Email already registered'}), 400
        
         # Create new admin user (auto-approved)
        user = User(
            username=data.get('name', data['email']),
            email=data['email'],
            business_name=data.get('business_name', 'My Business'),
            gst_number=data.get('gst_number', '00AAAAA0000A1Z5'),
            business_address=data.get('business_address', 'Business Address'),
            business_phone=data.get('business_phone', '1234567890'),
            business_email=data['email'],
            business_state=data.get('business_state', 'Delhi'),
            business_pincode=data.get('business_pincode', '110001'),
             business_reason=data.get('business_reason', 'Business reason not provided'),
             is_approved=True
        )
        user.set_password(data['password'])
        user.save()
        
        return jsonify({
            'success': True,
            'message': 'Registration successful! Please login.',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'business_name': user.business_name
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@auth_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    """User logout"""
    try:
        logout_user()
        session.clear()
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })
    except Exception as e:
        return jsonify({
            'success': True,
            'message': 'Logout successful'
        })

@auth_bp.route('/profile', methods=['GET', 'POST'])
def profile():
    """User profile management - bypassed for now"""
    return jsonify({
        'success': True,
        'message': 'Profile management bypassed for development',
        'user': {
            'id': 1,
            'username': 'demo',
            'email': 'demo@example.com',
            'business_name': 'Demo Business'
        }
    })

@auth_bp.route('/check', methods=['GET'])
def check_auth():
    """Check if user is authenticated and return user type"""
    try:
        if current_user.is_authenticated:
            # Determine user type
            if hasattr(current_user, 'is_super_admin') and current_user.is_super_admin:
                user_type = 'super_admin'
            elif hasattr(current_user, 'is_admin') and current_user.is_admin:
                user_type = 'admin'
            else:
                user_type = 'customer'
            
            return jsonify({
                'authenticated': True,
                'user_type': user_type,
                'user_id': current_user.id
            })
        else:
            return jsonify({
                'authenticated': False,
                'user_type': None
            })
    except Exception as e:
        return jsonify({
            'authenticated': False,
            'user_type': None,
            'error': str(e)
        }), 500

def is_valid_gst(gst_number):
    """Validate GST number format"""
    # GST number should be 15 characters: 2 digits + 10 digits + 1 digit + 1 digit + 1 digit
    pattern = r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$'
    return bool(re.match(pattern, gst_number))

