import africastalking
import os
from dotenv import load_dotenv

load_dotenv()

class SMSService:
    def __init__(self):
        self.username = os.getenv('AT_USERNAME', 'sandbox')
        self.api_key = os.getenv('AT_API_KEY', '')
        self.initialized = False
        self.initialize()

    def initialize(self):
        try:
            africastalking.initialize(self.username, self.api_key)
            self.sms = africastalking.SMS
            self.initialized = True
            print("SMS Service initialized successfully")
        except Exception as e:
            print(f"SMS Service initialization failed: {e}")
            self.initialized = False

    def send_sms(self, phone_number, message):
        if not self.initialized:
            print(f"SMS Simulation to {phone_number}: {message}")
            return True
        
        try:
            response = self.sms.send(message, [phone_number])
            print(f"SMS sent to {phone_number}: {response}")
            return True
        except Exception as e:
            print(f"SMS sending failed: {e}")
            return False

    def send_application_notification(self, employer_phone, job_title, applicant_phone):
        message = f"New application for '{job_title}' from {applicant_phone}. Login to JOWA to view details."
        return self.send_sms(employer_phone, message)

    def send_application_confirmation(self, applicant_phone, job_title):
        message = f"Thank you for applying to '{job_title}'. The employer will contact you soon via JOWA."
        return self.send_sms(applicant_phone, message)

    def send_job_posted_confirmation(self, employer_phone, job_title):
        message = f"Your job '{job_title}' has been posted successfully. Job seekers can now apply."
        return self.send_sms(employer_phone, message)