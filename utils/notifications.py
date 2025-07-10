import os
from twilio.rest import Client

def format_student_report(student_data):
    """
    Takes the student_data dictionary and formats it into a human-readable report.
    (This function remains the same as before).
    """
    if not student_data:
        return "No student data available to generate a report."

    profile = student_data.get('profile', {})
    financials = student_data.get('financials', {})
    attendance = student_data.get('attendance', [])
    
    lowest_attendance_course = None
    if attendance:
        try:
            lowest_attendance_course = min(attendance, key=lambda x: float(x.get('percentage', 100)))
        except (ValueError, TypeError):
            lowest_attendance_course = None

    report = f"""
*🎓 Superior University Academic Report 🎓*

Hello, this is an automated report for:
*Student:* {profile.get('student_name', 'N/A')}
*Semester:* {profile.get('semester', 'N/A')}

*📊 Academic Summary:*
- *Current CGPA:* {profile.get('cgpa', 'N/A')}
- *Academic Standing:* {profile.get('academic_standing', 'N/A')}
"""
    if lowest_attendance_course:
        report += f"""
*📈 Attendance Highlight:*
- *Lowest Attendance:* {lowest_attendance_course.get('course_name', 'N/A')} at *{lowest_attendance_course.get('percentage', 'N/A')}%*
"""
    report += f"""
*💰 Financials:*
- *Remaining Balance:* {financials.get('total_remaining_balance', 'N/A')}

Please log in to the student portal for a full breakdown.
_This is an automated message._
"""
    return report.strip()



def send_twilio_whatsapp_report(student_data):
    """
    Sends a report using a pre-approved Twilio Content Template.
    This is more reliable and can be sent outside the 24-hour window.
    """
    # 1. Get Credentials
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number_raw = os.getenv("TWILIO_WHATSAPP_NUMBER")
    recipient_phone_number = os.getenv("PARENT_WHATSAPP_NUMBER")

    if not all([account_sid, auth_token, twilio_number_raw, recipient_phone_number]):
        return {"error": "Twilio credentials or parent number are not configured."}

    # 2. Format Numbers
    formatted_from_number = f"whatsapp:{twilio_number_raw}"
    formatted_to_number = f"whatsapp:{recipient_phone_number}"

    # 3. Extract key info from student data for the template
    profile = student_data.get('profile', {})
    student_name = profile.get('student_name', 'N/A').split()[0] # Get first name
    cgpa = profile.get('cgpa', 'N/A')

    try:
        client = Client(account_sid, auth_token)
        
        # 4. Send the message using a Content Template
        message = client.messages.create(
            from_=formatted_from_number,
            to=formatted_to_number,
            # This is the standard Sandbox Template SID for appointments
            content_sid='HXb5b62575e6e4ff6129ad7c8efe1f983e',
            # We will creatively fill the variables with our student data
            content_variables=f'{{"1": "{student_name}", "2": "CGPA is {cgpa}"}}'
        )
        
        print(f"Template message sent successfully. SID: {message.sid}")
        return {"success": f"Report summary sent to {recipient_phone_number} successfully!"}
        
    except Exception as e:
        error_msg = f"Failed to send template message via Twilio. Error: {e}"
        print(error_msg)
        return {"error": error_msg}