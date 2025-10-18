import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:CassidyMadando16@db.amtfabgmtsujurppknfg.supabase.co:5432/postgres')
    DB_HOST = os.getenv('DB_HOST', 'db.amtfabgmtsujurppknfg.supabase.co')
    DB_NAME = os.getenv('DB_NAME', 'postgres')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'CassidyMadando16')
    DB_PORT = os.getenv('DB_PORT', '5432')
    
    # Application Settings
    SECRET_KEY = os.getenv('SECRET_KEY', '728495e15b6c5d935285eb079f7c78b99e6c2a7f6571e528aa7c52e0dbf4715d')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    APP_ENV = os.getenv('APP_ENV', 'development')
    
    # USSD Settings
    USSD_CODE = os.getenv('USSD_CODE', '*384*531#')
    COUNTRY_CODE = os.getenv('COUNTRY_CODE', 'ZM')
    
    # Africa's Talking
    AT_USERNAME = os.getenv('AT_USERNAME', 'sandbox')
    AT_API_KEY = os.getenv('AT_API_KEY', 'atsk_f74b6e4b9e0aa7ea82f7c0058d7315528f829f1993888ac1e696b031adb336daa6385c04')
    
    # Application URLs
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')
    
    # Session Settings
    SESSION_TIMEOUT_HOURS = 24
    
    # Pagination
    JOBS_PER_PAGE = 3
    APPLICATIONS_PER_PAGE = 5

class DevelopmentConfig(Config):
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    DEBUG = False
    TESTING = False

class TestingConfig(Config):
    TESTING = True
    DEBUG = True

def get_config():
    env = os.getenv('APP_ENV', 'development')
    configs = {
        'development': DevelopmentConfig,
        'production': ProductionConfig,
        'testing': TestingConfig
    }
    return configs.get(env, DevelopmentConfig)()