from django.db import models
from geopy.geocoders import GoogleV3
from django.utils import timezone

class Cliente(models.Model):
    codigo_cliente = models.CharField(max_length=255)
    tipo_documento = models.CharField(max_length=255)
    nombre_cliente = models.CharField(max_length=255)
    genero_cliente = models.CharField(max_length=255)
    tipo_cliente = models.CharField(max_length=255)
    profesion_cliente = models.CharField(max_length=255)
    estado_civil_cliente = models.CharField(max_length=255)
    nacionalidad_cliente = models.CharField(max_length=255)
    tipo_direccion_cliente = models.CharField(max_length=255)
    tipo_vivienda_cliente = models.CharField(max_length=255)
    tipo_parroquia_residencia_trabajo_cliente = models.CharField(max_length=255)
    pais_residencia_trabajo_cliente = models.CharField(max_length=255)
    provincia_residencia_trabajo_cliente = models.CharField(max_length=255)
    canton_residencia_trabajo_cliente = models.CharField(max_length=255)
    parroquia_residencia_trabajo_cliente = models.CharField(max_length=255)
    barrio_residencia_trabajo_cliente = models.CharField(max_length=255)
    calle_principal_residencia_trabajo_cliente = models.CharField(max_length=255)
    calle_secundaria_residencia_trabajo_cliente = models.CharField(max_length=255)
    referencia_residencia_trabajo_cliente = models.TextField(null=True, blank=True)
    nivel_educacion_cliente = models.CharField(max_length=255)
    producto_principal = models.CharField(max_length=255)
    latitud_domicilio = models.CharField(null=True, blank=True)
    longitud_domicilio = models.CharField(null=True, blank=True)
    latitud_trabajo = models.CharField(null=True, blank=True)
    longitud_trabajo = models.CharField(null=True, blank=True)


    def save(self, *args, **kwargs):
        geolocator = GoogleV3(api_key='AIzaSyAWcxXZO36iZusfLvs4CZeOLplPir5DlvY')

        direccion = f"{self.calle_principal_residencia_trabajo_cliente}, {self.calle_secundaria_residencia_trabajo_cliente},  {self.canton_residencia_trabajo_cliente}"
        location = geolocator.geocode(direccion)
        if location:
            self.latitud_domicilio = location.latitude
            self.longitud_domicilio = location.longitude


        super().save(*args, **kwargs)


    def __str__(self):
        return f"Código: {self.codigo_cliente} - Nombre: {self.nombre_cliente}"
    
class Visitador(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=100)
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
class Visita(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    visitador = models.ForeignKey(Visitador, null=True, on_delete=models.CASCADE)
    fecha_hora = models.DateTimeField(default=timezone.now)
    exitosa = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.fecha_hora} - {self.cliente}"


class Cluster(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    cluster_direccion = models.PositiveIntegerField()

    def __str__(self):
        return f"Cliente: {self.cliente.codigo_cliente} - Cluster Dirección: {self.cluster_direccion}"
    

