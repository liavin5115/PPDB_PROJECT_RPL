import os
from datetime import timedelta

class Config:
    SECRET_KEY = 'your-secret-key-here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ppdb.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False