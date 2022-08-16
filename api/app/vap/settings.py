from pathlib import Path
from datetime import timedelta as td
from os import environ
from corsheaders.defaults import default_headers

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-+aab4(s^z#4f^3cfdv3*9m5zvrqq-kw62&k+i2t1nak*&#n+k3'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# We use our own user model
AUTH_USER_MODEL = 'users.User'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users',
    'django_filters',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    # 'rest_framework.authtoken',
    'django_mkdocs',
    'simple_history',
    'phonenumber_field',
    'export_app',
    'drf_multiple_model',
    'drf_auto_endpoint',
    'vap',
    'core',
    'importer'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'vap.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'vap.wsgi.application'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Zurich'
USE_I18N = True
USE_L10N = True
USE_TZ = True

STATIC_URL = '/static/'
MEDIA_URL = '/media/'

MEDIA_ROOT = '/vol/web/media'
STATIC_ROOT = '/vol/web/static'

DISABLE_AUTH = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': environ.get('POSTGRES_DB'),
        'USER': environ.get('POSTGRES_USER'),
        'PASSWORD': environ.get('POSTGRES_PASSWORD'),
        'HOST': environ.get('POSTGRES_HOST'),
        'PORT': environ.get('POSTGRES_PORT'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        # 'rest_framework.authentication.TokenAuthentication',
        # 'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',
        'rest_framework.permissions.IsAuthenticated'
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'core.backends.DynamicSearchFilter'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 1000,
    'DEFAULT_METADATA_CLASS': 'drf_auto_endpoint.metadata.AutoMetadata',
    'TEST_REQUEST_DEFAULT_FORMAT': 'json',
}

### Authentication stuff ###
if DISABLE_AUTH:
    REST_FRAMEWORK.update({
        'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework.permissions.IsAuthenticated',),
        # 'DEFAULT_PERMISSION_CLASSES': ('rest_framework_jwt.authentication.JSONWebTokenAuthentication',),
    })

FIXTURE_DIRS = []

### JWT ###
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': td(minutes=30),
    'REFRESH_TOKEN_LIFETIME': td(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    'UPDATE_LAST_LOGIN': False,

    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,

    'AUTH_HEADER_TYPES': ('Bearer', 'JWT'),
    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'rest_framework_simplejwt.models.TokenUser',
    # We overwrite the token obtain serializer to support OTP
    'TOKEN_OBTAIN_SERIALIZER': 'users.serializers.TokenObtainPair2FASerializer',

    'JTI_CLAIM': 'jti',

    # 'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    # 'SLIDING_TOKEN_LIFETIME': td(minutes=30),
    # 'SLIDING_TOKEN_REFRESH_LIFETIME': td(days=1),
}

# JWT_AUTH = {
#     # 'JWT_ENCODE_HANDLER': 'rest_framework_jwt.utils.jwt_encode_handler',
#     # 'JWT_DECODE_HANDLER': 'rest_framework_jwt.utils.jwt_decode_handler',
#     # 'JWT_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_payload_handler',
#     # 'JWT_PAYLOAD_GET_USER_ID_HANDLER': 'rest_framework_jwt.utils.jwt_get_user_id_from_payload_handler',
#     # 'JWT_RESPONSE_PAYLOAD_HANDLER': 'rest_framework_jwt.utils.jwt_response_payload_handler',
#     'JWT_VERIFY': True,
#     'JWT_VERIFY_EXPIRATION': True,
#     'JWT_AUTH_HEADER_PREFIX': 'JWT',
#     'JWT_ALLOW_REFRESH': True,
#     'JWT_EXPIRATION_DELTA': td(hours=1),
#     'JWT_REFRESH_EXPIRATION_DELTA': td(days=7),
# }

### Mkdocs config ###
PROJECT_DIR = str(BASE_DIR)
DOCUMENTATION_ROOT = PROJECT_DIR + '/docs'
DOCUMENTATION_HTML_ROOT = DOCUMENTATION_ROOT + '/site'
DOCUMENTATION_XSENDFILE = False
def DOCUMENTATION_ACCESS_FUNCTION(_): return True

###
# SECURITY
###

ALLOWED_HOSTS = environ.get('DJANGO_ALLOWED_HOSTS').split(',')

# CORS configuration
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = environ.get('DJANGO_CORS_ALLOWED_ORIGINS').split(',')
CORS_ALLOW_HEADERS = default_headers + ('cache-control', 'pragma', 'expires')
CORS_ALLOW_CREDENTIALS = True

# CSRF configuration
CSRF_TRUSTED_ORIGINS = environ.get('DJANGO_CSRF_TRUSTED_ORIGINS').split(',')

# Config API
CONFIG_DIR = '/config'
USE_CONFIG = 'default'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = environ.get('EMAIL_HOST')
EMAIL_PORT = environ.get('EMAIL_PORT')
EMAIL_HOST_USER = environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = (environ.get('EMAIL_USE_TLS', 'False') == 'True')
EMAIL_FROM = environ.get('EMAIL_FROM')