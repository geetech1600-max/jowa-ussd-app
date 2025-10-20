# render_init.py
import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def init_render_database():
    """Initialize database tables on Render"""
    print("🔄 Initializing Render PostgreSQL Database...")
    
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL not found")
        return False
    
    try:
        conn = psycopg2.connect(database_url)
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
        
        print("📊 Creating tables...")
        for i, sql in enumerate(tables_sql, 1):
            cur.execute(sql)
            print(f"✅ Table {i} created")
        
        # Create indexes
        indexes_sql = [
            "CREATE INDEX IF NOT EXISTS idx_users_phone ON users(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_employers_phone ON employers(phone_number);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);",
            "CREATE INDEX IF NOT EXISTS idx_jobs_employer ON jobs(employer_id);",
            "CREATE INDEX IF NOT EXISTS idx_applications_user ON applications(user_id);",
            "CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);",
            "CREATE INDEX IF NOT EXISTS idx_ussd_sessions_phone ON ussd_sessions(phone_number);",
        ]
        
        print("📈 Creating indexes...")
        for i, sql in enumerate(indexes_sql, 1):
            cur.execute(sql)
            print(f"✅ Index {i} created")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("🎉 Render PostgreSQL database initialized successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

if __name__ == "__main__":
    init_render_database()