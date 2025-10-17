from flask import Flask, request, jsonify
import psycopg2
import os
import json
from datetime import datetime

app = Flask(__name__)

# Database configuration - will be set via environment variables
def get_db_config():
    # If DATABASE_URL is provided (common in hosting platforms)
    if os.environ.get('DATABASE_URL'):
        try:
            from urllib.parse import urlparse
            url = urlparse(os.environ.get('DATABASE_URL'))
            return {
                'dbname': url.path[1:],
                'user': url.username,
                'password': url.password,
                'host': url.hostname,
                'port': url.port
            }
        except:
            pass
    
    # Fallback to individual environment variables
    return {
        'dbname': os.environ.get('DB_NAME', 'postgres'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'host': os.environ.get('DB_HOST', 'localhost'),
        'port': os.environ.get('DB_PORT', '5432')
    }

def get_db_connection():
    try:
        conn = psycopg2.connect(**get_db_config())
        return conn
    except Exception as e:
        print(f"Database connection error: {e}")
        return None

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
        # Get USSD parameters
        session_id = request.json.get('sessionId')
        phone_number = request.json.get('phoneNumber')
        text = request.json.get('text', '')
        
        print(f"USSD Request: {session_id}, {phone_number}, {text}")
        
        # Initialize session if first request
        if text == '':
            return welcome_menu(session_id, phone_number)
        
        # Process user input
        response = process_input(session_id, phone_number, text)
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify(ussd_response("Sorry, an error occurred. Please try again.", session_id, False))

def welcome_menu(session_id, phone_number):
    welcome_text = """Welcome to JOWA - Find Work in Zambia!
    
1. Looking for Work
2. Post a Job
3. About Jowa
    
Reply with 1, 2, or 3"""
    
    # Initialize session
    conn = get_db_connection()
    if conn:
        cur = conn.cursor()
        
        # Check if user exists
        cur.execute("SELECT phone_number FROM users WHERE phone_number = %s", (phone_number,))
        user_exists = cur.fetchone()
        
        if not user_exists:
            cur.execute("INSERT INTO users (phone_number) VALUES (%s) ON CONFLICT DO NOTHING", (phone_number,))
        
        # Initialize session
        cur.execute("""
            INSERT INTO ussd_sessions (session_id, phone_number, menu_level, data) 
            VALUES (%s, %s, 'main_menu', '{}')
            ON CONFLICT (session_id) DO UPDATE SET 
            menu_level = 'main_menu', updated_at = CURRENT_TIMESTAMP
        """, (session_id, phone_number))
        
        conn.commit()
        cur.close()
        conn.close()
    
    return jsonify(ussd_response(welcome_text, session_id))

def process_input(session_id, phone_number, text):
    conn = get_db_connection()
    if not conn:
        return ussd_response("Service temporarily unavailable. Please try again later.", session_id, False)
    
    cur = conn.cursor()
    
    # Get current session state
    cur.execute("SELECT menu_level, data FROM ussd_sessions WHERE session_id = %s", (session_id,))
    session_data = cur.fetchone()
    
    if not session_data:
        return ussd_response("Session expired. Please dial *123# again.", session_id, False)
    
    menu_level, data_json = session_data
    data = json.loads(data_json) if data_json else {}
    
    # Route based on current menu level
    if menu_level == 'main_menu':
        response = handle_main_menu(session_id, phone_number, text, cur, conn)
    elif menu_level == 'job_seeker_registration':
        response = handle_job_seeker_registration(session_id, phone_number, text, cur, conn, data)
    elif menu_level == 'employer_registration':
        response = handle_employer_registration(session_id, phone_number, text, cur, conn, data)
    elif menu_level == 'job_seeker_dashboard':
        response = handle_job_seeker_dashboard(session_id, phone_number, text, cur, conn, data)
    elif menu_level == 'employer_dashboard':
        response = handle_employer_dashboard(session_id, phone_number, text, cur, conn, data)
    elif menu_level == 'post_job':
        response = handle_post_job(session_id, phone_number, text, cur, conn, data)
    elif menu_level == 'browse_jobs':
        response = handle_browse_jobs(session_id, phone_number, text, cur, conn, data)
    else:
        response = ussd_response("Invalid option. Please dial *123# to start again.", session_id, False)
    
    cur.close()
    conn.close()
    return response

def handle_main_menu(session_id, phone_number, text, cur, conn):
    if text == '1':
        # Job Seeker path
        cur.execute("SELECT full_name FROM users WHERE phone_number = %s", (phone_number,))
        user = cur.fetchone()
        
        if user and user[0]:  # User is registered
            update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
            return job_seeker_dashboard(session_id, phone_number, cur)
        else:
            update_session(cur, conn, session_id, 'job_seeker_registration', {'step': 1})
            return ussd_response("Please enter your full name:", session_id)
    
    elif text == '2':
        # Employer path
        cur.execute("SELECT company_name FROM employers WHERE phone_number = %s", (phone_number,))
        employer = cur.fetchone()
        
        if employer and employer[0]:  # Employer is registered
            update_session(cur, conn, session_id, 'employer_dashboard', {})
            return employer_dashboard(session_id, phone_number, cur)
        else:
            update_session(cur, conn, session_id, 'employer_registration', {'step': 1})
            return ussd_response("Please enter your company/business name:", session_id)
    
    elif text == '3':
        about_text = """JOWA - Find Work Zambia

Jowa connects job seekers with employers for informal jobs. No internet needed!

Features:
• Find daily work
• Post job opportunities
• Free to use
• Simple USSD interface

Dial *123# to get started!"""
        return ussd_response(about_text, session_id, False)
    
    else:
        return ussd_response("Invalid option. Please reply with 1, 2, or 3", session_id)

def handle_job_seeker_registration(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        # Save name and ask for skills
        data['full_name'] = text
        data['step'] = 2
        update_session(cur, conn, session_id, 'job_seeker_registration', data)
        return ussd_response("Enter your skills (e.g., Gardening, Cleaning, Construction):", session_id)
    
    elif step == 2:
        # Save skills and ask for location
        data['skills'] = text
        data['step'] = 3
        update_session(cur, conn, session_id, 'job_seeker_registration', data)
        return ussd_response("Enter your location/town:", session_id)
    
    elif step == 3:
        # Save location and complete registration
        data['location'] = text
        
        # Save to database
        cur.execute("""
            UPDATE users SET full_name = %s, skills = %s, location = %s 
            WHERE phone_number = %s
        """, (data['full_name'], data['skills'], data['location'], phone_number))
        
        conn.commit()
        
        update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
        return job_seeker_dashboard(session_id, phone_number, cur)

def job_seeker_dashboard(session_id, phone_number, cur):
    # Get user info
    cur.execute("SELECT full_name FROM users WHERE phone_number = %s", (phone_number,))
    user = cur.fetchone()
    
    name = user[0] if user else "User"
    
    dashboard_text = f"""Welcome {name}!

1. Browse Available Jobs
2. My Applications
3. Update Profile
4. Back to Main Menu

Reply with 1, 2, 3, or 4"""
    
    return ussd_response(dashboard_text, session_id)

def handle_job_seeker_dashboard(session_id, phone_number, text, cur, conn, data):
    if text == '1':
        update_session(cur, conn, session_id, 'browse_jobs', {'page': 0})
        return browse_jobs(session_id, phone_number, cur, 0)
    
    elif text == '2':
        return show_my_applications(session_id, phone_number, cur)
    
    elif text == '3':
        update_session(cur, conn, session_id, 'job_seeker_registration', {'step': 1})
        return ussd_response("Enter your full name:", session_id)
    
    elif text == '4':
        update_session(cur, conn, session_id, 'main_menu', {})
        return welcome_menu(session_id, phone_number)
    
    else:
        return ussd_response("Invalid option. Please try again.", session_id)

def browse_jobs(session_id, phone_number, cur, page):
    offset = page * 3
    cur.execute("""
        SELECT j.id, j.title, j.location, j.payment_amount, j.payment_type, e.company_name
        FROM jobs j
        JOIN employers e ON j.employer_id = e.id
        WHERE j.status = 'active'
        ORDER BY j.created_at DESC
        LIMIT 3 OFFSET %s
    """, (offset,))
    
    jobs = cur.fetchall()
    
    if not jobs:
        return ussd_response("No jobs available at the moment. Check back later!", session_id)
    
    response_text = "Available Jobs:\n\n"
    for i, job in enumerate(jobs, 1):
        job_id, title, location, amount, payment_type, company = job
        response_text += f"{i}. {title}\n"
        response_text += f"   {location} - {company}\n"
        response_text += f"   K{amount}/{payment_type}\n\n"
    
    response_text += "4. Next Page\n5. Previous Page\n6. Back"
    
    return ussd_response(response_text, session_id)

def handle_browse_jobs(session_id, phone_number, text, cur, conn, data):
    page = data.get('page', 0)
    
    if text.isdigit():
        choice = int(text)
        if 1 <= choice <= 3:
            # Apply for job
            offset = page * 3
            cur.execute("""
                SELECT j.id FROM jobs j
                WHERE j.status = 'active'
                ORDER BY j.created_at DESC
                LIMIT 3 OFFSET %s
            """, (offset,))
            
            jobs = cur.fetchall()
            if choice <= len(jobs):
                job_id = jobs[choice-1][0]
                
                # Get user ID
                cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone_number,))
                user_id = cur.fetchone()[0]
                
                # Check if already applied
                cur.execute("""
                    SELECT id FROM applications 
                    WHERE job_id = %s AND user_id = %s
                """, (job_id, user_id))
                
                if not cur.fetchone():
                    # Create application
                    cur.execute("""
                        INSERT INTO applications (job_id, user_id, status)
                        VALUES (%s, %s, 'pending')
                    """, (job_id, user_id))
                    conn.commit()
                
                return ussd_response("Application submitted! Employer will contact you.", session_id, False)
        
        elif choice == 4:
            # Next page
            page += 1
            data['page'] = page
            update_session(cur, conn, session_id, 'browse_jobs', data)
            return browse_jobs(session_id, phone_number, cur, page)
        
        elif choice == 5:
            # Previous page
            if page > 0:
                page -= 1
                data['page'] = page
                update_session(cur, conn, session_id, 'browse_jobs', data)
                return browse_jobs(session_id, phone_number, cur, page)
            else:
                return ussd_response("You're on the first page.", session_id)
        
        elif choice == 6:
            update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
            return job_seeker_dashboard(session_id, phone_number, cur)
    
    return ussd_response("Invalid option. Please try again.", session_id)

