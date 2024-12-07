import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'tis_be_our_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'mysql+pymysql://moneytracker:)_E7bn9MAuk2F3uN1-@sgp.domcloud.co/moneytracker_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
