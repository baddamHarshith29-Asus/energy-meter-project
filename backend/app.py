from flask import Flask
from flask_cors import CORS
from database import db
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///energy.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    from routes import api
    app.register_blueprint(api, url_prefix='/api')
    
    with app.app_context():
        import models
        # Only create tables if they don't exist
        db.create_all()
        
    @app.route('/api/health')
    def health_check():
        return {"status": "healthy"}, 200
        
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
