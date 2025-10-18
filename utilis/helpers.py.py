import json
from datetime import datetime

def update_session(cursor, conn, session_id, menu_level, data):
    cursor.execute("""
        UPDATE ussd_sessions 
        SET menu_level = %s, data = %s, updated_at = CURRENT_TIMESTAMP
        WHERE session_id = %s
    """, (menu_level, json.dumps(data), session_id))
    conn.commit()

def get_session_data(cursor, session_id):
    cursor.execute("SELECT menu_level, data FROM ussd_sessions WHERE session_id = %s", (session_id,))
    session_data = cursor.fetchone()
    
    if session_data:
        menu_level, data_json = session_data
        data = json.loads(data_json) if data_json else {}
        return menu_level, data
    return None, {}

def create_session(cursor, conn, session_id, phone_number, menu_level='main_menu', data=None):
    cursor.execute("""
        INSERT INTO ussd_sessions (session_id, phone_number, menu_level, data) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (session_id) DO UPDATE SET 
        menu_level = EXCLUDED.menu_level, 
        data = EXCLUDED.data,
        updated_at = CURRENT_TIMESTAMP
    """, (session_id, phone_number, menu_level, json.dumps(data or {})))
    conn.commit()

def cleanup_old_sessions(cursor, conn, hours=24):
    cursor.execute("""
        DELETE FROM ussd_sessions 
        WHERE updated_at < NOW() - INTERVAL '%s hours'
    """, (hours,))
    conn.commit()
    return cursor.rowcount

def format_currency(amount):
    try:
        return f"K{float(amount):.2f}"
    except (ValueError, TypeError):
        return "K0.00"

def format_date(date_value):
    if isinstance(date_value, datetime):
        return date_value.strftime('%d/%m/%Y')
    return str(date_value)

def truncate_text(text, max_length=100):
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."