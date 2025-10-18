import africastalking
import os
from dotenv import load_dotenv

load_dotenv()

class AfricaTalkingConfig:
    def __init__(self):
        self.username = os.getenv('AT_USERNAME', 'sandbox')
        self.api_key = os.getenv('AT_API_KEY', '')
        self.initialized = False

    def initialize(self):
        try:
            africastalking.initialize(self.username, self.api_key)
            self.sms = africastalking.SMS
            self.ussd = africastalking.USSD
            self.initialized = True
            print("Africa's Talking initialized successfully")
            return True
        except Exception as e:
            print(f"Africa's Talking initialization failed: {e}")
            return False

    def get_sms_service(self):
        if not self.initialized:
            self.initialize()
        return self.sms if self.initialized else None

    def get_ussd_service(self):
        if not self.initialized:
            self.initialize()
        return self.ussd if self.initialized else None

# Global instance
africas_talking_config = AfricaTalkingConfig()