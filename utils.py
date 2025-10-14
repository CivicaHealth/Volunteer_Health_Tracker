import smtplib
from email.message import EmailMessage
import config

def send_reminder_email(to_address, subject, body):
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = config.MAIL_USERNAME
    msg['To'] = to_address
    msg.set_content(body)

    try:
        with smtplib.SMTP(config.MAIL_SERVER, config.MAIL_PORT) as server:
            if config.MAIL_USE_TLS:
                server.starttls()
            server.login(config.MAIL_USERNAME, config.MAIL_PASSWORD)
            server.send_message(msg)
        print("Email sent to", to_address)
    except Exception as e:
        print("Error sending email:", e)
if __name__ == "__main__":
    send_reminder_email("Pagkratis@gmail.com", "test1", "the world is flatter than gabe")

