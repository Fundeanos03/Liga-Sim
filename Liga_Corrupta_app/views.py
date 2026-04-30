import csv
import io

import unicodedata
from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.http import HttpResponse

from Liga_Corrupta_app.forms import EquipoForm, ArbitroForm, JugadorForm
from Liga_Corrupta_app.models import Equipo, Arbitro, Jugador, Temporada, Partido


def index(request):
    return render(request, "inicio.html")

def clasi(request):
    return render(request, "clasi.html")

def mi_club(request):
    return render(request, "mi_club.html")


def vista_administrador(request):
    return render(request, "administrador.html")


def ver_equipos(request, pk=None):
    equipo = get_object_or_404(Equipo, pk=pk) if pk else None

    if request.method == "POST":
        form = EquipoForm(request.POST, instance=equipo)
        if form.is_valid():
            form.save()
            txt = "actualizado" if equipo else "registrado"
            messages.success(request, f"Equipo {txt} con éxito.")
            return redirect('equipos')
    else:
        form = EquipoForm(instance=equipo)

    equipos = Equipo.objects.all()
    return render(request, "equipos.html", {
        'form': form,
        'equipos': equipos,
        'editando': equipo
    })


def eliminar_equipos(request, id):
    Equipo.objects.get(id=id).delete()
    return redirect('equipos')


def gestionar_arbitros(request, pk=None):
    # 1. Detectar si estamos editando o creando
    if pk:
        instancia = get_object_or_404(Arbitro, pk=pk)
    else:
        instancia = None

    # 2. Lógica de guardado (POST)
    if request.method == "POST":
        form = ArbitroForm(request.POST, instance=instancia)
        if form.is_valid():
            form.save()
            messages.success(request, "Nómina actualizada correctamente.")
            return redirect('arbitros')
    else:
        form = ArbitroForm(instance=instancia)

    # 3. LA CLAVE: Ordenar por ID en lugar de nombre
    # Si quieres que el ÚLTIMO en entrar salga el PRIMERO, usa '-id'
    arbitros = Arbitro.objects.all().order_by('id')

    return render(request, "arbitros.html", {
        'form': form,
        'arbitros': arbitros,
        'editando': pk is not None
    })


# 1. VER PLANTILLAS (LISTADO Y FILTRO)
def gestionar_jugadores(request):
    equipo_id = request.GET.get('equipo')
    equipos = Equipo.objects.all().order_by('nombre')

    if equipo_id:
        jugadores = Jugador.objects.filter(equipo_actual_id=equipo_id)
    else:
        # Los ordenamos por media para ver a los mejores arriba
        jugadores = Jugador.objects.all().order_by('-equipo_actual')

    return render(request, "jugadores.html", {
        'jugadores': jugadores,
        'equipos': equipos,
        'equipo_seleccionado': equipo_id
    })


# 2. INSERCIÓN UNITARIA (NUEVO JUGADOR EN OTRA PÁGINA)
def nuevo_jugador(request):
    if request.method == "POST":
        form = JugadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Fichaje realizado correctamente!")
            return redirect('jugadores')
    else:
        form = JugadorForm()

    return render(request, 'nuevo_jugador.html', {'form': form})


# 3. EDITAR JUGADOR
def editar_jugador(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk)
    if request.method == "POST":
        form = JugadorForm(request.POST, instance=jugador)
        if form.is_valid():
            form.save()
            messages.success(request, f"Datos de {jugador.nombre} actualizados.")
            return redirect('jugadores')
    else:
        form = JugadorForm(instance=jugador)
    return render(request, 'editar_jugador.html', {'form': form, 'jugador': jugador})


# 4. ELIMINAR JUGADOR (UNITARIO)
def eliminar_jugador(request, pk):
    jugador = get_object_or_404(Jugador, pk=pk)
    nombre = jugador.nombre
    jugador.delete()
    messages.success(request, f"{nombre} ha sido despedido.")
    return redirect('jugadores')


# 5. BORRADO MASIVO (BOTÓN DE PÁNICO)
def borrar_todos_jugadores(request):
    if request.method == "POST":
        total = Jugador.objects.count()
        Jugador.objects.all().delete()
        messages.warning(request, f"Se han eliminado los {total} jugadores del sistema.")
    return redirect('jugadores')


# 6. CARGA MASIVA DE JUGADORES (TU FUNCIÓN MEJORADA)
def eliminar_tildes(cadena):
    """Transforma 'MÁLAGA' en 'MALAGA' para comparaciones seguras"""
    return "".join(c for c in unicodedata.normalize('NFD', cadena) if unicodedata.category(c) != 'Mn')


