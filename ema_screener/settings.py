from pathlib import Path
import os
from dotenv import load_dotenv, find_dotenv
import djsm



load_dotenv(find_dotenv(".env", raise_error_if_not_found=True))

secret_manager = djsm.get_djsm(quiet=True)

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = secret_manager.get_or_create_secret_key()

DEBUG = os.getenv("DEBUG", "false").lower() == "true"

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # dependencies
    'rest_framework',
    'djsm',
    'corsheaders',

    # apps
    'ema.apps.EmaConfig',
    'currency.apps.CurrencyConfig'
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


DATABASES = {
   'default': {
       'ENGINE': 'django.db.backends.postgresql',
       'NAME': secret_manager.get_secret("DB_NAME"),
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



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True



STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 50
}
