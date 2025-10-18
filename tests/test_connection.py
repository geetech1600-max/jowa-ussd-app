import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_flask():
    """Test if Flask is installed and working"""
    try:
        import flask
        print("SUCCESS: Flask is working!")
        print(f"   Version: {flask.__version__}")
        return True
    except ImportError:
        print("ERROR: Flask is not installed!")
        return False

def test_psycopg2():
    """Test if psycopg2 is installed"""
    try:
        import psycopg2
        print("SUCCESS: psycopg2 is installed!")
        print(f"   Version: {psycopg2.__version__}")
        return True
    except ImportError:
        print("ERROR: psycopg2 is not installed!")
        return False

def test_database_connection():
    """Test database connection"""
    try:
        import psycopg2
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("ERROR: DATABASE_URL not found in environment")
            print("TIP: Make sure you set the DATABASE_URL environment variable")
            return False
            
        print("Testing database connection...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # Test simple query
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        cursor.execute("SELECT current_database();")
        db_name = cursor.fetchone()
        
        cursor.execute("SELECT current_user;")
        db_user = cursor.fetchone()
        
        print("SUCCESS: Database connection successful!")
        print(f"Database: {db_name[0]}")
        print(f"User: {db_user[0]}")
        print(f"PostgreSQL: {db_version[0].split(',')[0]}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        return False

def test_environment_variables():
    """Test if all required environment variables are set"""
    print("Checking environment variables...")
    
    database_url = os.getenv('DATABASE_URL')
    secret_key = os.getenv('SECRET_KEY')
    flask_env = os.getenv('FLASK_ENV')
    
    vars_set = []
    if database_url:
        vars_set.append("DATABASE_URL")
    if secret_key:
        vars_set.append("SECRET_KEY")
    if flask_env:
        vars_set.append("FLASK_ENV")
    
    if vars_set:
        print(f"SUCCESS: Found variables: {', '.join(vars_set)}")
    else:
        print("WARNING: No environment variables found")
    
    return bool(database_url)  # Most important is DATABASE_URL

def main():
    print("=" * 50)
    print("Testing Jowa USSD App Dependencies...")
    print("=" * 50)
    
    tests = [
        test_environment_variables(),
        test_flask(),
        test_psycopg2(), 
        test_database_connection()
    ]
    
    print("=" * 50)
    
    if all(tests):
        print("ALL TESTS PASSED! You're ready to build your Jowa app!")
    else:
        print("Some tests failed. Please fix the issues above.")
        
        # Installation instructions
        print("\nSOLUTIONS:")
        if not test_flask():
            print("- Install Flask: pip install flask")
        if not test_psycopg2():
            print("- Install psycopg2: pip install psycopg2-binary")
        if not test_database_connection():
            print("- Check your DATABASE_URL connection string")
            print("- Verify your Supabase password is correct")
            print("- Make sure your IP is allowed in Supabase settings")

if __name__ == "__main__":
    main()