def handle_employer_registration(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        # Save company name and ask for business type
        data['company_name'] = text
        data['step'] = 2
        update_session(cur, conn, session_id, 'employer_registration', data)
        return ussd_response("Enter your business type (e.g., Construction, Farming, Retail):", session_id)
    
    elif step == 2:
        # Save business type and complete registration
        data['business_type'] = text
        
        # Save to database
        cur.execute("""
            INSERT INTO employers (phone_number, company_name, business_type) 
            VALUES (%s, %s, %s)
            ON CONFLICT (phone_number) DO UPDATE SET
            company_name = EXCLUDED.company_name,
            business_type = EXCLUDED.business_type
        """, (phone_number, data['company_name'], data['business_type']))
        
        conn.commit()
        
        update_session(cur, conn, session_id, 'employer_dashboard', {})
        return employer_dashboard(session_id, phone_number, cur)

def employer_dashboard(session_id, phone_number, cur):
    # Get employer info
    cur.execute("SELECT company_name FROM employers WHERE phone_number = %s", (phone_number,))
    employer = cur.fetchone()
    
    company_name = employer[0] if employer else "Employer"
    
    dashboard_text = f"""Welcome {company_name}!

1. Post New Job
2. View My Jobs
3. View Applications
4. Back to Main Menu

Reply with 1, 2, 3, or 4"""
    
    return ussd_response(dashboard_text, session_id)

def handle_employer_dashboard(session_id, phone_number, text, cur, conn, data):
    if text == '1':
        update_session(cur, conn, session_id, 'post_job', {'step': 1})
        return ussd_response("Enter job title:", session_id)
    
    elif text == '2':
        return show_employer_jobs(session_id, phone_number, cur)
    
    elif text == '3':
        return show_job_applications(session_id, phone_number, cur)
    
    elif text == '4':
        update_session(cur, conn, session_id, 'main_menu', {})
        return welcome_menu(session_id, phone_number)
    
    else:
        return ussd_response("Invalid option. Please try again.", session_id)

def handle_post_job(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        data['title'] = text
        data['step'] = 2
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter job description:", session_id)
    
    elif step == 2:
        data['description'] = text
        data['step'] = 3
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter job location:", session_id)
    
    elif step == 3:
        data['location'] = text
        data['step'] = 4
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter payment amount (e.g., 50):", session_id)
    
    elif step == 4:
        data['payment_amount'] = text
        data['step'] = 5
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter payment type (hourly/daily/project):", session_id)
    
    elif step == 5:
        data['payment_type'] = text
        
        # Get employer ID
        cur.execute("SELECT id FROM employers WHERE phone_number = %s", (phone_number,))
        employer_id = cur.fetchone()[0]
        
        # Save job to database
        cur.execute("""
            INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (employer_id, data['title'], data['description'], data['location'], 
              data['payment_amount'], data['payment_type']))
        
        conn.commit()
        
        update_session(cur, conn, session_id, 'employer_dashboard', {})
        return ussd_response("Job posted successfully! Job seekers can now apply.", session_id, False)

def update_session(cur, conn, session_id, menu_level, data):
    cur.execute("""
        UPDATE ussd_sessions 
        SET menu_level = %s, data = %s, updated_at = CURRENT_TIMESTAMP
        WHERE session_id = %s
    """, (menu_level, json.dumps(data), session_id))
    conn.commit()

def show_my_applications(session_id, phone_number, cur):
    cur.execute("""
        SELECT j.title, a.status, a.applied_at
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.user_id = u.id
        WHERE u.phone_number = %s
        ORDER BY a.applied_at DESC
        LIMIT 5
    """, (phone_number,))
    
    applications = cur.fetchall()
    
    if not applications:
        return ussd_response("You haven't applied to any jobs yet.", session_id, False)
    
    response_text = "Your Applications:\n\n"
    for app in applications:
        title, status, applied_at = app
        response_text += f"- {title}\n  Status: {status}\n  Applied: {applied_at.strftime('%d/%m/%Y')}\n\n"
    
    return ussd_response(response_text, session_id, False)

def show_employer_jobs(session_id, phone_number, cur):
    cur.execute("""
        SELECT j.title, j.status, COUNT(a.id) as applications
        FROM jobs j
        LEFT JOIN applications a ON j.id = a.job_id
        WHERE j.employer_id = (SELECT id FROM employers WHERE phone_number = %s)
        GROUP BY j.id, j.title, j.status
        ORDER BY j.created_at DESC
        LIMIT 5
    """, (phone_number,))
    
    jobs = cur.fetchall()
    
    if not jobs:
        return ussd_response("You haven't posted any jobs yet.", session_id, False)
    
    response_text = "Your Jobs:\n\n"
    for job in jobs:
        title, status, applications = job
        response_text += f"- {title}\n  Status: {status}\n  Applications: {applications}\n\n"
    
    return ussd_response(response_text, session_id, False)

def show_job_applications(session_id, phone_number, cur):
    cur.execute("""
        SELECT u.full_name, j.title, a.applied_at
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.user_id = u.id
        WHERE j.employer_id = (SELECT id FROM employers WHERE phone_number = %s)
        ORDER BY a.applied_at DESC
        LIMIT 5
    """, (phone_number,))
    
    applications = cur.fetchall()
    
    if not applications:
        return ussd_response("No applications received yet.", session_id, False)
    
    response_text = "Recent Applications:\n\n"
    for app in applications:
        name, title, applied_at = app
        response_text += f"- {title}\n  Applicant: {name}\n  Applied: {applied_at.strftime('%d/%m/%Y')}\n\n"
    
    response_text += "Contact applicants via their phone numbers."
    return ussd_response(response_text, session_id, False)

@app.route('/')
def home():
    return "Jowa USSD App is running!"

@app.route('/health')
def health_check():
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'Database connection failed'}), 500
        
        cur = conn.cursor()
        
        # Check if all tables exist
        tables = ['users', 'employers', 'jobs', 'applications', 'ussd_sessions']
        existing_tables = []
        
        for table in tables:
            cur.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = %s
                );
            """, (table,))
            exists = cur.fetchone()[0]
            existing_tables.append({'table': table, 'exists': exists})
        
        cur.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'tables': existing_tables
        })
        
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)