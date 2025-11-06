from django.contrib import admin
from .models import Articulo, Escaparate, Reservation


@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
	list_display = ("nombre", "price")
	search_fields = ("nombre",)


admin.site.register(Escaparate)
admin.site.register(Reservation)