#!/usr/bin/env python3
"""
Deployment script for GST Billing System
"""

import os
import sys
from app import create_app, db
from models import User, Customer, Product, SuperAdmin

def init_database():
    """Initialize database and create tables"""
    app = create_app('production')
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create super admin if not exists
        super_admin = SuperAdmin.query.filter_by(email='admin@gstbilling.com').first()
        if not super_admin:
            super_admin = SuperAdmin(
                email='admin@gstbilling.com',
                password='admin123'  # Change this in production!
            )
            super_admin.set_password('admin123')
            db.session.add(super_admin)
            db.session.commit()
            print("✅ Super admin created: admin@gstbilling.com / admin123")
        
        print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_database()
