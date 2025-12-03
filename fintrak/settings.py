"""
Django settings for fintrak project.
"""

from pathlib import Path
import os
import dj_database_url # We'll need this for production database if you switch from sqlite

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CORE SECURITY AND DEBUG SETTINGS ---

# SECRET_KEY: Use environment variable in production
SECRET_KEY = os.environ.get(
    'SECRET_KEY', 
    'django-insecure-!gpcd-r7$%s6f@jel34v*-xmfr%2ss*97u_u1s=spjz8myope!' # Fallback for local testing
)

# DEBUG: Set to False automatically by Koyeb unless overridden by env variable
# This is crucial for security!
DEBUG = os.environ.get('DEBUG', 'True') == 'True'


# ALLOWED_HOSTS: Allow Koyeb's public domain for deployment
ALLOWED_HOSTS = [
    "127.0.0.1",
    "localhost",
    # Koyeb automatically sets this environment variable
    os.environ.get('KOYEB_PUBLIC_DOMAIN', ''),
]

# CSRF_TRUSTED_ORIGINS: Only needed if you run on external domains like ngrok
CSRF_TRUSTED_ORIGINS = [
    "https://*.ngrok-free.dev",
    "https://*.ngrok-free.app",
    # Add your Koyeb domain here to be safe (it should already be covered by ALLOWED_HOSTS)
    "https://" + os.environ.get('KOYEB_PUBLIC_DOMAIN', ''),
]


# --- APPLICATION DEFINITION ---

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

# This is the corrected, ordered list to fix all your middleware errors (Session, CSRF)
MIDDLEWARE = [
    # Whitenoise must be first for security and efficiency
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    
    # Session and CSRF are mandatory for login/forms
    'django.contrib.sessions.middleware.SessionMiddleware', 
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'fintrak.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'fintrak.wsgi.application'


# --- DATABASE ---

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# --- PASSWORD VALIDATION ---

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


# --- INTERNATIONALIZATION ---

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True


# --- STATIC FILES (for Whitenoise/Production) ---

STATIC_URL = '/static/'

# REQUIRED for collectstatic during deploy
STATIC_ROOT = BASE_DIR / 'staticfiles'

# (optional) Your project-level static folders for development
# Only add if you have a 'static' folder in your project root
# If you used 'fintrak/static/', use that path instead.
STATICFILES_DIRS = [
    BASE_DIR / 'static'
]

# Whitenoise storage setting for optimized static file serving
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


# --- DEFAULT PRIMARY KEY ---

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
