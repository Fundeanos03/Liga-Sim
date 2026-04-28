import datetime

from django.db import models
from django.template.context_processors import request
from django.utils import timezone


# Create your models here.
class Equipo(models.Model):
    nombre = models.CharField(max_length=100)
    presidente = models.CharField(max_length=100)
    escudo = models.CharField(max_length=250)
    estadio = models.CharField(max_length=250)
    entrenador = models.CharField(max_length=250, null=True, blank=True)

class Jugador(models.Model):
    pos_choices = (
        ('POR', 'Portero'),
        ('DEF', 'Defensa'),
        ('MED', 'Mediocampo'),
        ('DEL', 'Delantero')
    )
    nombre = models.CharField(max_length=100)
    edad = models.IntegerField()
    posicion = models.CharField(max_length=100, choices=pos_choices)
    equipo_actual = models.ForeignKey(Equipo, on_delete=models.CASCADE)

class Temporada(models.Model):
    nombre = models.CharField(max_length=100)
    activa = models.BooleanField()

class MovimientoMercado(models.Model):
    tipos_choices = (
        ('FICH', 'Fichaje'),
        ('CES', 'Cesión'),
        ('RET', 'Retirado'),
    )
    equipo_origen = models.ForeignKey(Equipo, on_delete=models.CASCADE, null=True, related_name='equipo_origen')
    equipo_destino = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='equipo_destino')
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    importe = models.IntegerField()
    fecha = models.DateTimeField(default=timezone.now)
    tipo_movimiento = models.CharField(max_length=100, choices=tipos_choices)



class Partido(models.Model):
    temporada = models.ForeignKey(Temporada, on_delete=models.CASCADE)
    equipo_local = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='local')
    equipo_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='visitante')
    goles_local = models.IntegerField()
    goles_visitante = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    fecha = models.DateTimeField(default=timezone.now)


class EventoPartido(models.Model):
    tipo_evento_choices = (
        ('GOL', 'Gol'),
        ('ASI', 'Asitencia'),
        ('TAM', 'Tarjeta Amarilla'),
        ('TAR', 'Tarjeta Roja'),
        ('LES', 'Lesión'),
        ('GOP', 'Gol Propia'),
        ('PEF', 'Penalti Fallado'),
        ('PEC', 'Penalti cometido')
    )
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugador, on_delete=models.CASCADE)
    tipo_evento = models.CharField(max_length=100, choices=tipo_evento_choices)
    fecha = models.DateTimeField(default=timezone.now)


