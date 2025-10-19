# debug_env.py
import os
from dotenv import load_dotenv

print("DEBUG: Environment Check")
print("=" * 40)

# Show current directory
print(f"Current directory: {os.getcwd()}")

# List files in current directory
print("Files in current directory:")
for file in os.listdir('.'):
    if file.endswith('.env') or file.endswith('.py'):
        print(f"  - {file}")

# Try to load .env
print("\nLoading .env file...")
load_dotenv()

# Check if DATABASE_URL is loaded
database_url = os.getenv('DATABASE_URL')
print(f"DATABASE_URL loaded: {bool(database_url)}")

if database_url:
    print(f"DATABASE_URL value: {database_url}")
else:
    print("ERROR: DATABASE_URL is not set")
    print("Please check your .env file")

# Check other database variables
print("\nOther database variables:")
print(f"DB_HOST: {os.getenv('DB_HOST')}")
print(f"DB_NAME: {os.getenv('DB_NAME')}")
print(f"DB_USER: {os.getenv('DB_USER')}")
print(f"DB_PASSWORD: {'*' * len(os.getenv('DB_PASSWORD', ''))}")
print(f"DB_PORT: {os.getenv('DB_PORT')}")

print("=" * 40)