import re

def validate_phone_number(phone):
    pattern = r'^\+260(9|7)[0-9]{8}$'
    return bool(re.match(pattern, phone))

def validate_payment_amount(amount):
    try:
        return float(amount) > 0
    except (ValueError, TypeError):
        return False

def validate_name(name):
    if not name or len(name.strip()) < 2:
        return False
    return True

def validate_location(location):
    if not location or len(location.strip()) < 2:
        return False
    return True

def validate_skills(skills):
    if not skills or len(skills.strip()) < 2:
        return False
    return True

def validate_company_name(company_name):
    if not company_name or len(company_name.strip()) < 2:
        return False
    return True

def validate_business_type(business_type):
    if not business_type or len(business_type.strip()) < 2:
        return False
    return True

def validate_job_title(title):
    if not title or len(title.strip()) < 2:
        return False
    return True

def validate_job_description(description):
    if not description or len(description.strip()) < 10:
        return False
    return True