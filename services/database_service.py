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
        
        if database_url:
            try:
                url = urlparse(database_url)
                return {
                    'dbname': url.path[1:] if url.path.startswith('/') else url.path,
                    'user': url.username or 'postgres',
                    'password': url.password or 'CassidyMadando16',
                    'host': url.hostname or 'db.amtfabgmtsujurppknfg.supabase.co',
                    'port': url.port or 5432,
                    'sslmode': 'require'
                }
            except Exception as e:
                print(f"Error parsing DATABASE_URL: {e}")
        
        return {
            'dbname': os.getenv('DB_NAME', 'postgres'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'CassidyMadando16'),
            'host': os.getenv('DB_HOST', 'db.amtfabgmtsujurppknfg.supabase.co'),
            'port': os.getenv('DB_PORT', '5432'),
            'sslmode': 'require'
        }

    def get_connection(self):
        try:
            conn = psycopg2.connect(**self.config)
            return conn
        except Exception as e:
            print(f"Database connection error: {e}")
            return None

    def execute_query(self, query, params=None):
        conn = self.get_connection()
        if not conn:
            return None
        
        try:
            cur = conn.cursor()
            cur.execute(query, params or ())
            
            if query.strip().upper().startswith('SELECT'):
                result = cur.fetchall()
                columns = [desc[0] for desc in cur.description]
                return [dict(zip(columns, row)) for row in result]
            else:
                conn.commit()
                return cur.rowcount
            
            cur.close()
            conn.close()
        except Exception as e:
            print(f"Query execution error: {e}")
            conn.rollback()
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
        except:
            return False