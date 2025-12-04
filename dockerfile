FROM python:3.11-slim

# Directorio de trabajo principal. (Donde están requirements.txt, Dockerfile)
WORKDIR /app

# 1. Copiar requisitos e instalar
# (requirements.txt está aquí)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copiar todo el código fuente.
# Esto copia la carpeta 'tienda_virtual' a /app/tienda_virtual
COPY . . 

# 3. Cambiar el WORKDIR a la raíz real del proyecto Django
# Aquí es donde se encuentra manage.py
WORKDIR /app/tienda_virtual 

# 4. Configurar Django para encontrar el settings.py
# El settings.py está en /app/tienda_virtual/tienda_virtual/settings.py
# El módulo de settings es tienda_virtual.settings
ENV DJANGO_SETTINGS_MODULE="home.settings" 

# 5. Recopilar Archivos Estáticos
# Ahora se ejecuta desde /app/tienda_virtual, y manage.py está allí.
RUN python manage.py collectstatic --noinput

# 6. Ejecutar migraciones
RUN python manage.py migrate

EXPOSE 8000

# Comando de Inicio (Gunicorn)
# Ejecutamos gunicorn usando la ruta del módulo WSGI
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "tienda_virtual.wsgi:application"]