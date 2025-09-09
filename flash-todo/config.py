import os
from datetime import timedelta

class Config:
    """基础配置类"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DATABASE = os.environ.get('DATABASE') or 'todo.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SESSION_COOKIE_SECURE = False  # 开发环境设为False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 应用配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    UPLOAD_FOLDER = 'uploads'
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    
    # 分页配置
    TODOS_PER_PAGE = 20
    
    # 缓存配置
    CACHE_TYPE = 'simple'
    CACHE_DEFAULT_TIMEOUT = 300
    
    # 日志配置
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'todo_app.log'

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # 生产环境安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("No SECRET_KEY set for production environment")

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DEBUG = True
    DATABASE = 'test_todo.db'
    WTF_CSRF_ENABLED = False

# 配置映射
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 