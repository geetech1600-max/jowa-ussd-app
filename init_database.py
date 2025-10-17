import psycopg2
import os

def init_database():
    config = {
        'dbname': os.environ.get('DB_NAME', 'postgres'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432')
    }
    
    try:
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        
        print("🚀 Initializing Jowa Database...")
        
        # Drop tables if they exist (for clean setup)
        print("Dropping existing tables...")
        cur.execute("DROP TABLE IF EXISTS applications CASCADE;")
        cur.execute("DROP TABLE IF EXISTS jobs CASCADE;")
        cur.execute("DROP TABLE IF EXISTS ussd_sessions CASCADE;")
        cur.execute("DROP TABLE IF EXISTS users CASCADE;")
        cur.execute("DROP TABLE IF EXISTS employers CASCADE;")
        
        # Create tables
        print("Creating tables...")
        
        # Users table
        cur.execute("""
            CREATE TABLE users (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                full_name VARCHAR(100),
                skills TEXT,
                location VARCHAR(100),
                experience_level VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created users table")
        
        # Employers table
        cur.execute("""
            CREATE TABLE employers (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(20) UNIQUE NOT NULL,
                company_name VARCHAR(100),
                business_type VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created employers table")
        
        # Jobs table
        cur.execute("""
            CREATE TABLE jobs (
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
        """)
        print("✅ Created jobs table")
        
        # Applications table
        cur.execute("""
            CREATE TABLE applications (
                id SERIAL PRIMARY KEY,
                job_id INTEGER REFERENCES jobs(id),
                user_id INTEGER REFERENCES users(id),
                status VARCHAR(20) DEFAULT 'pending',
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created applications table")
        
        # USSD Sessions table
        cur.execute("""
            CREATE TABLE ussd_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(100) UNIQUE NOT NULL,
                phone_number VARCHAR(20) NOT NULL,
                user_type VARCHAR(20),
                menu_level VARCHAR(50),
                data JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("✅ Created ussd_sessions table")
        
        # Create indexes for better performance
        print("Creating indexes...")
        cur.execute("CREATE INDEX idx_users_phone ON users(phone_number);")
        cur.execute("CREATE INDEX idx_employers_phone ON employers(phone_number);")
        cur.execute("CREATE INDEX idx_jobs_status ON jobs(status);")
        cur.execute("CREATE INDEX idx_jobs_employer ON jobs(employer_id);")
        cur.execute("CREATE INDEX idx_applications_job ON applications(job_id);")
        cur.execute("CREATE INDEX idx_applications_user ON applications(user_id);")
        cur.execute("CREATE INDEX idx_sessions_phone ON ussd_sessions(phone_number);")
        cur.execute("CREATE INDEX idx_sessions_updated ON ussd_sessions(updated_at);")
        
        print("✅ Created indexes")
        
        # Insert sample data for testing
        print("Inserting sample data...")
        
        # Sample employer
        cur.execute("""
            INSERT INTO employers (phone_number, company_name, business_type) 
            VALUES ('+260961234567', 'BuildRight Construction', 'Construction')
            ON CONFLICT (phone_number) DO NOTHING;
        """)
        
        # Sample jobs
        cur.execute("""
            INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
            VALUES (
                (SELECT id FROM employers WHERE phone_number = '+260961234567'),
                'Construction Helper',
                'Need helper for construction site. No experience needed.',
                'Lusaka',
                80.00,
                'daily'
            );
        """)
        
        cur.execute("""
            INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type) 
            VALUES (
                (SELECT id FROM employers WHERE phone_number = '+260961234567'),
                'Gardener',
                'Looking for experienced gardener for residential property.',
                'Ndola',
                50.00,
                'daily'
            );
        """)
        
        print("✅ Inserted sample data")
        
        conn.commit()
        cur.close()
        conn.close()
        
        print("🎉 Database initialization completed successfully!")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")

if __name__ == "__main__":
    init_database()