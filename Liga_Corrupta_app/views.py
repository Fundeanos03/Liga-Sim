import csv
import io

import unicodedata
from django.contrib import messages
from django.db.models import Q
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.http import HttpResponse
from django.utils import timezone

from Liga_Corrupta_app.forms import EquipoForm, ArbitroForm, JugadorForm
from Liga_Corrupta_app.models import Equipo, Arbitro, Jugador, Temporada, Partido, EventoPartido


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


def tabla_clasificacion(request, temporada_id=None):
    # Lógica para buscar la temporada activa
    if temporada_id:
        temporada = get_object_or_404(Temporada, id=temporada_id)
    else:
        temporada = Temporada.objects.filter(activa=True).first() or Temporada.objects.last()

    if not temporada:
        return render(request, 'clasi.html', {'tabla': [], 'error': "No hay temporadas"})

    equipos = Equipo.objects.all()
    tabla = []

    for equipo in equipos:
        # ... (aquí va tu lógica de calcular PJ, PG, PE, PP, Puntos) ...
        stats = {
            'equipo': equipo,
            'pj': 0, 'pg': 0, 'pe': 0, 'pp': 0,
            'gf': 0, 'gc': 0, 'puntos': 0, 'dg': 0
        }
        tabla.append(stats)

    # Enviamos 'tabla' al template 'clasi.html'
    return render(request, 'clasi.html', {'tabla': tabla, 'temporada': temporada})


# --- VISTAS DE TEMPORADAS ---

def lista_temporadas(request):
    temporadas = Temporada.objects.all().order_by('-id')
    return render(request, 'temporadas/lista.html', {'temporadas': temporadas})

def nueva_temporada(request):
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        activa = request.POST.get('activa') == 'on'

        if activa:
            # Si marcamos esta como activa, las demás dejan de serlo
            Temporada.objects.all().update(activa=False)

        Temporada.objects.create(nombre=nombre, activa=activa)
        messages.success(request, "¡Temporada inaugurada con éxito!")
        return redirect('lista_temporadas')

    return render(request, 'temporadas/nueva.html')

def activar_temporada(request, temporada_id):
    Temporada.objects.all().update(activa=False)
    temp = get_object_or_404(Temporada, id=temporada_id)
    temp.activa = True
    temp.save()
    messages.success(request, f"Ahora la temporada activa es: {temp.nombre}")
    return redirect('lista_temporadas')

# --- VISTA ADMINISTRADOR ACTUALIZADA ---
# Sustituye tu 'def vista_administrador' por esta para que detecte la temporada
def vista_administrador(request):
    temporada_activa = Temporada.objects.filter(activa=True).first()
    return render(request, "administrador.html", {'temporada_activa': temporada_activa})


def lista_partidos(request):
    temp_activa = Temporada.objects.filter(activa=True).first()

    if temp_activa:
        # Ordenamos por jornada para que la 1 salga antes que la 2
        partidos = Partido.objects.filter(temporada=temp_activa).order_by('jornada')
    else:
        partidos = []

    return render(request, 'partidos/lista.html', {
        'partidos': partidos,
        'temporada': temp_activa
    })


def nuevo_partido(request):
    equipos = Equipo.objects.all().order_by('nombre')
    temp_activa = Temporada.objects.filter(activa=True).first()

    if request.method == "POST":
        local_id = request.POST.get('local')
        visitante_id = request.POST.get('visitante')
        g_l = request.POST.get('goles_l')
        g_v = request.POST.get('goles_v')
        num_jornada = request.POST.get('jornada')

        nuevo_p = Partido.objects.create(
            temporada=temp_activa,
            equipo_local_id=local_id,
            equipo_visitante_id=visitante_id,
            goles_local=g_l,
            goles_visitante=g_v,
            jornada=num_jornada  # LO GUARDAMOS
        )

        return redirect('editar_partido_eventos', partido_id=nuevo_p.id)

    return render(request, 'partidos/nuevo.html', {
        'equipos': equipos,
        'temporada': temp_activa
    })


def editar_partido_eventos(request, partido_id):
    partido = get_object_or_404(Partido, id=partido_id)

    # Creamos una fábrica de formularios: Partido + sus Eventos
    # 'extra=1' significa que siempre habrá una fila vacía al final para añadir uno nuevo
    EventoFormSet = inlineformset_factory(
        Partido, EventoPartido,
        fields=('jugador', 'tipo_evento'),
        extra=1,
        can_delete=True
    )

    if request.method == "POST":
        # Cargamos los datos del marcador del partido
        partido.goles_local = request.POST.get('goles_local')
        partido.goles_visitante = request.POST.get('goles_visitante')
        partido.save()

        # Cargamos y validamos los eventos (goles, tarjetas, etc.)
        formset = EventoFormSet(request.POST, instance=partido)
        if formset.is_valid():
            formset.save()
            messages.success(request, "Acta de partido actualizada.")
            return redirect('lista_partidos')
    else:
        formset = EventoFormSet(instance=partido)

    return render(request, 'partidos/editar_eventos.html', {
        'partido': partido,
        'formset': formset
    })