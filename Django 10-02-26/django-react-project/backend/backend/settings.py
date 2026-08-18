"""
Django settings for backend project.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------
# SECURITY
# ---------------------------------------------------------------------
SECRET_KEY = "django-insecure-q7$*418t187n9asdp5^iqis_bcu93z9n+u^7_-6sogcnt8wb7z"
DEBUG = True
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# ---------------------------------------------------------------------
# APPLICATIONS
# ---------------------------------------------------------------------
INSTALLED_APPS = [
    "corsheaders",
    "rest_framework",
    "api",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

# ---------------------------------------------------------------------
# MIDDLEWARE  (order is critical)
# ---------------------------------------------------------------------
MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",   # ✅ before Common
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",  # ✅ next to Session
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ---------------------------------------------------------------------
# ROOT & TEMPLATES
# ---------------------------------------------------------------------
ROOT_URLCONF = "backend.urls"

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

WSGI_APPLICATION = "backend.wsgi.application"

# ---------------------------------------------------------------------
# DATABASE
# ---------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "signup",
        "USER": "root",
        "PASSWORD": "",
        "HOST": "127.0.0.1",
        "PORT": "3306",
    }
}

# ---------------------------------------------------------------------
# PASSWORD VALIDATORS
# ---------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ---------------------------------------------------------------------
# INTERNATIONALIZATION
# ---------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------------------
# STATIC FILES
# ---------------------------------------------------------------------
STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------
# ✅  CORS + CSRF + SESSION CONFIG  (FINAL VERIFIED)
# ---------------------------------------------------------------------

# React frontend = 127.0.0.1:3000, Django backend = 127.0.0.1:8000
CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:3000",
]

CSRF_TRUSTED_ORIGINS = [
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True  # allow cookies/session sharing across origins

# Session Cookie Config for cross‑port localhost
SESSION_COOKIE_SAMESITE = "None"   # required for cross‑origin cookies
SESSION_COOKIE_SECURE = False      # True only for HTTPS
SESSION_COOKIE_HTTPONLY = True

# CSRF Cookie Config — must match session behavior
CSRF_COOKIE_SAMESITE = "None"
CSRF_COOKIE_SECURE = False
CSRF_COOKIE_HTTPONLY = False       # False to allow React to read token if ever needed

# Extend session lifetime: valid for 1 day
SESSION_COOKIE_AGE = 60 * 60 * 24      # 1 day in seconds
SESSION_EXPIRE_AT_BROWSER_CLOSE = False