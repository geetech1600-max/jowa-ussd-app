import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize database tables"""
    try:
        # Get database connection
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            print("❌ DATABASE_URL not found in environment")
            return
        
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        
        print("🚀 Initializing Jowa Database Tables...")
        
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
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """,
            
            # USSD Sessions table
            """
            CREATE TABLE IF NOT EXISTS ussd_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                user_type VARCHAR(20),
                menu_level VARCHAR(50),
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """
        ]
        
        for i, sql in enumerate(tables_sql, 1):
            cur.execute(sql)
            print(f"✅ Table {i} created/verified")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("🎉 Database initialization completed!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    init_database()