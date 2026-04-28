from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

# Create your views here.

from django.http import HttpResponse

from Liga_Corrupta_app.forms import EquipoForm
from Liga_Corrupta_app.models import Equipo


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
