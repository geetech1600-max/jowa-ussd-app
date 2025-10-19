# services/database_service.py
import psycopg2
import os
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class DatabaseService:
    def __init__(self):
        self.config = self.get_db_config()

    def get_db_config(self):
        database_url = os.getenv('DATABASE_URL')
        
        if database_url and database_url.startswith('postgresql://'):
            try:
                url = urlparse(database_url)
                return {
                    'dbname': url.path[1:],  # Remove leading slash
                    'user': url.username,
                    'password': url.password,
                    'host': url.hostname,
                    'port': url.port or 5432,
                    'sslmode': 'disable'  # Add this line to disable SSL
                }
            except:
                pass
        
        # Fallback to individual environment variables
        return {
            'dbname': os.getenv('DB_NAME', 'jowa'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres'),
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'sslmode': 'disable'  # Add this line
        }

    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            print(f"PostgreSQL connection error: {e}")
            return None

    def health_check(self):
        try:
            conn = self.get_connection()
            if conn:
                cur = conn.cursor()
                cur.execute("SELECT 1")
                cur.close()
                conn.close()
                return True
            return False
        except Exception as e:
            print(f"Health check failed: {e}")
            return False