from django.db import models

# Create your models here.
class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    presidente = models.CharField(max_length=100)
    escudo = models.CharField(max_length=250)

class jugadores(models.Model):
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    posicion = models.IntegerField()

class temporada(models.Model):
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField()

class plantillas(models.Model):
    id_jugador = models.ForeignKey(jugadores, on_delete=models.CASCADE)
    id_equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    id_temporada = models.ForeignKey(temporada, on_delete=models.CASCADE)
    media = models.IntegerField()

class competiciones(models.Model):
    nombre = models.CharField(max_length=100)
    tipo_competicion = models.enums()
