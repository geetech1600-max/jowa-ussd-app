# init_postgresql.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    """Get database connection - simple and direct"""
    try:
        # Direct connection without any SSL checks
        conn = psycopg2.connect(
            host='localhost',
            database='jowa',
            user='postgres', 
            password='postgres',
            port=5432
        )
        return conn
    except Exception as e:
        print(f"Connection error: {e}")
        return None

def test_postgresql_connection():
    """Test PostgreSQL connection - no SSL checks"""
    print("Testing database connection...")
    
    conn = get_connection()
    if not conn:
        return False
        
    try:
        cur = conn.cursor()
        
        # Simple test query
        cur.execute("SELECT version();")
        version = cur.fetchone()[0]
        print(f"SUCCESS: Connected to PostgreSQL")
        print(f"Version: {version}")
        
        cur.execute("SELECT current_database();")
        db_name = cur.fetchone()[0]
        print(f"Database: {db_name}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Connection test failed: {e}")
        if conn:
            conn.close()
        return False

def init_postgresql_database():
    """Initialize PostgreSQL database tables"""
    print("Initializing database tables...")
    
    conn = get_connection()
    if not conn:
        print("ERROR: Cannot connect to database")
        return False
        
    try:
        cur = conn.cursor()
        
        # Create tables
        tables_sql = [
            # Users table
            """
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                skills TEXT,
                location VARCHAR(100),
                experience_level VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Employers table
            """
            CREATE TABLE IF NOT EXISTS employers (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                company_name VARCHAR(100),
                business_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Jobs table
            """
            CREATE TABLE IF NOT EXISTS jobs (
                id SERIAL PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(id),
                title VARCHAR(200) NOT NULL,
                description TEXT,
                category VARCHAR(100),
                location VARCHAR(100),
                payment_amount DECIMAL(10,2),
                payment_type VARCHAR(50),
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # Applications table
            """
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id),
                user_id INTEGER REFERENCES users(id),
                status VARCHAR(20) DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(job_id, user_id)
            );
            """,
            
            # USSD Sessions table
            """
            CREATE TABLE IF NOT EXISTS ussd_sessions (
                session_id VARCHAR(100) PRIMARY KEY,
                phone_number VARCHAR(20) NOT NULL,
                menu_level VARCHAR(50),
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        
        print("Creating tables...")
        for i, sql in enumerate(tables_sql, 1):
            cur.execute(sql)
            print(f"SUCCESS: Table {i} created")
        
        # Create indexes
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_employers_phone ON employers(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_employer ON jobs(employer_id);",
            "CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);",
            "CREATE INDEX IF NOT EXISTS idx_ussd_sessions_phone ON ussd_sessions(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_ussd_sessions_updated ON ussd_sessions(updated_at);"
        ]
        
        print("Creating indexes...")
        for i, sql in enumerate(indexes_sql, 1):
            cur.execute(sql)
            print(f"SUCCESS: Index {i} created")
        
        # Add sample data
        print("Adding sample data...")
        sample_data_sql = [
            # Sample users
            """
            INSERT INTO users (phone_number, full_name, skills, location) 
            VALUES ('+260971234567', 'John Banda', 'Construction, Carpentry, Painting', 'Lusaka')
            ON CONFLICT (phone_number) DO NOTHING;
            """,
            """
            INSERT INTO users (phone_number, full_name, skills, location) 
            VALUES ('+260972345678', 'Mary Phiri', 'Cleaning, Cooking, Childcare', 'Ndola')
            ON CONFLICT (phone_number) DO NOTHING;
            """,
            
            # Sample employers
            """
            INSERT INTO employers (phone_number, company_name, business_type) 
            VALUES ('+260973456789', 'BuildRight Construction', 'Construction')
            ON CONFLICT (phone_number) DO NOTHING;
            """,
            """
            INSERT INTO employers (phone_number, company_name, business_type) 
            VALUES ('+260974567890', 'CleanSweep Services', 'Cleaning')
            ON CONFLICT (phone_number) DO NOTHING;
            """,
            
            # Sample jobs
            """
            INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
            SELECT id, 'Construction Helper', 'Need helper for construction site', 'Lusaka', 80.00, 'daily'
            FROM employers WHERE phone_number = '+260973456789'
            ON CONFLICT DO NOTHING;
            """,
            """
            INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
            SELECT id, 'Office Cleaner', 'Cleaning office building', 'Ndola', 50.00, 'daily'
            FROM employers WHERE phone_number = '+260974567890'
            ON CONFLICT DO NOTHING;
            """
        ]
        
        for i, sql in enumerate(sample_data_sql, 1):
            cur.execute(sql)
            print(f"SUCCESS: Sample data {i} added")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("=" * 50)
        print("DATABASE INITIALIZATION COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"ERROR: Database initialization failed: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("JOWA DATABASE SETUP")
    print("=" * 50)
    
    # Test connection first
    if test_postgresql_connection():
        print("\nProceeding with database initialization...")
        print("-" * 40)
        
        if init_postgresql_database():
            print("\nSUCCESS: JOWA database is ready!")
        else:
            print("\nERROR: Database initialization failed")
    else:
        print("\nERROR: Cannot connect to PostgreSQL")
        print("\nTROUBLESHOOTING:")
        print("1. Make sure PostgreSQL service is running")
        print("2. Check if password is correct")
        print("3. Verify database 'jowa' exists")
        print("4. Try: net start postgresql-x64-16 (as Administrator)")