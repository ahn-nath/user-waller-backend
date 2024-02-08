import json
import os
from pathlib import Path

import environ

ENVIRONMENT = environ.Env(
    # set casting, default value
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

environ.Env.read_env(os.path.join(BASE_DIR.parent, ".env"))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ENVIRONMENT("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = ENVIRONMENT("DJANGO_DEBUG")


ALLOWED_HOSTS = ENVIRONMENT("ALLOWED_HOSTS", cast=json.loads)


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_yasg",
    "phonenumber_field",
    "apps.wallet",
    "apps.users",
    "apps.auth_xp",
    "apps.kyc",
    "django_dbml",
    "django_extensions",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "project.middleware.RequestResponseLoggingMiddleware",
    "project.middleware.JWTAuthenticationMiddleware",
]

ROOT_URLCONF = "project.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "project.wsgi.application"

# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": ENVIRONMENT("DATABASE_NAME"),
        "USER": ENVIRONMENT("DATABASE_USER"),
        "PASSWORD": ENVIRONMENT("DATABASE_PASSWORD"),
        "HOST": ENVIRONMENT("DATABASE_HOST"),
        "PORT": ENVIRONMENT("DATABASE_PORT"),
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "static"

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Users
AUTH_USER_MODEL = "users.XPUser"

# Auth
# USE_SESSION_AUTH = True  # ? for drf-yasg
LOGIN_URL = "/auth/login/"  # URL to redirect to if the user isn't logged in.
LOGIN_REDIRECT_URL = "/auth/"  # URL to redirect to after a successful login.
LOGOUT_REDIRECT_URL = "/auth/"  # URL to redirect to after a successful logout.

# DRF-YASG (swagger)
SWAGGER_SETTINGS = {
    "LOGOUT_URL": "/auth/logout/",
}

# DRF SETTINGS
# https://www.django-rest-framework.org/
REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
}

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": ENVIRONMENT("DJANGO_LOGS_FILE_PATH"),
        },
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            # "formatter": "simple",
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
        # logger for the app
        "apps.wallet": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

# Graph models conf
GRAPH_MODELS = {
    "all_applications": True,
    "group_models": True,
    "output": "ERD.png",
    "exclude_models": ",".join(
        [
            # "User",
            # "AbstractUser",
            # "Group",
            # "Permission",
            "ContentType",
            "LogEntry",
            "Session",
            "AbstractBaseSession",
            # "Token",
        ]
    ),
}

# JWT
SIMPLE_JWT = {
    "ALGORITHM": "HS256",
    "SIGNING_KEY": ENVIRONMENT("JWT_SIGNING_KEY"),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
}

COOKIE_NAME_ACCESS_TOKEN = "access_token"
COOKIE_NAME_REFRESH_TOKEN = "refresh_token"

# Magic link
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "sesame.backends.ModelBackend",
]

SESAME_MAX_AGE = 300
SESAME_TOKEN_NAME = "hash"

# SENDGRID
SENDGRID_FROM_EMAIL = ENVIRONMENT("SENDGRID_FROM_EMAIL")
SENDGRID_API_KEY = ENVIRONMENT("SENDGRID_API_KEY")
SENDGRID_DOMAIN = ENVIRONMENT("SENDGRID_DOMAIN")
