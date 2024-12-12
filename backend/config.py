import os
from urllib.parse import quote_plus

password = ")_W#laodbu#60*4"
encoded_password = quote_plus(password)

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tis_be_our_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL', 
        f'mysql+pymysql://moneytracker:{encoded_password}@sgp.domcloud.co/moneytracker_db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
