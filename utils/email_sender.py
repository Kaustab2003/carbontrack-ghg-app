# utils/email_sender.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os

def send_email_report(recipient, subject, body, attachment_path):
    sender = "kaustabdas2003@gmail.com"  # 🔁 Replace with your actual Gmail address
    password = "Sanu22003"   # 🔁 Use your Gmail App Password (not regular password)

    # Setup MIME message
    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject

    # Add email body
    msg.attach(MIMEText(body, "plain"))

    # Add PDF attachment
    with open(attachment_path, "rb") as f:
        part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(attachment_path)}"'
        msg.attach(part)

    # Send the email using Gmail SMTP server
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)

    print(f"✅ Email sent successfully to {recipient}")
