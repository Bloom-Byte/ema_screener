from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
import djsm



load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))

secret_manager = djsm.get_djsm(quiet=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = secret_manager.get_or_create_secret_key()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

INSTALLED_APPS = [
    # dependencies
    'rest_framework',
    'rest_framework_api_key',
    'rest_framework.authtoken',
    'djsm',
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
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}

DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': os.getenv("DB_NAME"),
       'USER': secret_manager.get_secret("DB_USER"),
       'PASSWORD': secret_manager.get_secret("DB_PASSWORD"),
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


SITE_ID = 1

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

EMAIL_HOST = os.getenv("EMAIL_HOST")

EMAIL_PORT = os.getenv("EMAIL_PORT")

EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "false").lower() == "true"

EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "false").lower() == "true"

EMAIL_HOST_USER = secret_manager.get_secret("EMAIL_HOST_USER")

EMAIL_HOST_PASSWORD = secret_manager.get_secret("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = os.getenv("SERVER_EMAIL")


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50,
}


if DEBUG is False:
    # Production only settings
    # REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
    #     "rest_framework.renderers.JSONRenderer",
    # ]

    REST_FRAMEWORK['DEFAULT_PERMISSION_CLASSES'] = [
        "api.permissions.HasAPIKeyOrIsAuthenticated",
    ]

    ALLOWED_HOSTS = ["*"] # Set to your domain

    CORS_ALLOW_ALL_ORIGINS = False

    CORS_ALLOWED_ORIGINS = ["https://*", "http://*", "ws://*", "wss://*"]

    API_KEY_CUSTOM_HEADER = "HTTP_X_API_KEY" # Request header should have "X-API-KEY" key

else:
    REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [
        "rest_framework.renderers.JSONRenderer",
        "rest_framework.renderers.BrowsableAPIRenderer",
    ]

    CORS_ALLOW_ALL_ORIGINS = True
