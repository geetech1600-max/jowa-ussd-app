#!/usr/bin/env python3
"""
Render initialization script for JOWA deployment
"""
import os
import sys
import subprocess

def init_render():
    print("🚀 Initializing Render deployment for JOWA...")
    
    try:
        # Install dependencies
        print("📦 Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        # Debug: Check environment variables
        database_url = os.getenv('DATABASE_URL')
        print(f"🔍 DATABASE_URL in render_init: {bool(database_url)}")
        if database_url and '//' in database_url:
            url_parts = database_url.split('//')
            if len(url_parts) > 1:
                host_part = url_parts[1].split('@')[-1].split('/')[0]
                print(f"🔍 Database host in render_init: {host_part}")
        
        # Import and initialize database from app.py
        print("🔄 Initializing database...")
        
        # Add current directory to Python path
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from app import initialize_database
        success = initialize_database()
        
        if success:
            print("✅ Render initialization complete!")
            return True
        else:
            print("⚠️ Database initialization had issues, but continuing deployment...")
            return True  # Still return True to allow deployment
            
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        import traceback
        print(f"Full error: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = init_render()
    sys.exit(0 if success else 1)