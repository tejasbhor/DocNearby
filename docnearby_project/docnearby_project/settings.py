# docnearby_project/docnearby_project/settings.py
import os
from pathlib import Path
from datetime import timedelta
# --- Import python-dotenv ---
from dotenv import load_dotenv

# --- Load .env file ---
BASE_DIR = Path(__file__).resolve().parent.parent
# Load .env file located at the project root
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    load_dotenv(dotenv_path=env_path)
    print("Loaded environment variables from .env file.")
else:
    print("!!! WARNING: .env file not found. Environment variables may not be loaded. !!!")
# -----------------------

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'default-insecure-key-for-dev-only-@#$%^') # Load from env

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv('DJANGO_DEBUG', 'True') == 'True' # Load from env

ALLOWED_HOSTS = []
if DEBUG:
    ALLOWED_HOSTS.extend(['localhost', '127.0.0.1'])

# --- Google API Key Settings ---
# Key for Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY and DEBUG:
    print("\n" + "!"*60)
    print("!!! WARNING: GOOGLE_API_KEY (for Gemini) environment variable not set !!!")
    print("!!! Symptom analysis using Gemini will not function.             !!!")
    print("!"*60 + "\n")

# Key for Google Maps Platform APIs (Places, Geocoding, etc.)
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
if not GOOGLE_MAPS_API_KEY and DEBUG:
    print("\n" + "!"*60)
    print("!!! WARNING: GOOGLE_MAPS_API_KEY environment variable not set      !!!")
    print("!!! Google Places search for doctors will not function.          !!!")
    print("!"*60 + "\n")
# -----------------------------

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'doctors',
    'appointments',
    'symptoms',
    'feedback',
    'users',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware', # High up
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'docnearby_project.urls'

TEMPLATES = [ { 'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [], 'APP_DIRS': True, 'OPTIONS': { 'context_processors': [ 'django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages', ], }, }, ]

WSGI_APPLICATION = 'docnearby_project.wsgi.application'

# Database
DATABASES = { 'default': { 'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3', } }

# Password validation
AUTH_PASSWORD_VALIDATORS = [ { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator', }, { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', }, { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator', }, { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator', }, ]

# Internationalization
LANGUAGE_CODE = 'en-us'; TIME_ZONE = 'UTC'; USE_I18N = True; USE_TZ = True

# Static files
STATIC_URL = 'static/'
# STATIC_ROOT = BASE_DIR / 'staticfiles' # For production

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# DRF Settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ('rest_framework_simplejwt.authentication.JWTAuthentication',),
    'DEFAULT_PERMISSION_CLASSES': ('rest_framework.permissions.IsAuthenticatedOrReadOnly',)
}

# Simple JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': SECRET_KEY,
    # Add other settings if needed
}

# CORS Settings
CORS_ALLOWED_ORIGINS = [ "http://localhost:3000", "http://127.0.0.1:3000", ]
# CORS_ALLOW_ALL_ORIGINS = DEBUG # Alternative for testing

# User Model
AUTH_USER_MODEL = 'auth.User'