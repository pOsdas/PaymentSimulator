from pathlib import Path
import logging.config
import environ
from app.config import pydantic_settings

env = environ.Env()

DOCKER = env.bool("DOCKER", False)

# Корневая директория проекта
BASE_DIR = Path(__file__).resolve().parent

# Основные настройки
SECRET_KEY = pydantic_settings.secret_key
DEBUG = pydantic_settings.debug
ALLOWED_HOSTS = env.str("ALLOWED_HOSTS", "127.0.0.1,localhost").split(",")


# Настройка базы данных
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': env.str('POSTGRES_DB'),
        'USER': env.str('POSTGRES_USER'),
        'PASSWORD': env.str('POSTGRES_PASSWORD'),
        'HOST': env.str('POSTGRES_HOST') if DOCKER else 'localhost',
        'PORT': env.str('POSTGRES_PORT')
    }
}

# DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql_async"
DATABASES["default"]["ENGINE"] = "django.db.backends.postgresql"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Настройка Redis
REDIS_HOST = env.str("REDIS_HOST", "localhost") if DOCKER else '127.0.0.1'
REDIS_PORT = env.str("REDIS_PORT", "6379")  # if DOCKER else '127.0.0.1:6379'
REDIS_DB = env.str("REDIS_DB", "1")
REDIS_DECODE_RESPONSES = True

# TTL для redis
CATALOG_CACHE_TTL = 60 * 60  # 1 час
SMART_PROCESSES_CACHE_TTL = 60 * 20  # 20 минут
ALAN_ACCESS_TTL = 60 * 60 * 24  # День

# Настройка Celery
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL")  # f"redis://{_REDIS_HOST}:{_REDIS_PORT}/{REDIS_DB}"
CELERY_RESULT_BACKEND = env.str("CELERY_BROKER_URL")  # f"redis://{_REDIS_HOST}:{_REDIS_PORT}/{REDIS_DB}"
CELERY_BEAT_SCHEDULE = {
}

# Установленные приложения
INSTALLED_APPS = [
    'app',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework.authtoken',
    'drf_spectacular',
    'rest_framework',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'app_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ASGI_APPLICATION = 'app_project.asgi.application'
WSGI_APPLICATION = 'app_project.wsgi.application'

# Статические файлы
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'static'

# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.TokenAuthentication"
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        "rest_framework.permissions.IsAuthenticated",
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

AUTH_USER_MODEL = "app.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
            "log_colors": {
                "DEBUG": "cyan",
                "INFO": "white",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "bold_red",
            },
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "fmt": "%(levelname)s %(name)s %(message)s %(asctime)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "colored" if DEBUG else "json",
            "level": "DEBUG",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

logging.config.dictConfig(LOGGING)