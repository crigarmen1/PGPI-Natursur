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
    nombre = models.CharField(max_length=100)
    fecha = models.DateField()
    hora = models.TimeField()
    servicio = models.CharField(max_length=100, default="Masaje relajante")


    def __str__(self):
        return f"{self.nombre} - {self.fecha} {self.hora}"