# simple_db_test.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def simple_test():
    print("Simple Database Connection Test")
    print("=" * 40)
    
    try:
        # Direct connection with SSL disabled
        conn = psycopg2.connect(
            host='localhost',
            database='jowa',
            user='postgres',
            password='postgres',
            port=5432,
            sslmode='disable'
        )
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"SUCCESS: Connected to {version}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        return False

if __name__ == "__main__":
    if simple_test():
        print("Database connection is working!")
    else:
        print("Database connection failed!")