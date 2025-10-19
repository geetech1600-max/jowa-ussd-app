# test_pgadmin.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def test_pgadmin_connection():
    print("Testing pgAdmin/PostgreSQL Connection...")
    print("=" * 50)
    
    # Your connection details from .env
    db_config = {
        'host': 'localhost',
        'database': 'jowa', 
        'user': 'postgres',
        'password': 'postgres',
        'port': '5432'
    }
    
    try:
        print("Attempting to connect...")
        conn = psycopg2.connect(**db_config)  # FIXED: psycopg2 not psycopopg2
        cur = conn.cursor()
        
        print("SUCCESS: Connected to PostgreSQL!")
        
        # Test basic queries
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL Version: {version}")
        
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()[0]
        print(f"Current Database: {db_name}")
        
        # List all databases
        cur.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        databases = cur.fetchall()
        print(f"Available Databases: {[db[0] for db in databases]}")
        
        cur.close()
        conn.close()
        print("All tests passed! pgAdmin setup is working correctly.")
        return True
        
    except psycopg2.OperationalError as e:
        print(f"CONNECTION FAILED: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Is PostgreSQL service running?")
        print("2. Check if password is correct")
        print("3. Verify database 'jowa' exists in pgAdmin")
        print("4. Make sure port 5432 is not blocked")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    test_pgadmin_connection()