import re
import smtplib
from email.mime.text import MIMEText
from langchain.tools import tool
from config import EMAIL_ADDRESS, EMAIL_PASSWORD

EMAIL = EMAIL_ADDRESS
PASSWORD = EMAIL_PASSWORD

EMAIL_REGEX = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"


def template(name, doctor, time):
    """
    Appointment confirmation email template.
    """
    return f"""
    <h2>Appointment Confirmed</h2>
    <p><b>Patient:</b> {name}</p>
    <p><b>Doctor:</b> {doctor}</p>
    <p><b>Time:</b> {time}</p>
    """
def reschedule_template(name, doctor, old_time, new_time):
    """
    Appointment reschedule email template.
    """
    return f"""
    <h2>Appointment Rescheduled</h2>

    <p>Dear {name},</p>

    <p>
    Your appointment with <b>Dr. {doctor}</b> has been rescheduled
    because an urgent critical patient required immediate medical attention.
    </p>

    <p><b>Previous Time:</b> {old_time}</p>
    <p><b>New Time:</b> {new_time}</p>

    <p>
    We apologize for the inconvenience and appreciate your understanding.
    </p>
    """
@tool
def send_email(email: str, patient_name: str, doctor_name: str, appointment_time: str):
    """
    Sends appointment confirmation email after booking.
    """

    if not email or not re.match(EMAIL_REGEX, email):
        return "ERROR: Invalid email address"

    try:
        msg = MIMEText(
            template(patient_name, doctor_name, appointment_time),
            "html"
        )

        msg["Subject"] = "Appointment Confirmation"
        msg["From"] = EMAIL
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()

        return "Email sent successfully"

    except Exception as e:
        return f"Email failed: {str(e)}"


def send_reschedule_email(
    email: str,
    patient_name: str,
    doctor_name: str,
    old_time: str,
    new_time: str
):
    """
    Sends appointment reschedule notification email.
    """

    if not email or not re.match(EMAIL_REGEX, email):
        return "ERROR: Invalid email address"

    try:
        msg = MIMEText(
            reschedule_template(
                patient_name,
                doctor_name,
                old_time,
                new_time
            ),
            "html"
        )

        msg["Subject"] = "Appointment Rescheduled"
        msg["From"] = EMAIL
        msg["To"] = email

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(EMAIL, PASSWORD)
        server.sendmail(EMAIL, email, msg.as_string())
        server.quit()

        return "Reschedule email sent successfully"

    except Exception as e:
        return f"Reschedule email failed: {str(e)}"