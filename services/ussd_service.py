import json
from models.user import User
from models.employer import Employer
from models.job import Job
from models.application import Application
from utils.validators import validate_phone_number, validate_payment_amount
from utils.formatters import format_job_listing, format_application_list

class USSDService:
    def __init__(self, db_connection):
        self.conn = db_connection
        self.user_model = User(db_connection)
        self.employer_model = Employer(db_connection)
        self.job_model = Job(db_connection)
        self.application_model = Application(db_connection)

    def handle_main_menu(self, session_id, phone_number, text, session_data):
        if text == '1':
            user = self.user_model.get_by_phone(phone_number)
            if user and user.get('full_name'):
                session_data['menu_level'] = 'job_seeker_dashboard'
                return self.job_seeker_dashboard(phone_number), session_data
            else:
                session_data['menu_level'] = 'job_seeker_registration'
                session_data['registration_step'] = 1
                return "Welcome! Let's set up your profile.\n\nEnter your full name:", session_data
        
        elif text == '2':
            employer = self.employer_model.get_by_phone(phone_number)
            if employer and employer.get('company_name'):
                session_data['menu_level'] = 'employer_dashboard'
                return self.employer_dashboard(phone_number), session_data
            else:
                session_data['menu_level'] = 'employer_registration'
                session_data['registration_step'] = 1
                return "Welcome Employer! Let's register your business.\n\nEnter your company name:", session_data
        
        elif text == '3':
            about_text = """About JOWA\n\nConnecting job seekers with employers across Zambia. No internet needed!\n\nFind daily work opportunities\nPost jobs for free\nSimple USSD interface\nTrusted by Zambians\n\nFor support: +260960000000"""
            return about_text, session_data
        
        elif text == '4':
            support_text = """Contact Support:\n\nCall: +260960000000\nEmail: support@jowa.co.zm\n\nOur team is here to help you with any issues using Jowa.\n\nThank you for using Jowa!"""
            return support_text, session_data
        
        else:
            return "Invalid option. Please reply with 1, 2, 3, or 4", session_data

    def job_seeker_dashboard(self, phone_number):
        user = self.user_model.get_by_phone(phone_number)
        name = user.get('full_name', 'User') if user else "User"
        
        return f"""Welcome {name}!\n\n1. Browse Available Jobs\n2. My Applications\n3. Update Profile\n4. Back to Main Menu\n\nReply with 1, 2, 3, or 4"""

    def employer_dashboard(self, phone_number):
        employer = self.employer_model.get_by_phone(phone_number)
        company_name = employer.get('company_name', 'Employer') if employer else "Employer"
        
        return f"""Welcome {company_name}!\n\n1. Post New Job\n2. View My Jobs\n3. View Applications\n4. Back to Main Menu\n\nReply with 1, 2, 3, or 4"""

    def browse_jobs(self, phone_number, page=0):
        jobs = self.job_model.get_active_jobs(limit=3, offset=page*3)
        
        if not jobs:
            return "No jobs available at the moment. Check back later!"
        
        return format_job_listing(jobs, page)

    def handle_job_application(self, phone_number, job_index, page=0):
        jobs = self.job_model.get_active_jobs(limit=3, offset=page*3)
        
        if 0 <= job_index < len(jobs):
            job = jobs[job_index]
            user = self.user_model.get_by_phone(phone_number)
            
            if user:
                application = self.application_model.create(job['id'], user['id'])
                if application:
                    return f"Application submitted for: {job['title']}\n\nEmployer will contact you soon!"
        
        return "Invalid job selection. Please try again."

    def get_user_applications(self, phone_number, page=0):
        user = self.user_model.get_by_phone(phone_number)
        if not user:
            return "User not found."
        
        applications = self.application_model.get_by_user_id(user['id'], limit=5, offset=page*5)
        return format_application_list(applications, page)