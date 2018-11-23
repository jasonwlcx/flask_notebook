# services/users/project/config.py

import os

class BaseConfig:
    """Base Configuration"""
    DEBUG = False
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'secret_key'

class DevelopmentConfig:
    """Development Configuration"""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

class TestingConfig:
    """Testing Configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')

class ProductionConfig:
    """Production Configuration"""
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