def cargar_jugadores_csv(request):
    if request.method == "POST":
        archivo = request.FILES.get('archivo_csv')

        if not archivo or not archivo.name.endswith('.csv'):
            messages.error(request, "El archivo debe ser un formato .csv")
            return redirect('cargar_jugadores_csv')

        try:
            # Leemos el archivo
            contenido = archivo.read()
            try:
                data = contenido.decode('utf-8-sig')
            except UnicodeDecodeError:
                data = contenido.decode('latin-1')

            io_string = io.StringIO(data)
            next(io_string)  # Saltar cabecera

            creados = 0
            errores = 0

            # Traemos todos los equipos de la DB una sola vez para ahorrar tiempo
            equipos_en_db = list(Equipo.objects.all())

            for row in csv.reader(io_string, delimiter=','):
                if not row or len(row) < 5:
                    continue

                try:
                    nombre_jugador = row[0].strip()
                    nombre_equipo_csv = row[1].strip()
                    pos = row[2].strip().upper()[:3]
                    edad = int(row[3])
                    media = int(row[4]) if row[4] else None

                    # --- LÓGICA DE BÚSQUEDA ROBUSTA ---
                    equipo = None
                    nombre_csv_comparar = eliminar_tildes(nombre_equipo_csv).lower()

                    for e in equipos_en_db:
                        if eliminar_tildes(e.nombre).lower() == nombre_csv_comparar:
                            equipo = e
                            break

                    if equipo:
                        Jugador.objects.create(
                            nombre=nombre_jugador,
                            equipo_actual=equipo,
                            posicion=pos,
                            edad=edad,
                            media=media
                        )
                        creados += 1
                    else:
                        print(f"❌ ERROR: No se encontró el equipo '{nombre_equipo_csv}'")
                        errores += 1

                except Exception as e:
                    print(f"Error en fila {row}: {e}")
                    errores += 1

            messages.success(request, f"✅ Carga terminada: {creados} creados. ❌ Fallos: {errores}")
            return redirect('jugadores')

        except Exception as e:
            messages.error(request, f"Error crítico al leer el archivo: {e}")
            return redirect('cargar_jugadores_csv')

    return render(request, "cargar_csv.html")


def tabla_clasificacion(request, temporada_id):
    temporada = get_object_or_404(Temporada, id=temporada_id)
    equipos = Equipo.objects.all()
    tabla = []

    for equipo in equipos:
        partidos = Partido.objects.filter(
            Q(equipo_local=equipo) | Q(equipo_visitante=equipo),
            temporada=temporada
        )

        # Si aún no tienes modelo de tarjetas, los dejamos a 0
        # Pero la lógica ya está lista para cuando los tengas
        amarillas = 0
        rojas = 0

        stats = {
            'equipo': equipo,
            'nombre': equipo.nombre.lower(),
            'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0,
            'gf': 0, 'gc': 0, 'puntos': 0,
            'dg': 0,
            'amarillas': amarillas,
            'rojas': rojas
        }

        for p in partidos:
            stats['pj'] += 1
            if p.equipo_local == equipo:
                stats['gf'] += p.goles_local
                stats['gc'] += p.goles_visitante
                if p.goles_local > p.goles_visitante:
                    stats['pg'] += 1
                    stats['puntos'] += 3
                elif p.goles_local == p.goles_visitante:
                    stats['pe'] += 1
                    stats['puntos'] += 1
                else:
                    stats['pp'] += 1
            else:
                stats['gf'] += p.goles_visitante
                stats['gc'] += p.goles_local
                if p.goles_visitante > p.goles_local:
                    stats['pg'] += 1
                    stats['puntos'] += 3
                elif p.goles_visitante == p.goles_local:
                    stats['pe'] += 1
                    stats['puntos'] += 1
                else:
                    stats['pp'] += 1

        stats['dg'] = stats['gf'] - stats['gc']
        tabla.append(stats)

    # ORDEN: Puntos, DG, GF, Amarillas, Rojas, Nombre
    tabla = sorted(tabla, key=lambda x: (
        -x['puntos'],
        -x['dg'],
        -x['gf'],
        x['amarillas'],
        x['rojas'],
        x['nombre']
    ))

    return render(request, 'clasi.html', {'tabla': tabla, 'temporada': temporada})