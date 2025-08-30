from flask_migrate import Migrate
from models import db

migrate = Migrate()

def init_app(app):
    """Initialize database with Flask app"""
    db.init_app(app)
    migrate.init_app(app, db)
    
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Import models to ensure they are registered
        from models import User, Customer, Product, Invoice, InvoiceItem, StockMovement, GSTReport
        
    return db

