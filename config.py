import os

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key'
    UPLOAD_FOLDER = 'static/uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max upload
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE = 'database.db'

class ProductionConfig(Config):
    DEBUG = False
    DATABASE = os.environ.get('DATABASE_PATH') or 'database.db'
    # 生产环境应使用更强的密钥
    SECRET_KEY = os.environ.get('SECRET_KEY')
    # 安全设置
    SESSION_COOKIE_SECURE = False  # 仅通过HTTPS发送cookie，本地环境设为False
    SESSION_COOKIE_HTTPONLY = True  # 防止JavaScript访问cookie
    PERMANENT_SESSION_LIFETIME = 3600  # 会话过期时间（秒）

# 根据环境变量选择配置
config = {
    'development': DevelopmentConfig,
    'production': DevelopmentConfig,
    'default': DevelopmentConfig
}