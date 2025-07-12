import os
from .settings import *
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 🔍 调试信息：打印环境变量
print("🔧 数据库环境变量调试信息:")
print(f"DATABASE_HOST: {os.getenv('DATABASE_HOST', 'db')}")
print(f"DATABASE_NAME: {os.getenv('DATABASE_NAME', 'DataSystem')}")
print(f"DATABASE_USER: {os.getenv('DATABASE_USER', 'root')}")
print(f"DATABASE_PORT: {os.getenv('DATABASE_PORT', '3306')}")

# 生产环境配置 - 临时开启DEBUG确保管理后台样式正常
DEBUG = True  # 修复：临时开启DEBUG模式

# 允许的主机
ALLOWED_HOSTS = ['*']  # 临时允许所有主机用于调试

# 数据库配置 - 修复版本
DATABASES = {
    'default': {
        'ENGINE': os.getenv('DATABASE_ENGINE', 'django.db.backends.mysql'),
        'NAME': os.getenv('DATABASE_NAME', 'DataSystem'),
        'USER': os.getenv('DATABASE_USER', 'root'),
        'PASSWORD': os.getenv('DATABASE_PASSWORD', '1997yx0912'),
        'HOST': os.getenv('DATABASE_HOST', 'db'),  # 确保连接到Docker容器
        'PORT': os.getenv('DATABASE_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            # 添加连接配置确保数据一致性
            'autocommit': True,
        },
        # 连接池配置 - 确保数据库连接稳定
        'CONN_MAX_AGE': 0,  # 每次请求都使用新连接
        'CONN_HEALTH_CHECKS': True,
    }
}

# 🔍 调试信息：打印最终数据库配置
print("🔧 最终数据库配置:")
print(f"HOST: {DATABASES['default']['HOST']}")
print(f"NAME: {DATABASES['default']['NAME']}")
print(f"PORT: {DATABASES['default']['PORT']}")

# 安全密钥
SECRET_KEY = os.getenv('SECRET_KEY', 'django-insecure-yy)&3!0l7+6^!-sf9n_0=ee0g--^&l4+sy*5ruf*lfrz^02h^v')

# 静态文件配置
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 媒体文件配置
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# CORS配置 - 允许跨域但支持CSRF
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF配置 - 正确配置CSRF保护
CSRF_COOKIE_SECURE = False  # 开发环境用HTTP
CSRF_COOKIE_HTTPONLY = False  # 允许JavaScript访问
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_HEADER_NAME = 'HTTP_X_CSRFTOKEN'
CSRF_TRUSTED_ORIGINS = [
    'http://localhost:8080',
    'http://127.0.0.1:8080',
    'http://localhost',
    'http://127.0.0.1',
]

# 修复：添加WhiteNoise中间件到MIDDLEWARE配置
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # 添加WhiteNoise中间件
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# REST Framework配置
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',  # 临时保持AllowAny
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
    ],
}

# 安全配置
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

# 日志配置
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
} 