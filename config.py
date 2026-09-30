import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    """Base application configuration."""
    SECRET_KEY = os.getenv('SECRET_KEY', 'cybersec-bluetooth-secret-key-prod-2026-xyz')
    
    # MySQL is the primary target database, with SQLite fallback if MySQL is not configured
    DATABASE_URL = os.getenv(
        'DATABASE_URL',
        'mysql+pymysql://root:password@localhost:3306/bluetooth_security_db'
    )
    
    # If DATABASE_URL starts with sqlite: use as is, else keep MySQL URL
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 280,
        'pool_pre_ping': True,
    } if 'mysql' in DATABASE_URL else {}

    # Application settings
    DEMO_MODE_DEFAULT = os.getenv('DEMO_MODE_DEFAULT', 'True').lower() in ('true', '1', 't')
    REPORTS_DIR = os.path.join(basedir, 'generated_reports')
    
    # Session Configuration
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # Set to True if running behind HTTPS in production


class TestConfig(Config):
    """Test environment configuration with in-memory SQLite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SECRET_KEY = 'test-secret-key-12345'
