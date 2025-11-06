from django.db import models

class Articulo(models.Model):
    nombre = models.CharField(max_length=30)
    descripcion = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)

    def __str__(self):
        return self.nombre
    
class Escaparate(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.articulo.id)


class Reservation(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    time = models.TimeField()
    service = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.date} {self.time} ({self.service})"