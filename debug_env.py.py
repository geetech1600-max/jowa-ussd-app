import os
import sys

print("🔍 Debugging Environment Variables...")
print("=" * 40)

# Check current directory
print(f"📁 Current directory: {os.getcwd()}")

# List all files in current directory
print("📄 Files in current directory:")
for file in os.listdir('.'):
    print(f"   - {file}")

# Check if .env file exists
env_exists = os.path.exists('.env')
print(f"📁 .env file exists: {env_exists}")

# Try to load dotenv manually
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv loaded successfully")
    
    # Check if DATABASE_URL is loaded
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        print("✅ DATABASE_URL found in environment")
        # Show first part of URL (without password)
        if '@' in database_url:
            parts = database_url.split('@')
            print(f"   Host: {parts[1]}")
    else:
        print("❌ DATABASE_URL not found")
        
except ImportError:
    print("❌ python-dotenv not installed")

print("=" * 40)