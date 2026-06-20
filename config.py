import os

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///expense_manager.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    JSON_SORT_KEYS = False
