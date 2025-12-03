"""
Django settings for tienda_virtual project.
"""

from pathlib import Path
import os
# --- INICIO MODIFICACIONES DE RENDER/PRODUCCIÓN ---
import dj_database_url # Necesario para PostgreSQL
from whitenoise.storage import CompressedManifestStaticFilesStorage # Necesario para archivos estáticos
# --- FIN MODIFICACIONES DE RENDER/PRODUCCIÓN ---

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
# 💡 MODIFICACIÓN: Leer SECRET_KEY de las variables de entorno de Render
SECRET_KEY = os.environ.get(
    "SECRET_KEY", 
    "django-insecure-^sex271=z$ma^w_&qa93m-*6(oxz5ki^d^)e413h1lwe$y94f$" # Clave de fallback local
)

# SECURITY WARNING: don't run with debug turned on in production!
# 💡 MODIFICACIÓN: DEBUG es True si la variable RENDER no está definida o es diferente a 'True'
DEBUG = (os.environ.get("RENDER") != "True")

# 💡 MODIFICACIÓN: Permitir acceso desde el host de Render
ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost").split(',')


# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "home"
]

# Optional Herbalife integration: sale code and base URL
HERBALIFE_SALE_CODE = os.environ.get("HERBALIFE_SALE_CODE", "YOUR_SALE_CODE")
HERBALIFE_BASE_URL = os.environ.get("HERBALIFE_BASE_URL", "https://www.herbalife.com/product")

# Company contact info used in templates
COMPANY_ADDRESS = os.environ.get("COMPANY_ADDRESS", "Calle Falsa 123, Ciudad, País")
COMPANY_OWNER = os.environ.get("COMPANY_OWNER", "Nombre del Propietario")
COMPANY_EMAIL = os.environ.get("COMPANY_EMAIL", "owner@example.com")

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # 💡 MODIFICACIÓN: Añadir WhiteNoise justo después de SecurityMiddleware
    "whitenoise.middleware.WhiteNoiseMiddleware", 
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "tienda_virtual.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# 🚨 CORRECCIÓN CLAVE: Debe reflejar la estructura anidada del proyecto (tienda_virtual/tienda_virtual)
WSGI_APPLICATION = "tienda_virtual.tienda_virtual.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

# 💡 MODIFICACIÓN: Configuración dinámica para PostgreSQL en producción (DATABASE_URL de Render)
DATABASES = {
    "default": dj_database_url.config(
        default="sqlite:///db.sqlite3", # Fallback para desarrollo local
        conn_max_age=600 # Para mantener la conexión viva
    )
}


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "static/"

# 💡 MODIFICACIÓN: Configuración de producción para WhiteNoise (archivos estáticos)
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Instagram feed configuration (use environment variables in production)
# Set INSTAGRAM_ACCESS_TOKEN to a valid Instagram Basic Display access token.
INSTAGRAM_ACCESS_TOKEN = os.environ.get("INSTAGRAM_ACCESS_TOKEN")
# How long to cache Instagram feed (seconds)
INSTAGRAM_FEED_TTL = int(os.environ.get("INSTAGRAM_FEED_TTL", "300"))