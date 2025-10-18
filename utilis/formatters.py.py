from datetime import datetime

def format_job_listing(jobs, page=0):
    if not jobs:
        return "No jobs available at the moment. Check back later!"
    
    response_text = "Available Jobs:\n\n"
    for i, job in enumerate(jobs, 1):
        response_text += f"{i}. {job['title']}\n"
        response_text += f"   Location: {job['location']} - {job['company_name']}\n"
        response_text += f"   Payment: K{job['payment_amount']}/{job['payment_type']}\n\n"
    
    response_text += "4. Next Page\n5. Back to Menu\n0. Main Menu"
    return response_text

def format_application_list(applications, page=0):
    if not applications:
        return "You haven't applied to any jobs yet.\n\nBrowse jobs to get started!"
    
    response_text = "Your Applications:\n\n"
    for i, app in enumerate(applications, 1):
        status_text = "Approved" if app['status'] == 'approved' else "Pending" if app['status'] == 'pending' else "Rejected"
        applied_date = app['applied_at'].strftime('%d/%m/%Y') if isinstance(app['applied_at'], datetime) else app['applied_at']
        
        response_text += f"{i}. {app['job_title']}\n"
        response_text += f"   Company: {app['company_name']}\n"
        response_text += f"   Status: {status_text}\n"
        response_text += f"   Date: {applied_date}\n\n"
    
    response_text += "6. Next Page\n7. Previous Page\n0. Main Menu"
    return response_text

def format_employer_jobs(jobs):
    if not jobs:
        return "You haven't posted any jobs yet.\n\nPost a job to find workers!"
    
    response_text = "Your Jobs:\n\n"
    for job in jobs:
        status_text = "Active" if job['status'] == 'active' else "Inactive"
        response_text += f"Title: {job['title']}\n"
        response_text += f"Status: {status_text}\n"
        response_text += f"Applications: {job['application_count']}\n\n"
    
    return response_text

def format_job_applications(applications):
    if not applications:
        return "No applications received yet.\n\nCheck back later!"
    
    response_text = "Recent Applications:\n\n"
    for app in applications:
        applied_date = app['applied_at'].strftime('%d/%m/%Y') if isinstance(app['applied_at'], datetime) else app['applied_at']
        response_text += f"Job: {app['job_title']}\n"
        response_text += f"Applicant: {app['applicant_name']}\n"
        response_text += f"Phone: {app['applicant_phone']}\n"
        response_text += f"Date: {applied_date}\n\n"
    
    response_text += "Contact applicants via their phone numbers above."
    return response_text