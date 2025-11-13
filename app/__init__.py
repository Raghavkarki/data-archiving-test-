from flask import Flask
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    """Application factory pattern"""
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    # Load configuration
    from app.config import Config
    app.config.from_object(Config)
    
    # Register blueprints
    from app.routes.auth import auth_bp
    from app.routes.main import main_bp
    from app.routes.tombstone import tombstone_bp
    from app.routes.csv_mapper import csv_mapper_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(tombstone_bp)
    app.register_blueprint(csv_mapper_bp)
    
    return app

