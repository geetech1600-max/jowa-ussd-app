import psycopg2

def test_connection():
    DB_CONFIG = {
        'dbname': 'postgres',
        'user': 'postgres',
        'password': 'your-password',
        'host': 'db.xxxxxx.supabase.co',
        'port': '5432'
    }
    
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        print("✅ Database connected successfully!")
        
        # Test basic query
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"📊 Database version: {version[0]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

if __name__ == "__main__":
    test_connection()