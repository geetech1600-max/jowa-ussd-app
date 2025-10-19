# manual_test.py
import psycopg2

def manual_connection_test():
    print("Manual Connection Test")
    print("=" * 40)
    
    # Try direct connection
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="jowa",
            user="postgres",
            password="postgres",
            port="5432"
        )
        print("SUCCESS: Direct connection works!")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"PostgreSQL: {version}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Direct connection failed: {e}")
        return False

if __name__ == "__main__":
    manual_connection_test()