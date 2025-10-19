# test_db_fixed.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    print("Testing Database Connection with SSL Disabled")
    print("=" * 50)
    
    # Connection parameters with SSL disabled
    conn_params = {
        'host': 'localhost',
        'database': 'jowa',
        'user': 'postgres',
        'password': 'postgres',
        'port': 5432,
        'sslmode': 'disable'
    }
    
    try:
        conn = psycopg2.connect(**conn_params)
        cur = conn.cursor()
        
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"SUCCESS: Connected to PostgreSQL")
        print(f"Version: {version}")
        
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()[0]
        print(f"Database: {db_name}")
        
        # List tables
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
        tables = [row[0] for row in cur.fetchall()]
        print(f"Tables: {', '.join(tables)}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Connection failed: {e}")
        return False

if __name__ == "__main__":
    if test_connection():
        print("\nDatabase connection is working!")
    else:
        print("\nDatabase connection failed!")