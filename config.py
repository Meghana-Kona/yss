import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'yss-anantapur-spiritual-2026-secret-key-ravi')
    
    # Database Configuration
    database_url = os.environ.get('DATABASE_URL')
    if database_url and database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    
    # Using your PostgreSQL URL as the default fallback
    SQLALCHEMY_DATABASE_URI = database_url or 'postgresql://postgres:meghana@localhost:5432/YSS'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    EXPORTS_DIR = os.path.join(BASE_DIR, 'exports')

    # Flask-Mail config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'ravitejakv777@gmail.com'
    MAIL_PASSWORD = 'lzszxpahybsgxivf'
    MAIL_DEFAULT_SENDER = ('YSS Anantapur', 'ravitejakv777@gmail.com')

    # Event config
    EVENT_NAME = '3-Day Spiritual Program – Anantapur'
    EVENT_DATES = '24 – 26 July 2026'
    EVENT_DATE_RANGE = 'July 24, 25, 26 – 2026'
    EVENT_VENUE = 'Krishna Kala Mandir, Anantapur, Andhra Pradesh'
    EVENT_CONTACT_EMAIL = 'ravitejakv777@gmail.com'
    EVENT_CONTACT_MOBILE = '8019682209'
    EVENT_MAPS_URL = 'https://maps.app.goo.gl/WQxUo86SVYtabmMP9'

    # Admin defaults
    ADMIN_EMAIL = 'ravitejakv777@gmail.com'
    ADMIN_PASSWORD = 'YSS@Ravi2026'
