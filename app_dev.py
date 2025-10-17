from flask import Flask, request, jsonify
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)

# SQLite database for development
def get_db_connection():
    conn = sqlite3.connect('jowa_dev.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Initialize SQLite database with tables"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Create tables
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            full_name TEXT,
            skills TEXT,
            location TEXT,
            experience_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS employers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT UNIQUE NOT NULL,
            company_name TEXT,
            business_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employer_id INTEGER,
            title TEXT NOT NULL,
            description TEXT,
            category TEXT,
            location TEXT,
            payment_amount REAL,
            payment_type TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (employer_id) REFERENCES employers (id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id INTEGER,
            user_id INTEGER,
            status TEXT DEFAULT 'pending',
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cur.execute('''
        CREATE TABLE IF NOT EXISTS ussd_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            phone_number TEXT NOT NULL,
            user_type TEXT,
            menu_level TEXT,
            data TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    print("✅ SQLite database initialized!")

# USSD Response Format
def ussd_response(text, session_id, continue_session=True):
    response_type = "2" if continue_session else "1"
    return {
        "sessionId": session_id,
        "message": text,
        "type": response_type
    }

# Main USSD Handler
@app.route('/ussd', methods=['POST'])
def ussd_handler():
    try:
        data = request.get_json()
        session_id = data.get('sessionId', 'test123')
        phone_number = data.get('phoneNumber', '+260000000000')
        text = data.get('text', '')
        
        print(f"USSD Request: {session_id}, {phone_number}, {text}")
        
        if text == '':
            response = {
                "sessionId": session_id,
                "message": "Welcome to JOWA! 🇿🇲\n\n1. Find Work\n2. Post Job\n3. About\n\nReply 1-3",
                "type": "2"
            }
        elif text == '1':
            response = {
                "sessionId": session_id,
                "message": "Find Work:\n\n1. Browse Jobs\n2. My Applications\n3. Back\n\nReply 1-3",
                "type": "2"
            }
        elif text == '2':
            response = {
                "sessionId": session_id,
                "message": "Post Job:\n\nPost job features coming soon!\n\nThank you for using Jowa!",
                "type": "1"
            }
        elif text == '3':
            response = {
                "sessionId": session_id,
                "message": "About Jowa:\n\nUSSD job app for Zambia.\nNo internet needed!\n\nDial *123# to start.",
                "type": "1"
            }
        else:
            response = {
                "sessionId": session_id,
                "message": f"You entered: {text}\n\nThank you for using Jowa!",
                "type": "1"
            }
            
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            "sessionId": "error",
            "message": "Service unavailable. Try again.",
            "type": "1"
        })

@app.route('/')
def home():
    return "Jowa USSD App (Development) is running!"

@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy", 
        "database": "sqlite",
        "message": "Development mode - using SQLite"
    })

@app.route('/test-db')
def test_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cur.fetchall()
        conn.close()
        
        table_names = [table[0] for table in tables]
        return jsonify({
            "status": "connected",
            "tables": table_names,
            "database": "jowa_dev.db"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    # Initialize database on startup
    init_database()
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)