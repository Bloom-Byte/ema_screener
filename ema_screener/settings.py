from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
from typing import Union
from corsheaders.defaults import default_headers


load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

INSTALLED_APPS = [
    # dependencies
    'rest_framework',
    'rest_framework_api_key',
    'corsheaders',
    "channels",
    "daphne",

    # django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # apps
    'ema.apps.EmaConfig',
    'currency.apps.CurrencyConfig',
    'users.apps.UsersConfig',
    'tokens.apps.TokensConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ema_screener.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'ema_screener.wsgi.application'

ASGI_APPLICATION = 'ema_screener.asgi.application'

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv("REDIS_SERVICE_HOST"), 6379)],
        },
    },
}

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': os.getenv("DB_NAME"),
       'USER': os.getenv("DB_USER"),
       'PASSWORD': os.getenv("DB_PASSWORD"),
       'HOST': os.getenv("DB_HOST"),
       'PORT': os.getenv("DB_PORT"),
   }
}


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

AUTH_USER_MODEL = 'users.UserAccount'

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# SITE SETTINGS

SITE_ID = 1

# The name of the web application
SITE_NAME = os.getenv("SITE_NAME")

# The base URL of the web application
PASSWORD_RESET_URL = os.getenv("PASSWORD_RESET_URL")


STATIC_URL = 'static/'

STATIC_ROOT = os.path.join(BASE_DIR, "static")

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# EMAIL SETTINGS

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv("EMAIL_HOST")

EMAIL_PORT = os.getenv("EMAIL_PORT")

EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "false").lower() == "true"

EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL")

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_PERMISSION_CLASSES': [
        "api.permissions.HasAPIKey",
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [],
}

API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY" # Request header should have "X-API-KEY" key

CORS_ALLOW_HEADERS = (*default_headers, 'x-api-key')

def _parse_validity_period(period: Union[str, int]) -> int:
    """
    Converts a password reset token validity period in hours to a valid value.

    If the value set is not valid, a default of 24.
    """
    try:
        return int(period)
    except (ValueError, TypeError):
        return 24

PASSWORD_RESET_TOKEN_VALIDITY_PERIOD = _parse_validity_period(os.getenv("PASSWORD_RESET_TOKEN_VALIDITY_PERIOD"))

CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = ["https://*.emascreener.bloombyte.dev", "http://*"]

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')


if DEBUG is False:
    # Production only settings
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
    ]

    ALLOWED_HOSTS = ["be.emascreener.bloombyte.dev"] # Set to your domain

else:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]

    ALLOWED_HOSTS = ["*"]
