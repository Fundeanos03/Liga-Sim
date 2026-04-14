from django.db import models
from django.template.context_processors import request


# Create your models here.
class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    presidente = models.CharField(max_length=100)
    escudo = models.CharField(max_length=250)
    estadio = models.CharField(max_length=250)

class jugadores(models.Model):
    pos_choices = (
        ('POR', 'Portero'),
        ('DEF', 'Defensa'),
        ('MED', 'Mediocampo'),
        ('DEL', 'Delantero')
    )
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    posicion = models.CharField(max_length=100, choices=pos_choices)

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

