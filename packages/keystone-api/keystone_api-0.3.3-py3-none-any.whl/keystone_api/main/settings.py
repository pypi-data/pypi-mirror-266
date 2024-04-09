"""Top level Django application settings."""

import importlib.metadata
import os
import sys
from datetime import timedelta
from pathlib import Path

import environ
from django.core.management.utils import get_random_secret_key

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Application metadata

dist = importlib.metadata.distribution('keystone-api')
VERSION = dist.metadata['version']
SUMMARY = dist.metadata['summary']

# Developer settings

env = environ.Env()
DEBUG = env.bool('DEBUG', False)
FIXTURE_DIRS = [BASE_DIR / 'tests' / 'fixtures']

# Core security settings

SECRET_KEY = os.environ.get('SECURE_SECRET_KEY', get_random_secret_key())
ALLOWED_HOSTS = env.list("SECURE_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

_SECURE_SESSION_TOKENS = env.bool("SECURE_SESSION_TOKENS", False)
SESSION_COOKIE_SECURE = _SECURE_SESSION_TOKENS
CSRF_COOKIE_SECURE = _SECURE_SESSION_TOKENS
CSRF_TRUSTED_ORIGINS = env.list("SECURE_CSRF_ORIGINS", default=[])

SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", False)
SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", False)
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", 0)
SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_SUBDOMAINS", False)

CORS_ORIGIN_ALLOW_ALL = True

# App Configuration

ROOT_URLCONF = 'main.urls'
LOGIN_REDIRECT_URL = '/'
SITE_ID = 1

INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',
    'health_check',
    'health_check.db',
    'health_check.storage',
    'health_check.contrib.migrations',
    'health_check.contrib.celery',
    'health_check.contrib.celery_ping',
    'health_check.contrib.redis',
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'django_celery_beat',
    'django_celery_results',
    'django_filters',
    'drf_spectacular',
    'apps.admin_utils',
    'apps.allocations',
    'apps.docs',
    'apps.health',
    'apps.logging',
    'apps.scheduler',
    'apps.users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'apps.logging.middleware.LogRequestMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
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

# Base styling for the Admin UI

JAZZMIN_SETTINGS = {
    "site_title": "Keystone",
    "site_header": "Keystone",
    "site_brand": "Keystone",
    "hide_apps": ["sites", "auth", "token_blacklist"],
    "order_with_respect_to": [
        "users",
        "allocations",
        "research_products",
        "sites"
    ],
    "icons": {},
    "login_logo": "fake/file/path.jpg",  # Missing file path hides the logo
}

# REST API settings

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': env.str('API_THROTTLE_ANON', '1000/day'),
        'user': env.str('API_THROTTLE_USER', '10000/day')
    },
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
    ),
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}

# Customize the generation of OpenAPI specifications

SPECTACULAR_SETTINGS = {
    'TITLE': f'Keystone API',
    'DESCRIPTION': SUMMARY,
    'VERSION': VERSION,
    'SERVE_INCLUDE_SCHEMA': False,
}

# Redis backend and Celery scheduler

_redis_host = env.url('REDIS_HOST', '127.0.0.1').geturl()
_redis_port = env.int('REDIS_PORT', 6379)
_redis_db = env.int('REDIS_DB', 0)
_redis_pass = env.str('REDIS_PASSWORD', '')

REDIS_URL = f'redis://:{_redis_pass}@{_redis_host}:{_redis_port}'

CELERY_BROKER_URL = REDIS_URL + f'/{_redis_db}'
CELERY_CACHE_BACKEND = 'django-cache'
CELERY_RESULT_BACKEND = 'django-db'
CELERY_RESULT_EXTENDED = True

# Database

DATABASES = dict()
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

_db_name = env.str('DB_NAME', 'keystone')
if env.bool('DB_POSTGRES_ENABLE', False):
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': _db_name,
        'USER': env.str('DB_USER', ''),
        'PASSWORD': env.str('DB_PASSWORD', ''),
        'HOST': env.str('DB_HOST', 'localhost'),
        'PORT': env.str('DB_PORT', '5432'),
    }

else:
    DATABASES['default'] = {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / f'{_db_name}.db',
        'timeout': 30,
    }

# Authentication

AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["django.contrib.auth.backends.ModelBackend"]

if AUTH_LDAP_SERVER_URI := env.url("AUTH_LDAP_SERVER_URI", "").geturl():
    import ldap
    from django_auth_ldap.config import LDAPSearch

    AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

    AUTH_LDAP_ALWAYS_UPDATE_USER = True
    AUTH_LDAP_START_TLS = env.bool("AUTH_LDAP_START_TLS", True)
    AUTH_LDAP_BIND_DN = env.str("AUTH_LDAP_BIND_DN", "")
    AUTH_LDAP_BIND_PASSWORD = env.str("AUTH_LDAP_BIND_PASSWORD", "")
    AUTH_LDAP_USER_ATTR_MAP = env.dict('AUTH_LDAP_ATTR_MAP', default=dict())
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        env.str("AUTH_LDAP_USER_SEARCH", ""),
        ldap.SCOPE_SUBTREE,
        "(uid=%(user)s)"
    )

    if env.bool('AUTH_LDAP_REQUIRE_CERT', False):
        AUTH_LDAP_GLOBAL_OPTIONS = {ldap.OPT_X_TLS_REQUIRE_CERT: ldap.OPT_X_TLS_NEVER}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Static file handling (CSS, JavaScript, Images)

STATIC_URL = 'static/'
STATIC_ROOT = Path(env.path('CONFIG_STATIC_DIR', BASE_DIR / 'static_files'))
STATIC_ROOT.mkdir(parents=True, exist_ok=True)

MEDIA_URL = 'uploads/'
MEDIA_ROOT = Path(env.path('CONFIG_UPLOAD_DIR', BASE_DIR / 'upload_files'))
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)

# Timezones

USE_TZ = True
CELERY_ENABLE_UTC = True
DJANGO_CELERY_BEAT_TZ_AWARE = True
TIME_ZONE = env.str('CONFIG_TIMEZONE', 'UTC')

# Logging

LOG_RECORD_ROTATION = env.int('CONFIG_LOG_RETENTION', timedelta(days=30).total_seconds())
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "db": {
            "class": "apps.logging.handlers.DBHandler",
        }
    },
    "loggers": {
        "": {
            "level": env.str('CONFIG_LOG_LEVEL', 'WARNING'),
            "handlers": ["db"],
        },
    }
}
