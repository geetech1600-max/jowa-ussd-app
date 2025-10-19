# test_db_connection.py
from services.database_service import DatabaseService

db_service = DatabaseService()
if db_service.health_check():
    print("SUCCESS: Database connection is working!")
else:
    print("ERROR: Database connection failed!")