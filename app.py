from flask import Flask, request, jsonify
import psycopg2
import os
import json
from datetime import datetime
from urllib.parse import urlparse
import re
import africastalking

app = Flask(__name__)

# Set your specific environment variables
os.environ['AT_USERNAME'] = 'sandbox'
os.environ['AT_API_KEY'] = 'atsk_f74b6e4b9e0aa7ea82f7c0058d7315528f829f1993888ac1e696b031adb336daa6385c04'
os.environ['DATABASE_URL'] = 'postgresql://postgres:CassidyMadando16@db.amtfabgmtsujurppknfg.supabase.co:5432/postgres'
os.environ['DB_HOST'] = 'db.amtfabgmtsujurppknfg.supabase.co'
os.environ['DB_NAME'] = 'postgres'
os.environ['DB_USER'] = 'postgres'
os.environ['DB_PASSWORD'] = 'CassidyMadando16'
os.environ['DB_PORT'] = '5432'
os.environ['SECRET_KEY'] = '728495e15b6c5d935285eb079f7c78b99e6c2a7f6571e528aa7c52e0dbf4715d'

# Initialize Africa's Talking
def initialize_africas_talking():
    try:
        username = os.environ.get('AT_USERNAME', 'sandbox')
        api_key = os.environ.get('AT_API_KEY', 'atsk_f74b6e4b9e0aa7ea82f7c0058d7315528f829f1993888ac1e696b031adb336daa6385c04')
        
        africastalking.initialize(username, api_key)
        
        global sms
        sms = africastalking.SMS
        
        print("Africa's Talking initialized successfully with username:", username)
        return True
    except Exception as e:
        print(f"Africa's Talking initialization failed: {e}")
        return False

# Initialize Africa's Talking when app starts
initialize_africas_talking()

# Database configuration for Supabase
def get_db_config():
    database_url = os.environ.get('DATABASE_URL', 'postgresql://postgres:CassidyMadando16@db.amtfabgmtsujurppknfg.supabase.co:5432/postgres')
    
    if database_url:
        try:
            url = urlparse(database_url)
            return {
                'dbname': url.path[1:] if url.path.startswith('/') else url.path,
                'user': url.username or 'postgres',
                'password': url.password or 'CassidyMadando16',
                'host': url.hostname or 'db.amtfabgmtsujurppknfg.supabase.co',
                'port': url.port or 5432,
                'sslmode': 'require'
            }
        except Exception as e:
            print(f"Error parsing DATABASE_URL: {e}")
    
    # Fallback to individual environment variables for Supabase
    return {
        'dbname': os.environ.get('DB_NAME', 'postgres'),
        'user': os.environ.get('DB_USER', 'postgres'),
        'password': os.environ.get('DB_PASSWORD', 'CassidyMadando16'),
        'host': os.environ.get('DB_HOST', 'db.amtfabgmtsujurppknfg.supabase.co'),
        'port': os.environ.get('DB_PORT', '5432'),
        'sslmode': 'require'
    }

def get_db_connection():
    try:
        config = get_db_config()
        print(f"Connecting to database: {config['host']}")
        conn = psycopg2.connect(**config)
        print("Database connection successful")
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

# Input validation
def validate_phone_number(phone):
    pattern = r'^\+260(9|7)[0-9]{8}$'
    return bool(re.match(pattern, phone))

def validate_payment_amount(amount):
    try:
        return float(amount) > 0
    except:
        return False

# Main USSD Handler
@app.route('/ussd', methods=['POST'])
def ussd_handler():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        session_id = data.get('sessionId')
        phone_number = data.get('phoneNumber')
        text = data.get('text', '')
        
        if not validate_phone_number(phone_number):
            return jsonify(ussd_response("Invalid phone number format. Use +260 format.", session_id, False))
        
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

