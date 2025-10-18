import psycopg2

def test_db():
    try:
        conn = psycopg2.connect(
            host="db.amtfabgmtsujurppknfg.supabase.co",
            database="postgres",
            user="postgres",
            password="CassidyMadando16",
            port="5432"
        )
        print("✅ Connected successfully!")
        conn.close()
    except Exception as e:
        print(f"❌ Connection failed: {e}")

test_db()