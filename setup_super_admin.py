#!/usr/bin/env python3
"""
Setup script to create the super admin
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from models import db, SuperAdmin

def create_super_admin():
    """Create the super admin user"""
    app = create_app()
    
    with app.app_context():
        # Check if super admin already exists
        existing_super_admin = SuperAdmin.query.filter_by(email='akhileshsamayamanthula@gmail.com').first()
        
        if existing_super_admin:
            print("Super admin already exists!")
            return
        
        # Create super admin
        super_admin = SuperAdmin(
            email='akhileshsamayamanthula@gmail.com',
            name='Akhilesh Samayamanthula'
        )
        super_admin.set_password('Akhilesh')
        
        db.session.add(super_admin)
        db.session.commit()
        
        print("Super admin created successfully!")
        print("Email: akhileshsamayamanthula@gmail.com")
        print("Password: Akhilesh")

if __name__ == '__main__':
    create_super_admin()


