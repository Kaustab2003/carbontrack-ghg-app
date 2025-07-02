import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

EMAIL_CONFIG = {
    'sender': os.getenv('EMAIL_SENDER', 'your_email@example.com'),
    'password': os.getenv('EMAIL_PASSWORD', 'your_email_password'),
    'smtp_server': os.getenv('SMTP_SERVER', 'smtp.example.com'),
    'smtp_port': int(os.getenv('SMTP_PORT', 587))
}

def send_email(to_email, subject, body, attachment=None):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['sender']
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if attachment:
        part = MIMEApplication(attachment, Name="prediction_report.pdf")
        part['Content-Disposition'] = 'attachment; filename="prediction_report.pdf"'
        msg.attach(part)

    with smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port']) as server:
        server.starttls()
        server.login(EMAIL_CONFIG['sender'], EMAIL_CONFIG['password'])
        server.send_message(msg)