# Africa's Talking USSD Callback Endpoint
@app.route('/at-ussd', methods=['POST'])
def africas_talking_ussd():
    """
    Africa's Talking USSD callback endpoint
    """
    try:
        # Get data from Africa's Talking
        session_id = request.values.get("sessionId")
        phone_number = request.values.get("phoneNumber")
        text = request.values.get("text", "")
        network_code = request.values.get("networkCode")
        
        print(f"Africa's Talking USSD: {session_id}, {phone_number}, {text}")
        
        # Process the USSD request
        if text == "":
            # First menu - welcome screen
            response = "CON Welcome to JOWA - Find Work in Zambia\n\n1. Looking for Work\n2. Post a Job\n3. About Jowa\n4. Contact Support\n\nReply with 1, 2, 3, or 4"
        else:
            # Process user input
            response = process_africas_talking_ussd(session_id, phone_number, text)
        
        return response
        
    except Exception as e:
        print(f"Africa's Talking USSD error: {e}")
        return "END Sorry, service temporarily unavailable. Please try again later."

def process_africas_talking_ussd(session_id, phone_number, text):
    """
    Process USSD input and return Africa's Talking formatted response
    """
    try:
        conn = get_db_connection()
        if not conn:
            return "END Service temporarily unavailable. Please try again."
        
        cur = conn.cursor()
        
        # Get or create session
        cur.execute("SELECT menu_level, data FROM ussd_sessions WHERE session_id = %s", (session_id,))
        session_data = cur.fetchone()
        
        if not session_data:
            # New session
            cur.execute("""
                INSERT INTO ussd_sessions (session_id, phone_number, menu_level, data) 
                VALUES (%s, %s, 'main_menu', '{}')
            """, (session_id, phone_number))
            conn.commit()
            menu_level = 'main_menu'
            data = {}
        else:
            menu_level, data_json = session_data
            data = json.loads(data_json) if data_json else {}
        
        # Process based on current menu level
        if menu_level == 'main_menu':
            if text == '1':
                # Job seeker path
                cur.execute("SELECT full_name FROM users WHERE phone_number = %s", (phone_number,))
                user = cur.fetchone()
                
                if user and user[0]:
                    update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
                    response_text = job_seeker_dashboard_at(session_id, phone_number, cur)
                else:
                    update_session(cur, conn, session_id, 'job_seeker_registration', {'step': 1})
                    response_text = "CON Welcome! Let's set up your profile.\n\nEnter your full name:"
            elif text == '2':
                # Employer path
                cur.execute("SELECT company_name FROM employers WHERE phone_number = %s", (phone_number,))
                employer = cur.fetchone()
                
                if employer and employer[0]:
                    update_session(cur, conn, session_id, 'employer_dashboard', {})
                    response_text = employer_dashboard_at(session_id, phone_number, cur)
                else:
                    update_session(cur, conn, session_id, 'employer_registration', {'step': 1})
                    response_text = "CON Welcome Employer! Let's register your business.\n\nEnter your company name:"
            elif text == '3':
                about_text = """END About JOWA\n\nConnecting job seekers with employers across Zambia. No internet needed!\n\nFind daily work opportunities\nPost jobs for free\nSimple USSD interface\nTrusted by Zambians\n\nFor support: +260960000000"""
                response_text = about_text
            elif text == '4':
                support_text = """END Contact Support:\n\nCall: +260960000000\nEmail: support@jowa.co.zm\n\nOur team is here to help you with any issues using Jowa.\n\nThank you for using Jowa!"""
                response_text = support_text
            else:
                response_text = "CON Invalid option. Please reply with 1, 2, 3, or 4\n\n1. Looking for Work\n2. Post a Job\n3. About Jowa\n4. Contact Support"
        
        elif menu_level == 'job_seeker_registration':
            response_text = handle_job_seeker_registration_at(session_id, phone_number, text, cur, conn, data)
        
        elif menu_level == 'employer_registration':
            response_text = handle_employer_registration_at(session_id, phone_number, text, cur, conn, data)
        
        elif menu_level == 'job_seeker_dashboard':
            response_text = handle_job_seeker_dashboard_at(session_id, phone_number, text, cur, conn, data)
        
        elif menu_level == 'employer_dashboard':
            response_text = handle_employer_dashboard_at(session_id, phone_number, text, cur, conn, data)
        
        elif menu_level == 'post_job':
            response_text = handle_post_job_at(session_id, phone_number, text, cur, conn, data)
        
        elif menu_level == 'browse_jobs':
            response_text = handle_browse_jobs_at(session_id, phone_number, text, cur, conn, data)
        
        else:
            response_text = "END Invalid option. Please dial the USSD code again to start."
        
        cur.close()
        conn.close()
        
        return response_text
        
    except Exception as e:
        print(f"Africa's Talking processing error: {e}")
        return "END Sorry, an error occurred. Please try again."

