from app import create_app, db
from models import User, Customer, Product, Invoice, InvoiceItem, StockMovement, GSTReport, SuperAdmin, Order, OrderItem

app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("All database tables created successfully!")
    
    # Check if super admin exists
    from models import SuperAdmin
    existing_super_admin = SuperAdmin.query.filter_by(email='akhileshsamayamanthula@gmail.com').first()
    
    if not existing_super_admin:
        # Create super admin
        super_admin = SuperAdmin(
            email='akhileshsamayamanthula@gmail.com',
            name='Akhilesh Samayamanthula'
        )
        super_admin.set_password('Akhilesh')
        db.session.add(super_admin)
        db.session.commit()
        print("Super admin created successfully!")
    else:
        print("Super admin already exists!")

