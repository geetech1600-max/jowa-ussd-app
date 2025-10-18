import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def check_table_structure():
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:CassidyMadando16@db.amtfabgmtsujurppknfg.supabase.co:5432/postgres')
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        expected_tables = {
            'users': ['id', 'phone_number', 'full_name', 'skills', 'location', 'created_at'],
            'employers': ['id', 'phone_number', 'company_name', 'business_type', 'created_at'],
            'jobs': ['id', 'employer_id', 'title', 'description', 'location', 'payment_amount', 'payment_type', 'status', 'created_at'],
            'applications': ['id', 'job_id', 'user_id', 'status', 'applied_at'],
            'ussd_sessions': ['session_id', 'phone_number', 'menu_level', 'data', 'created_at', 'updated_at']
        }
        
        print("Checking table structures...")
        
        for table, expected_columns in expected_tables.items():
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = %s
            """, (table,))
            
            actual_columns = [row[0] for row in cur.fetchall()]
            
            if not actual_columns:
                print(f"FAILED: Table '{table}' does not exist")
                continue
            
            missing_columns = set(expected_columns) - set(actual_columns)
            extra_columns = set(actual_columns) - set(expected_columns)
            
            if not missing_columns and not extra_columns:
                print(f"SUCCESS: Table '{table}': Structure correct")
            else:
                print(f"WARNING: Table '{table}':")
                if missing_columns:
                    print(f"   Missing columns: {missing_columns}")
                if extra_columns:
                    print(f"   Extra columns: {extra_columns}")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"FAILED: Error checking table structure: {e}")

if __name__ == "__main__":
    check_table_structure()