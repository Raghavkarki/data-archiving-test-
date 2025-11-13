"""Configuration settings for the application"""
import os

class Config:
    """Base configuration"""
    # Flask Secret Key - MUST be set in .env file
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError(
            "SECRET_KEY must be set in .env file. "
            "Please copy .env.example to .env and set your SECRET_KEY."
        )
    
    # CouchDB Configuration
    COUCHDB_URL = os.environ.get('COUCHDB_URL')
    COUCHDB_USERNAME = os.environ.get('COUCHDB_USERNAME')
    COUCHDB_PASSWORD = os.environ.get('COUCHDB_PASSWORD')
    
    if not all([COUCHDB_URL, COUCHDB_USERNAME, COUCHDB_PASSWORD]):
        raise ValueError(
            "CouchDB credentials must be set in .env file. "
            "Required: COUCHDB_URL, COUCHDB_USERNAME, COUCHDB_PASSWORD. "
            "Please copy .env.example to .env and configure your credentials."
        )
    
    # Authentication
    VALID_USERNAME = os.environ.get('ADMIN_USERNAME')
    VALID_PASSWORD = os.environ.get('ADMIN_PASSWORD')
    
    if not all([VALID_USERNAME, VALID_PASSWORD]):
        raise ValueError(
            "Admin credentials must be set in .env file. "
            "Required: ADMIN_USERNAME, ADMIN_PASSWORD. "
            "Please copy .env.example to .env and configure your credentials."
        )
    
    # File paths (relative to project root)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    LOG_FILE = os.path.join(BASE_DIR, 'data', 'deletion_logs.csv')
    TOMBSTONE_DATA_DIR = os.path.join(BASE_DIR, 'tombstone_data')
    LOGS_DIR = os.path.join(BASE_DIR, 'logs')
    
    # Logging configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Form name mappings
    FORM_NAME_MAPPING = {
        "u2_registry": "U2 Registry",
        "anc_monitoring": "ANC Monitoring-old",
        "anc_monitoring_form": "ANC Monitoring-new", 
        "pregnancy_screening_form": "Pregnancy Screening Form",
        "epds_module_5": "EPDS Module 5",
        "epds_module_1": "EPDS Module 1",
        "epds_module_2": "EPDS Module 2",
        "post_delivery_form": "Post Delivery Form",
        "epds_screening": "EPDS Screening",
    }

