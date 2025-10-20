# Render PostgreSQL Database Configuration
def get_db_connection():
    try:
        # Render provides DATABASE_URL environment variable
        database_url = os.getenv('DATABASE_URL')
        
        if database_url:
            # For Render PostgreSQL - fix the URL format if needed
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            print(f"Connecting to database using DATABASE_URL")
            conn = psycopg2.connect(database_url, sslmode='require')
        else:
            # Fallback for local development
            print("Using local database configuration")
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'jowa'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=os.getenv('DB_PORT', '5432')
            )
        
        print("Database connection successful")
        return conn
        
    except Exception as e:
        print(f"Database connection error: {e}")
        # Print more detailed error information
        import traceback
        print(f"Detailed error: {traceback.format_exc()}")
        return None