# Africa's Talking formatted menu functions
def job_seeker_dashboard_at(session_id, phone_number, cur):
    cur.execute("SELECT full_name FROM users WHERE phone_number = %s", (phone_number,))
    user = cur.fetchone()
    name = user[0] if user else "User"
    
    return f"CON Welcome {name}!\n\n1. Browse Available Jobs\n2. My Applications\n3. Update Profile\n4. Back to Main Menu\n\nReply with 1, 2, 3, or 4"

def employer_dashboard_at(session_id, phone_number, cur):
    cur.execute("SELECT company_name FROM employers WHERE phone_number = %s", (phone_number,))
    employer = cur.fetchone()
    company_name = employer[0] if employer else "Employer"
    
    return f"CON Welcome {company_name}!\n\n1. Post New Job\n2. View My Jobs\n3. View Applications\n4. Back to Main Menu\n\nReply with 1, 2, 3, or 4"

def handle_job_seeker_registration_at(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        if len(text.strip()) < 2:
            return "CON Please enter a valid full name:"
        
        data['full_name'] = text.strip()
        data['step'] = 2
        update_session(cur, conn, session_id, 'job_seeker_registration', data)
        return "CON Enter your skills (e.g., Construction, Farming, Cleaning):"
    
    elif step == 2:
        if len(text.strip()) < 2:
            return "CON Please enter your skills:"
        
        data['skills'] = text.strip()
        data['step'] = 3
        update_session(cur, conn, session_id, 'job_seeker_registration', data)
        return "CON Enter your location/town:"
    
    elif step == 3:
        if len(text.strip()) < 2:
            return "CON Please enter your location:"
        
        data['location'] = text.strip()
        
        # Save to database
        cur.execute("""
            UPDATE users SET full_name = %s, skills = %s, location = %s 
            WHERE phone_number = %s
        """, (data['full_name'], data['skills'], data['location'], phone_number))
        
        conn.commit()
        
        update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
        return job_seeker_dashboard_at(session_id, phone_number, cur)

def handle_employer_registration_at(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        if len(text.strip()) < 2:
            return "CON Please enter a valid company name:"
        
        data['company_name'] = text.strip()
        data['step'] = 2
        update_session(cur, conn, session_id, 'employer_registration', data)
        return "CON Enter your business type (e.g., Construction, Retail, Farming):"
    
    elif step == 2:
        if len(text.strip()) < 2:
            return "CON Please enter your business type:"
        
        data['business_type'] = text.strip()
        
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
        return employer_dashboard_at(session_id, phone_number, cur)

def handle_job_seeker_dashboard_at(session_id, phone_number, text, cur, conn, data):
    if text == '1':
        update_session(cur, conn, session_id, 'browse_jobs', {'page': 0})
        return browse_jobs_at(session_id, phone_number, cur, 0)
    
    elif text == '2':
        update_session(cur, conn, session_id, 'view_applications', {'page': 0})
        return show_my_applications_at(session_id, phone_number, cur, 0)
    
    elif text == '3':
        update_session(cur, conn, session_id, 'job_seeker_registration', {'step': 1})
        return "CON Update your profile:\n\nEnter your full name:"
    
    elif text == '4':
        update_session(cur, conn, session_id, 'main_menu', {})
        return "CON Welcome to JOWA - Find Work in Zambia\n\n1. Looking for Work\n2. Post a Job\n3. About Jowa\n4. Contact Support\n\nReply with 1, 2, 3, or 4"
    
    else:
        return "CON Invalid option. Please try again."

def handle_employer_dashboard_at(session_id, phone_number, text, cur, conn, data):
    if text == '1':
        update_session(cur, conn, session_id, 'post_job', {'step': 1})
        return "CON Let's post a new job!\n\nEnter job title:"
    
    elif text == '2':
        return show_employer_jobs_at(session_id, phone_number, cur)
    
    elif text == '3':
        return show_job_applications_at(session_id, phone_number, cur)
    
    elif text == '4':
        update_session(cur, conn, session_id, 'main_menu', {})
        return "CON Welcome to JOWA - Find Work in Zambia\n\n1. Looking for Work\n2. Post a Job\n3. About Jowa\n4. Contact Support\n\nReply with 1, 2, 3, or 4"
    
    else:
        return "CON Invalid option. Please try again."

def browse_jobs_at(session_id, phone_number, cur, page):
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
        return "END No jobs available at the moment. Check back later!"
    
    response_text = "CON Available Jobs:\n\n"
    for i, job in enumerate(jobs, 1):
        job_id, title, location, amount, payment_type, company = job
        response_text += f"{i}. {title}\n"
        response_text += f"   Location: {location} - {company}\n"
        response_text += f"   Payment: K{amount}/{payment_type}\n\n"
    
    response_text += "4. Next Page\n5. Back to Menu\n0. Main Menu"
    
    return response_text

def handle_browse_jobs_at(session_id, phone_number, text, cur, conn, data):
    page = data.get('page', 0)
    
    if text.isdigit():
        choice = int(text)
        if 1 <= choice <= 3:
            offset = page * 3
            cur.execute("""
                SELECT j.id, j.title FROM jobs j
                WHERE j.status = 'active'
                ORDER BY j.created_at DESC
                LIMIT 3 OFFSET %s
            """, (offset,))
            
            jobs = cur.fetchall()
            if choice <= len(jobs):
                job_id, job_title = jobs[choice-1]
                
                cur.execute("SELECT id FROM users WHERE phone_number = %s", (phone_number,))
                user_id = cur.fetchone()[0]
                
                cur.execute("""
                    SELECT id FROM applications 
                    WHERE job_id = %s AND user_id = %s
                """, (job_id, user_id))
                
                if not cur.fetchone():
                    cur.execute("""
                        INSERT INTO applications (job_id, user_id, status)
                        VALUES (%s, %s, 'pending')
                    """, (job_id, user_id))
                    conn.commit()
                    
                    # Send SMS notification to employer
                    send_sms_notification(phone_number, f"New application received for job: {job_title}. Applicant: {phone_number}")
                
                return f"END Application submitted for: {job_title}\n\nEmployer will contact you soon!"
        
        elif choice == 4:
            page += 1
            data['page'] = page
            update_session(cur, conn, session_id, 'browse_jobs', data)
            return browse_jobs_at(session_id, phone_number, cur, page)
        
        elif choice == 5:
            update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
            return job_seeker_dashboard_at(session_id, phone_number, cur)
        
        elif choice == 0:
            update_session(cur, conn, session_id, 'main_menu', {})
            return "CON Welcome to JOWA - Find Work in Zambia\n\n1. Looking for Work\n2. Post a Job\n3. About Jowa\n4. Contact Support\n\nReply with 1, 2, 3, or 4"
    
    return "CON Invalid option. Please try again."

def show_my_applications_at(session_id, phone_number, cur, page):
    offset = page * 5
    cur.execute("""
        SELECT j.title, e.company_name, a.status, a.applied_at
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN employers e ON j.employer_id = e.id
        JOIN users u ON a.user_id = u.id
        WHERE u.phone_number = %s
        ORDER BY a.applied_at DESC
        LIMIT 5 OFFSET %s
    """, (phone_number, offset))
    
    applications = cur.fetchall()
    
    if not applications:
        return "END You haven't applied to any jobs yet.\n\nBrowse jobs to get started!"
    
    response_text = "CON Your Applications:\n\n"
    for i, app in enumerate(applications, 1):
        title, company, status, applied_at = app
        status_text = "Approved" if status == 'approved' else "Pending" if status == 'pending' else "Rejected"
        response_text += f"{i}. {title}\n"
        response_text += f"   Company: {company}\n"
        response_text += f"   Status: {status_text}\n"
        response_text += f"   Date: {applied_at.strftime('%d/%m/%Y')}\n\n"
    
    response_text += "6. Next Page\n7. Previous Page\n0. Main Menu"
    
    return response_text

def handle_post_job_at(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        data['title'] = text
        data['step'] = 2
        update_session(cur, conn, session_id, 'post_job', data)
        return "CON Enter job description:"
    
    elif step == 2:
        data['description'] = text
        data['step'] = 3
        update_session(cur, conn, session_id, 'post_job', data)
        return "CON Enter job location:"
    
    elif step == 3:
        data['location'] = text
        data['step'] = 4
        update_session(cur, conn, session_id, 'post_job', data)
        return "CON Enter payment amount (e.g., 50):"
    
    elif step == 4:
        if not validate_payment_amount(text):
            return "CON Please enter a valid payment amount (e.g., 50):"
        
        data['payment_amount'] = text
        data['step'] = 5
        update_session(cur, conn, session_id, 'post_job', data)
        return "CON Enter payment type:\n1. Hourly\n2. Daily\n3. Project\n\nReply 1, 2, or 3"
    
    elif step == 5:
        payment_types = {'1': 'hourly', '2': 'daily', '3': 'project'}
        payment_type = payment_types.get(text)
        
        if not payment_type:
            return "CON Invalid choice. Enter payment type:\n1. Hourly\n2. Daily\n3. Project"
        
        data['payment_type'] = payment_type
        
        cur.execute("SELECT id FROM employers WHERE phone_number = %s", (phone_number,))
        employer_id = cur.fetchone()[0]
        
        cur.execute("""
            INSERT INTO jobs (employer_id, title, description, location, payment_amount, payment_type)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (employer_id, data['title'], data['description'], data['location'], 
              data['payment_amount'], data['payment_type']))
        
        conn.commit()
        
        update_session(cur, conn, session_id, 'employer_dashboard', {})
        return "END Job posted successfully!\n\nJob seekers can now apply for your position."

def show_employer_jobs_at(session_id, phone_number, cur):
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
        return "END You haven't posted any jobs yet.\n\nPost a job to find workers!"
    
    response_text = "END Your Jobs:\n\n"
    for job in jobs:
        title, status, applications = job
        status_text = "Active" if status == 'active' else "Inactive"
        response_text += f"Title: {title}\n"
        response_text += f"Status: {status_text}\n"
        response_text += f"Applications: {applications}\n\n"
    
    return response_text

def show_job_applications_at(session_id, phone_number, cur):
    cur.execute("""
        SELECT u.full_name, j.title, a.applied_at, u.phone_number
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.user_id = u.id
        WHERE j.employer_id = (SELECT id FROM employers WHERE phone_number = %s)
        ORDER BY a.applied_at DESC
        LIMIT 5
    """, (phone_number,))
    
    applications = cur.fetchall()
    
    if not applications:
        return "END No applications received yet.\n\nCheck back later!"
    
    response_text = "END Recent Applications:\n\n"
    for app in applications:
        name, title, applied_at, applicant_phone = app
        response_text += f"Job: {title}\n"
        response_text += f"Applicant: {name}\n"
        response_text += f"Phone: {applicant_phone}\n"
        response_text += f"Date: {applied_at.strftime('%d/%m/%Y')}\n\n"
    
    response_text += "Contact applicants via their phone numbers above."
    return response_text

# SMS Notification Function
def send_sms_notification(phone_number, message):
    """
    Send SMS notifications to users
    """
    try:
        if 'sms' in globals():
            response = sms.send(message, [phone_number])
            print(f"SMS sent to {phone_number}: {response}")
            return True
        else:
            print(f"SMS simulation to {phone_number}: {message}")
            return True
    except Exception as e:
        print(f"SMS sending failed: {e}")
        return False

def welcome_menu(session_id, phone_number):
    welcome_text = """Welcome to JOWA - Find Work in Zambia

1. Looking for Work
2. Post a Job
3. About Jowa
4. Contact Support

Reply with 1, 2, 3, or 4"""
    
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
        return ussd_response("Session expired. Please dial again.", session_id, False)
    
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
    elif menu_level == 'view_applications':
        response = handle_view_applications(session_id, phone_number, text, cur, conn, data)
    else:
        response = ussd_response("Invalid option. Please dial again.", session_id, False)
    
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
            return ussd_response("Welcome! Let's set up your profile.\n\nEnter your full name:", session_id)
    
    elif text == '2':
        # Employer path
        cur.execute("SELECT company_name FROM employers WHERE phone_number = %s", (phone_number,))
        employer = cur.fetchone()
        
        if employer and employer[0]:  # Employer is registered
            update_session(cur, conn, session_id, 'employer_dashboard', {})
            return employer_dashboard(session_id, phone_number, cur)
        else:
            update_session(cur, conn, session_id, 'employer_registration', {'step': 1})
            return ussd_response("Welcome Employer! Let's register your business.\n\nEnter your company name:", session_id)
    
    elif text == '3':
        about_text = """About JOWA\n\nConnecting job seekers with employers across Zambia. No internet needed!\n\nFind daily work opportunities\nPost jobs for free\nSimple USSD interface\nTrusted by Zambians\n\nFor support: +260960000000"""
        return ussd_response(about_text, session_id, False)
    
    elif text == '4':
        support_text = """Contact Support:\n\nCall: +260960000000\nEmail: support@jowa.co.zm\n\nOur team is here to help you with any issues using Jowa.\n\nThank you for using Jowa!"""
        return ussd_response(support_text, session_id, False)
    
    else:
        return ussd_response("Invalid option. Please reply with 1, 2, 3, or 4", session_id)

def handle_job_seeker_registration(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        # Save name and ask for skills
        if len(text.strip()) < 2:
            return ussd_response("Please enter a valid full name:", session_id)
        
        data['full_name'] = text.strip()
        data['step'] = 2
        update_session(cur, conn, session_id, 'job_seeker_registration', data)
        return ussd_response("Enter your skills (e.g., Construction, Farming, Cleaning):", session_id)
    
    elif step == 2:
        # Save skills and ask for location
        if len(text.strip()) < 2:
            return ussd_response("Please enter your skills:", session_id)
        
        data['skills'] = text.strip()
        data['step'] = 3
        update_session(cur, conn, session_id, 'job_seeker_registration', data)
        return ussd_response("Enter your location/town:", session_id)
    
    elif step == 3:
        # Save location and complete registration
        if len(text.strip()) < 2:
            return ussd_response("Please enter your location:", session_id)
        
        data['location'] = text.strip()
        
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
        update_session(cur, conn, session_id, 'view_applications', {'page': 0})
        return show_my_applications(session_id, phone_number, cur, 0)
    
    elif text == '3':
        update_session(cur, conn, session_id, 'job_seeker_registration', {'step': 1})
        return ussd_response("Update your profile:\n\nEnter your full name:", session_id)
    
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
        return ussd_response("No jobs available at the moment. Check back later!", session_id, False)
    
    response_text = "Available Jobs:\n\n"
    for i, job in enumerate(jobs, 1):
        job_id, title, location, amount, payment_type, company = job
        response_text += f"{i}. {title}\n"
        response_text += f"   Location: {location} - {company}\n"
        response_text += f"   Payment: K{amount}/{payment_type}\n\n"
    
    response_text += "4. Next Page\n5. Back to Menu\n0. Main Menu"
    
    return ussd_response(response_text, session_id)

def handle_browse_jobs(session_id, phone_number, text, cur, conn, data):
    page = data.get('page', 0)
    
    if text.isdigit():
        choice = int(text)
        if 1 <= choice <= 3:
            # Apply for job
            offset = page * 3
            cur.execute("""
                SELECT j.id, j.title FROM jobs j
                WHERE j.status = 'active'
                ORDER BY j.created_at DESC
                LIMIT 3 OFFSET %s
            """, (offset,))
            
            jobs = cur.fetchall()
            if choice <= len(jobs):
                job_id, job_title = jobs[choice-1]
                
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
                    
                    # Send SMS notification
                    send_sms_notification(phone_number, f"Thank you for applying to {job_title}. The employer will contact you soon.")
                
                return ussd_response(f"Application submitted for: {job_title}\n\nEmployer will contact you soon!", session_id, False)
        
        elif choice == 4:
            # Next page
            page += 1
            data['page'] = page
            update_session(cur, conn, session_id, 'browse_jobs', data)
            return browse_jobs(session_id, phone_number, cur, page)
        
        elif choice == 5:
            # Back to job seeker dashboard
            update_session(cur, conn, session_id, 'job_seeker_dashboard', {})
            return job_seeker_dashboard(session_id, phone_number, cur)
        
        elif choice == 0:
            # Back to main menu
            update_session(cur, conn, session_id, 'main_menu', {})
            return welcome_menu(session_id, phone_number)
    
    return ussd_response("Invalid option. Please try again.", session_id)

def show_my_applications(session_id, phone_number, cur, page):
    offset = page * 5
    cur.execute("""
        SELECT j.title, e.company_name, a.status, a.applied_at
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN employers e ON j.employer_id = e.id
        JOIN users u ON a.user_id = u.id
        WHERE u.phone_number = %s
        ORDER BY a.applied_at DESC
        LIMIT 5 OFFSET %s
    """, (phone_number, offset))
    
    applications = cur.fetchall()
    
    if not applications:
        return ussd_response("You haven't applied to any jobs yet.\n\nBrowse jobs to get started!", session_id, False)
    
    response_text = "Your Applications:\n\n"
    for i, app in enumerate(applications, 1):
        title, company, status, applied_at = app
        status_text = "Approved" if status == 'approved' else "Pending" if status == 'pending' else "Rejected"
        response_text += f"{i}. {title}\n"
        response_text += f"   Company: {company}\n"
        response_text += f"   Status: {status_text}\n"
        response_text += f"   Date: {applied_at.strftime('%d/%m/%Y')}\n\n"
    
    response_text += "6. Next Page\n7. Previous Page\n0. Main Menu"
    
    return ussd_response(response_text, session_id)

def handle_view_applications(session_id, phone_number, text, cur, conn, data):
    page = data.get('page', 0)
    
    if text == '6':
        page += 1
        data['page'] = page
        update_session(cur, conn, session_id, 'view_applications', data)
        return show_my_applications(session_id, phone_number, cur, page)
    
    elif text == '7':
        page = max(0, page - 1)
        data['page'] = page
        update_session(cur, conn, session_id, 'view_applications', data)
        return show_my_applications(session_id, phone_number, cur, page)
    
    elif text == '0':
        update_session(cur, conn, session_id, 'main_menu', {})
        return welcome_menu(session_id, phone_number)
    
    else:
        return ussd_response("Invalid option. Please try again.", session_id)

def handle_employer_registration(session_id, phone_number, text, cur, conn, data):
    step = data.get('step', 1)
    
    if step == 1:
        # Save company name and ask for business type
        if len(text.strip()) < 2:
            return ussd_response("Please enter a valid company name:", session_id)
        
        data['company_name'] = text.strip()
        data['step'] = 2
        update_session(cur, conn, session_id, 'employer_registration', data)
        return ussd_response("Enter your business type (e.g., Construction, Retail, Farming):", session_id)
    
    elif step == 2:
        # Save business type and complete registration
        if len(text.strip()) < 2:
            return ussd_response("Please enter your business type:", session_id)
        
        data['business_type'] = text.strip()
        
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
        return ussd_response("Let's post a new job!\n\nEnter job title:", session_id)
    
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
        # Get job title
        data['title'] = text
        data['step'] = 2
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter job description:", session_id)
    
    elif step == 2:
        # Get job description
        data['description'] = text
        data['step'] = 3
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter job location:", session_id)
    
    elif step == 3:
        # Get job location
        data['location'] = text
        data['step'] = 4
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter payment amount (e.g., 50):", session_id)
    
    elif step == 4:
        # Get payment amount
        if not validate_payment_amount(text):
            return ussd_response("Please enter a valid payment amount (e.g., 50):", session_id)
        
        data['payment_amount'] = text
        data['step'] = 5
        update_session(cur, conn, session_id, 'post_job', data)
        return ussd_response("Enter payment type:\n1. Hourly\n2. Daily\n3. Project\n\nReply 1, 2, or 3", session_id)
    
    elif step == 5:
        # Get payment type and save job
        payment_types = {'1': 'hourly', '2': 'daily', '3': 'project'}
        payment_type = payment_types.get(text)
        
        if not payment_type:
            return ussd_response("Invalid choice. Enter payment type:\n1. Hourly\n2. Daily\n3. Project", session_id)
        
        data['payment_type'] = payment_type
        
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
        return ussd_response("Job posted successfully!\n\nJob seekers can now apply for your position.", session_id, False)

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
        return ussd_response("You haven't posted any jobs yet.\n\nPost a job to find workers!", session_id, False)
    
    response_text = "Your Jobs:\n\n"
    for job in jobs:
        title, status, applications = job
        status_text = "Active" if status == 'active' else "Inactive"
        response_text += f"Title: {title}\n"
        response_text += f"Status: {status_text}\n"
        response_text += f"Applications: {applications}\n\n"
    
    return ussd_response(response_text, session_id, False)

def show_job_applications(session_id, phone_number, cur):
    cur.execute("""
        SELECT u.full_name, j.title, a.applied_at, u.phone_number
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON a.user_id = u.id
        WHERE j.employer_id = (SELECT id FROM employers WHERE phone_number = %s)
        ORDER BY a.applied_at DESC
        LIMIT 5
    """, (phone_number,))
    
    applications = cur.fetchall()
    
    if not applications:
        return ussd_response("No applications received yet.\n\nCheck back later!", session_id, False)
    
    response_text = "Recent Applications:\n\n"
    for app in applications:
        name, title, applied_at, applicant_phone = app
        response_text += f"Job: {title}\n"
        response_text += f"Applicant: {name}\n"
        response_text += f"Phone: {applicant_phone}\n"
        response_text += f"Date: {applied_at.strftime('%d/%m/%Y')}\n\n"
    
    response_text += "Contact applicants via their phone numbers above."
    return ussd_response(response_text, session_id, False)

def update_session(cur, conn, session_id, menu_level, data):
    cur.execute("""
        UPDATE ussd_sessions 
        SET menu_level = %s, data = %s, updated_at = CURRENT_TIMESTAMP
        WHERE session_id = %s
    """, (menu_level, json.dumps(data), session_id))
    conn.commit()

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    try:
        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            cur.execute("SELECT 1")
            cur.close()
            conn.close()
            return jsonify({
                "status": "healthy", 
                "database": "connected",
                "app": "JOWA USSD App",
                "timestamp": datetime.now().isoformat()
            }), 200
        else:
            return jsonify({"status": "unhealthy", "database": "disconnected"}), 503
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503

# SMS callback endpoint for Africa's Talking
@app.route('/at-sms-callback', methods=['POST'])
def sms_callback():
    try:
        data = request.get_json()
        print(f"SMS Callback received: {data}")
        return jsonify({"status": "success"}), 200
    except Exception as e:
        print(f"SMS callback error: {e}")
        return jsonify({"status": "error"}), 400

@app.route('/')
def home():
    return "JOWA USSD App is running! Database: db.amtfabgmtsujurppknfg.supabase.co"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("Starting JOWA USSD App...")
    print("Africa's Talking Username:", os.environ.get('AT_USERNAME'))
    print("Database Host:", os.environ.get('DB_HOST'))
    app.run(host='0.0.0.0', port=port, debug=False)