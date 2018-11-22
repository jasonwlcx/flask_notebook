# services/users/project/config.py

class BaseConfig:
    """Base Configuration"""
    TESTING = False

class DevelopmentConfig:
    """Development Configuration"""
    pass

class TestingConfig:
    """Testing Configuration"""
    TESTING = True

class ProductionConfig:
    """Production Configuration"""
    pass
