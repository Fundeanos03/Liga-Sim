import csv
import io

from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.http import HttpResponse

from Liga_Corrupta_app.forms import EquipoForm, ArbitroForm, JugadorForm
from Liga_Corrupta_app.models import Equipo, Arbitro, Jugador


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
        jugadores = Jugador.objects.all().order_by('-media')

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
def cargar_jugadores_csv(request):
    if request.method == "POST":
        archivo = request.FILES.get('archivo_csv')
        if not archivo or not archivo.name.endswith('.csv'):
            messages.error(request, "Sube un .csv, compadre.")
            return redirect('cargar_jugadores_csv')

        try:
            data = archivo.read().decode('UTF-8')
            io_string = io.StringIO(data)
            next(io_string)  # Saltamos cabecera

            creados, errores = 0, 0
            for row in csv.reader(io_string, delimiter=','):
                try:
                    nombre_j = row[0].strip()
                    nombre_e = row[1].strip()
                    pos = row[2].strip().upper()[:3]
                    edad = int(row[3])
                    media = int(row[4]) if row[4] else None

                    equipo = Equipo.objects.filter(nombre__iexact=nombre_e).first()
                    if equipo:
                        Jugador.objects.create(nombre=nombre_j, equipo_actual=equipo, posicion=pos, edad=edad,
                                               media=media)
                        creados += 1
                    else:
                        errores += 1
                except:
                    errores += 1

            messages.success(request, f"Carga terminada. Creados: {creados}. Fallos: {errores}")
            return redirect('jugadores')
        except Exception as e:
            messages.error(request, f"Error crítico: {e}")
            return redirect('cargar_jugadores_csv')

    return render(request, "cargar_csv.html")


# 7. CARGA MASIVA DE EQUIPOS
def cargar_equipos_csv(request):
    if request.method == "POST":
        archivo = request.FILES.get('archivo_csv_equipos')  # Cambia el name en el HTML si quieres
        if archivo and archivo.name.endswith('.csv'):
            data = archivo.read().decode('UTF-8')
            io_string = io.StringIO(data)
            for row in csv.reader(io_string, delimiter=','):
                if row:
                    nombre_e = row[0].strip()
                    # Creamos el equipo si no existe
                    Equipo.objects.get_or_create(nombre=nombre_e)
            messages.success(request, "Equipos cargados.")
        else:
            messages.error(request, "Archivo no válido.")
    return redirect('administracion')