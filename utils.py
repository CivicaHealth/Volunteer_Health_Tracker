import smtplib
from email.message import EmailMessage
from config import MAIL_SERVER, MAIL_PORT, MAIL_USE_TLS, MAIL_USERNAME, MAIL_PASSWORD

def send_reminder_email(to_address, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = MAIL_USERNAME
    msg['To'] = to_address
    msg.set_content(body)

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            if MAIL_USE_TLS:
                server.starttls()
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent to", to_address)
    except Exception as e:
        print("Error sending email:", e)
