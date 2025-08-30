from flask import Flask, jsonify, request
from flask_cors import CORS
import os

def create_app():
    app = Flask(__name__)
    
    # Basic configuration
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///app.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Enable CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "supports_credentials": True,
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Health check endpoints
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'message': 'GST Billing System API is running'})
    
    @app.route('/')
    def root():
        return jsonify({'status': 'healthy', 'message': 'GST Billing System API is running'})
    
    # Test API endpoints
    @app.route('/api/test')
    def test_api():
        return jsonify({'message': 'API is working!'})
    
    @app.route('/api/super-admin/login', methods=['POST'])
    def super_admin_login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            # Simple test response
            if email == 'admin@gstbilling.com' and password == 'admin123':
                return jsonify({
                    'success': True,
                    'message': 'Login successful!',
                    'super_admin': {
                        'id': 1,
                        'name': 'Super Admin',
                        'email': email
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    def auth_login():
        try:
            data = request.get_json()
            email = data.get('email')
            password = data.get('password')
            
            # Simple test response
            if email == 'admin@gstbilling.com' and password == 'admin123':
                return jsonify({
                    'success': True,
                    'message': 'Login successful!',
                    'user': {
                        'id': 1,
                        'username': 'admin',
                        'email': email
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid credentials'}), 401
                
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
    
    return app

# Create the app instance
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
