# tienda_virtual/settings.py

import os
from pathlib import Path

# Definición de la ruta base
# Asume que el settings.py está en tienda_virtual/tienda_virtual/settings.py
BASE_DIR = Path(__file__).resolve().parent

# --- Configuración Básica de Producción ---
# ⚠️ CAMBIA ESTO: Usa una clave secreta fuerte en producción
SECRET_KEY = 'tu-clave-secreta-de-produccion' 

# Django en Docker debe ser False para eficiencia y seguridad
DEBUG = False 

ALLOWED_HOSTS = ['*'] # Permite todas las IPs dentro del contenedor

# --- Aplicaciones Instaladas Mínimas ---
INSTALLED_APPS = [
    # Mínimas
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Tu App
    'home', # Nombre de la aplicación que contiene los estáticos
]

# --- Middlewares (Añadiendo WhiteNoise) ---
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    
    # 🌟 VITAL: Añadir WhiteNoise inmediatamente después de SecurityMiddleware
    'whitenoise.middleware.WhiteNoiseMiddleware', 
    
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# --- CONFIGURACIÓN VITAL DE TEMPLATES ---
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [], # Puedes dejar esto vacío si no usas templates globales de proyecto
        'APP_DIRS': True, # Busca templates dentro de las carpetas de las apps (como home/templates)
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

# --- CONFIGURACIÓN VITAL DE BASE DE DATOS ---
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        # VITAL: Usa BASE_DIR para colocar el archivo SQLite en la raíz del proyecto
        'NAME': BASE_DIR / 'db.sqlite3', 
    }
}

ROOT_URLCONF = 'tienda_virtual.urls' # Ajusta si tu archivo urls.py está en otro lugar

# --- Configuración de Archivos Estáticos (Estándar para Producción) ---
STATIC_URL = '/static/'
# Directorio donde collectstatic copiará *todos* los estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles_root') 

# 🌟 VITAL: Configuración de WhiteNoise para compresión y caché
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Si tienes estáticos de proyecto fuera de la carpeta 'static' de una app, añádelos aquí.
# Por tu estructura, asumo que tus estáticos están bien ubicados en 'home/static/home'.
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, 'static'), 
# ]