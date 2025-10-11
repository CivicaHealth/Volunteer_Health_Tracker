import os

# Flask secret key for session management
SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-secret-key')

# Email settings (using Gmail SMTP for demo)
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')  # Set in environment!
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# Other app settings can go here
DEFAULT_NOTIFICATION_EMAIL = os.environ.get('NOTIFY_EMAIL', 'pagkratis@gmail.com')
