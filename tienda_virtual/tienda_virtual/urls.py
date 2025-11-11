"""
URL configuration for tienda_virtual project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path("", views.index, name="home"),
    path("catalog/", views.catalog, name="catalog"),
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("api/products/", views.products_api, name="products_api"),
    path("contact/", views.contact, name="contact"),
    path("reservations/", views.reservations, name="reservations"),
    path("admin/", admin.site.urls),
]
