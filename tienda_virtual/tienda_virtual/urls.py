"""
URL configuration for tienda_virtual project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
    path("reservar/", views.reservar, name="reservar"),
    path("reservas/crear/", views.crear_reserva, name="crear_reserva"),
    path("reservas/available_slots/", views.available_slots, name="available_slots"),
    path("admin/", admin.site.urls),
]
